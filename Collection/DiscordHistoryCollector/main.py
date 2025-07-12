import discord
import asyncio
import sqlite3
import aiohttp
import os
import urllib.parse
from pathlib import Path
import threading
import queue
from datetime import datetime
from minio import Minio
from minio.error import S3Error
import io
from dotenv import load_dotenv
import label_studio_sdk

# Load environment variables from .env file
load_dotenv()

# Environment variables for configuration
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', '0'))  # Replace with your channel ID

# Global queue for downloads
download_queue = queue.Queue()

# Number of download worker threads
NUM_DOWNLOAD_THREADS = int(os.getenv('NUM_DOWNLOAD_THREADS', '10'))

# MinIO configuration
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'admin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minio_admin')
MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'garage')
MINIO_SECURE = os.getenv('MINIO_SECURE', 'false').lower() == 'true'  # Set to True if using HTTPS

# Label Studio configuration (optional)
LABEL_STUDIO_ENABLED = os.getenv('LABEL_STUDIO_ENABLED', 'false').lower() == 'true'
LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL', 'http://localhost:8080')
LABEL_STUDIO_API_KEY = os.getenv('LABEL_STUDIO_API_KEY', '')
LABEL_STUDIO_PROJECT_ID = int(os.getenv('LABEL_STUDIO_PROJECT_ID', '0'))

# Validate required environment variables
if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is required")
if CHANNEL_ID == 0:
    raise ValueError("DISCORD_CHANNEL_ID environment variable is required")

# Initialize MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

# Initialize Label Studio client (if enabled)
label_studio_client = None
if LABEL_STUDIO_ENABLED and LABEL_STUDIO_API_KEY:
    try:
        label_studio_client = label_studio_sdk.Client(url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_KEY)
        print(f"[{datetime.now()}] INFO: Label Studio client initialized")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR: Failed to initialize Label Studio client: {e}")
        label_studio_client = None
elif LABEL_STUDIO_ENABLED and not LABEL_STUDIO_API_KEY:
    print(f"[{datetime.now()}] WARNING: Label Studio is enabled but API key is not provided")

# Ensure MinIO bucket exists
try:
    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)
        print(f"[{datetime.now()}] INFO: Created MinIO bucket '{MINIO_BUCKET}'")
    else:
        print(f"[{datetime.now()}] INFO: MinIO bucket '{MINIO_BUCKET}' already exists")
except Exception as e:
    print(f"[{datetime.now()}] ERROR: Failed to connect to MinIO: {e}")

intents = discord.Intents.default()
intents.message_content = True  # ✅ Needed to read messages

client = discord.Client(intents=discord.Intents.all())

# Create SQLite DB connection
conn = sqlite3.connect("messages.db")
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id TEXT UNIQUE,
        gate_status TEXT,
        gate_status_confidence INTEGER,
        garage_occupancy TEXT,
        timestamp TEXT
    )
