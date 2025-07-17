from label_studio_sdk import Client
from label_studio_sdk.data_manager import Filters, Operator, Type, Column
from datetime import datetime
from shared import config

class LabelStudioManager:
    def __init__(self):
        self.client = Client(url=config.label_studio_url, api_key=config.label_studio_api_key)
        self.project = self.client.get_project(config.label_studio_project_id)

    def fetch_annotated_tasks(self):
        """Generator: Yield annotated tasks from Label Studio in pages of 100 using filters and pagination."""
        filters = Filters.create(
            Filters.AND,
            [
                Filters.item(
                    Column.completed_at,
                    Operator.NOT_EQUAL,
                    Type.Datetime,
                    Filters.value(datetime.now())
                ),
            ],
        )

        page = 1
        page_size = 100
        while True:
            tasks_page = self.project.get_paginated_tasks(
                filters=filters,
                page=page,
                page_size=page_size
            )

            tasks = tasks_page.get('tasks', [])
            if not tasks:
                break
            for task in tasks:
                yield task
            if tasks_page.get('end_pagination', False):
                break
            page += 1

    def get_label_config_info(self):
        """Extract label info and mappings from the Label Studio project object."""
        label_config = self.project.parsed_label_config

        gate_labels = label_config['gate_status']['labels']
        parking_labels = label_config['parking_status']['labels']
        
        gate_label_map = {label: idx for idx, label in enumerate(gate_labels)}
        parking_label_map = {label: idx for idx, label in enumerate(parking_labels)}
        
        return gate_label_map, parking_label_map 