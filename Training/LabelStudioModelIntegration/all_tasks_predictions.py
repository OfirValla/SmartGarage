import threading
from queue import Queue
from label_studio_sdk import Client
from garage_model import GarageModel
import config

# Init LS client
ls = Client(url=config.LABEL_STUDIO_URL, api_key=config.LABEL_STUDIO_API_KEY)
project = ls.get_project(config.LABEL_STUDIO_PROJECT_ID)

task_queue = Queue(maxsize=1000)

NUM_PRODUCERS = 3
NUM_CONSUMERS = 12

def producer(producer_id):
    page = producer_id + 1  # stagger start page
    page_size = 50
    stride = NUM_PRODUCERS
    total_tasks = 0

    while True:
        batch = project.get_paginated_tasks(page=page, page_size=page_size)
        tasks = list(batch.get('tasks'))

        if not tasks:
            break

        for task in tasks:
            task_queue.put(task)

        total_tasks += len(tasks)
        print(f"[Producer-{producer_id}] Fetched page {page} ({len(tasks)} tasks)")

        page += stride

    print(f"[Producer-{producer_id}] Done. Total tasks queued: {total_tasks}")

def consumer(worker_id):
    model = GarageModel()

    while True:
        task = task_queue.get()
        if task is None:
            print(f"[Consumer-{worker_id}] Exiting.")
            break

        task_id = task.get('id')
        print(f"[Consumer-{worker_id}] Processing task {task_id}")

        results = model.predict([task])
        prediction = results[0]

        project.create_prediction(
            task_id=task_id,
            result=prediction['result'],
            score=prediction.get('score'),
            model_version=prediction.get('model_version'),
        )

        gate_label = None
        parking_label = None

        for item in prediction['result']:
            if item['from_name'] == 'gate_status':
                gate_label = item['value']['choices'][0]
            if item['from_name'] == 'parking_status':
                parking_label = item['value']['choices'][0]

        try:
            project.update_task(
                task_id,
                data={
                    **task.get('data'),
                    "prediction_gate_label": gate_label,
                    "prediction_parking_label": parking_label
                }
            )
            print(f"[Consumer-{worker_id}] Updated task {task_id} gate={gate_label} parking={parking_label}")
        except Exception as e:
            print(f"[Consumer-{worker_id}] Failed to patch task {task_id}: {e}")

        task_queue.task_done()

# Start producers
producer_threads = []
for i in range(NUM_PRODUCERS):
    t = threading.Thread(target=producer, args=(i,))
    t.start()
    producer_threads.append(t)

# Start consumers
consumer_threads = []
for i in range(NUM_CONSUMERS):
    t = threading.Thread(target=consumer, args=(i,))
    t.start()
    consumer_threads.append(t)

# Wait for producers to finish
for t in producer_threads:
    t.join()

# All producers done → send poison pills for each consumer
for _ in range(NUM_CONSUMERS):
    task_queue.put(None)

# Wait for consumers to finish
for t in consumer_threads:
    t.join()

print("✅ All tasks processed and updated!")
