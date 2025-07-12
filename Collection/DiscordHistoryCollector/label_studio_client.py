import label_studio_sdk
from datetime import datetime
from typing import Optional, Any, Dict, List
from config import LABEL_STUDIO_ENABLED, LABEL_STUDIO_URL, LABEL_STUDIO_API_KEY, LABEL_STUDIO_PROJECT_ID

class LabelStudioManager:
    def __init__(self) -> None:
        self.client: Optional[label_studio_sdk.Client] = None
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize Label Studio client"""
        if LABEL_STUDIO_ENABLED and LABEL_STUDIO_API_KEY:
            try:
                self.client = label_studio_sdk.Client(url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_KEY)
                print(f"[{datetime.now()}] INFO: Label Studio client initialized")
            except Exception as e:
                print(f"[{datetime.now()}] ERROR: Failed to initialize Label Studio client: {e}")
                self.client = None
        elif LABEL_STUDIO_ENABLED and not LABEL_STUDIO_API_KEY:
            print(f"[{datetime.now()}] WARNING: Label Studio is enabled but API key is not provided")
    
    def is_available(self) -> bool:
        """Check if Label Studio is available"""
        return LABEL_STUDIO_ENABLED and self.client is not None
    
    def sync_storages(self) -> None:
        """Sync all import storages"""
        if not self.is_available():
            print(f"[{datetime.now()}] INFO: Label Studio not available, skipping sync")
            return
        
        try:
            print(f"[{datetime.now()}] INFO: Running Label Studio sync...")
            
            # Get the project
            if self.client is None:
                print(f"[{datetime.now()}] ERROR: Label Studio client is None")
                return
                
            project = self.client.get_project(LABEL_STUDIO_PROJECT_ID)
            
            # Get import storages and sync each one
            import_storages: List[Dict[str, Any]] = project.get_import_storages()
            
            print(f"[{datetime.now()}] INFO: Found {len(import_storages)} import storages")
            
            for storage in import_storages:
                storage_id: int = storage['id']
                storage_type: str = storage['type']
                storage_title: str = storage.get('title', f'Storage {storage_id}')
                
                print(f"[{datetime.now()}] INFO: Syncing storage: {storage_title} (ID: {storage_id}, Type: {storage_type})")
                
                try:
                    sync_result = project.sync_import_storage(storage_type, storage_id)
                    print(f"[{datetime.now()}] INFO: Successfully synced storage {storage_title}")
                except Exception as e:
                    print(f"[{datetime.now()}] ERROR: Failed to sync storage {storage_title}: {e}")
            
            print(f"[{datetime.now()}] INFO: Label Studio sync process completed")
            
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Failed to run Label Studio sync: {e}") 