''')
conn.commit()

def download_worker(worker_id):
    """Worker thread that processes download queue"""
    session = None
    try:
        # Create aiohttp session for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def create_session():
            return aiohttp.ClientSession()
        
        session = loop.run_until_complete(create_session())
        
        print(f"[{datetime.now()}] Download worker {worker_id} started")
        
        while True:
            try:
                # Get download task from queue
                task = download_queue.get(timeout=10)
                if task is None:  # Shutdown signal
                    break
                
                message_id, url = task
                
                # Download the file
                loop.run_until_complete(download_single_file(session, url, message_id, worker_id))
                
                download_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[{datetime.now()}] ERROR: Worker {worker_id} error: {e}")
                download_queue.task_done()
                
    except Exception as e:
        print(f"[{datetime.now()}] FATAL ERROR: Worker {worker_id} fatal error: {e}")
    finally:
        if session:
            loop.run_until_complete(session.close())
        loop.close()
        print(f"[{datetime.now()}] Download worker {worker_id} stopped")

def run_label_studio_sync():
    """Run the Label Studio sync after downloads are complete"""
    if not LABEL_STUDIO_ENABLED or not label_studio_client:
        print(f"[{datetime.now()}] INFO: Label Studio not available, skipping sync")
        return
    
    try:
        print(f"[{datetime.now()}] INFO: Running Label Studio sync...")
        
        # Get the project
        project = label_studio_client.get_project(LABEL_STUDIO_PROJECT_ID)
        
        # Get import storages and sync each one
        import_storages = project.get_import_storages()
        
        print(f"[{datetime.now()}] INFO: Found {len(import_storages)} import storages")
        
        for storage in import_storages:
            storage_id = storage['id']
            storage_type = storage['type']
            storage_title = storage.get('title', f'Storage {storage_id}')
            
            print(f"[{datetime.now()}] INFO: Syncing storage: {storage_title} (ID: {storage_id}, Type: {storage_type})")
            
            try:
                sync_result = project.sync_import_storage(storage_type, storage_id)
                print(f"[{datetime.now()}] INFO: Successfully synced storage {storage_title}")
            except Exception as e:
                print(f"[{datetime.now()}] ERROR: Failed to sync storage {storage_title}: {e}")
        
        print(f"[{datetime.now()}] INFO: Label Studio sync process completed")
        
    except Exception as e:
        print(f"[{datetime.now()}] ERROR: Failed to run Label Studio sync: {e}")



async def download_single_file(session, url, message_id, worker_id):
    """Download a single file and upload to MinIO"""
    try:
        # Extract file extension from URL
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        original_filename = os.path.basename(path)
        
        # Get file extension from original filename
        _, ext = os.path.splitext(original_filename)
        
        # Always use message_id as filename, preserve original extension
        if ext:
            filename = f"{message_id}{ext}"
        else:
            # Default to .jpg if no extension found
            filename = f"{message_id}.jpg"
        
        # Download the file directly to memory
        async with session.get(url) as response:
            if response.status == 200:
                # Read the entire file into memory
                file_data = await response.read()
                
                # Create a BytesIO object for MinIO upload
                file_stream = io.BytesIO(file_data)
                file_stream.seek(0)
                
                # Upload to MinIO
                try:
                    minio_client.put_object(
                        MINIO_BUCKET, 
                        filename, 
                        file_stream,
                        length=len(file_data),
                        content_type="image/jpeg" if ext.lower() in ['.jpg', '.jpeg'] else "image/png" if ext.lower() == '.png' else "image/gif" if ext.lower() == '.gif' else "application/octet-stream"
                    )
                    print(f"[{datetime.now()}] Worker {worker_id}: Downloaded and uploaded to MinIO: {filename}")
                        
                except S3Error as e:
                    print(f"[{datetime.now()}] ERROR: Worker {worker_id}: Failed to upload {filename} to MinIO: {e}")
                except Exception as e:
                    print(f"[{datetime.now()}] ERROR: Worker {worker_id}: Failed to upload {filename} to MinIO: {e}")
            else:
                print(f"[{datetime.now()}] ERROR: Worker {worker_id}: Failed to download {url}: HTTP {response.status}")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR: Worker {worker_id}: Error downloading {url}: {e}")

@client.event
async def on_ready():
    print(f'[{datetime.now()}] Logged in as {client.user}')
    channel = client.get_channel(CHANNEL_ID)

    # Start multiple download worker threads
    download_threads = []
    for i in range(NUM_DOWNLOAD_THREADS):
        thread = threading.Thread(target=download_worker, args=(i+1,), daemon=True)
        thread.start()
        download_threads.append(thread)
    
    print(f"[{datetime.now()}] Started {NUM_DOWNLOAD_THREADS} download worker threads")

    # Get last saved message ID if any
    c.execute("SELECT message_id FROM messages ORDER BY message_id DESC LIMIT 1")
    row = c.fetchone()
    after_message = None
    if row:
        last_message_id = int(row[0])
        print(f"[{datetime.now()}] Resuming after message ID: {last_message_id}")
        after_message = discord.Object(id=last_message_id)

    counter = 0
    
    async for message in channel.history(after=after_message, oldest_first=True, limit=None):
        print(f"[{datetime.now()}] Processing message {message.id} from {message.created_at}")

        gate_status = None
        confidence = 0.0

        # Find the embed fields
        for embed in message.embeds:
            for f in embed.fields:
                fname = f.name.lower().strip()
                fvalue = f.value.strip()

                if fname == "status":
                    gate_status = fvalue

                elif fname == "confidence":
                    try:
                        confidence = int(fvalue.strip('%'))
                    except ValueError:
                        confidence = 0.0

        # Always store first attachment URL from embeds
        attachment_url = None
        for embed in message.embeds:
            if embed.thumbnail and embed.thumbnail.url:
                attachment_url = embed.thumbnail.url
                break

        if not attachment_url:
            print(f"[{datetime.now()}] No attachment found for message {message.id}")
            continue  # Skip if no attachment URL

        # Add download task to queue
        download_queue.put((message.id, attachment_url))

        # Store message in database
        try:
            c.execute('''
                       INSERT INTO messages (message_id, gate_status, gate_status_confidence, timestamp)
                       VALUES (?, ?, ?, ?)
                   ''', (
                str(message.id),
                gate_status,
                confidence,
                str(message.created_at)
            ))
            counter += 1
        except sqlite3.IntegrityError:
            print(f"[{datetime.now()}] WARNING: Message {message.id} already exists in database")
            continue

        if counter % 100 == 0:
            conn.commit()
            print(f"[{datetime.now()}] INFO: Processed {counter} messages, queue size: {download_queue.qsize()}")

    # Wait for remaining downloads to complete
    print(f"[{datetime.now()}] Waiting for remaining downloads to complete...")
    download_queue.join()
    
    # Signal worker threads to shutdown
    for _ in range(NUM_DOWNLOAD_THREADS):
        download_queue.put(None)
    
    # Wait for all threads to finish
    for thread in download_threads:
        thread.join(timeout=5)

    conn.commit()
    print(f"[{datetime.now()}] INFO: Fetched and saved {counter} new messages.")

    # Run Label Studio sync after all downloads are complete
    run_label_studio_sync()

    await client.close()

client.run(TOKEN)