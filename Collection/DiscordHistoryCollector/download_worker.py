import asyncio
import aiohttp
import os
import urllib.parse
import queue
import threading
from datetime import datetime
from typing import Optional, Tuple
from minio_client import MinioManager
from config import NUM_DOWNLOAD_THREADS

class DownloadWorker:
    def __init__(self, worker_id: int, download_queue: queue.Queue, minio_manager: MinioManager) -> None:
        self.worker_id: int = worker_id
        self.download_queue: queue.Queue = download_queue
        self.minio_manager: MinioManager = minio_manager
        self.session: Optional[aiohttp.ClientSession] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
    
    def start(self) -> threading.Thread:
        """Start the download worker thread"""
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        return thread
    
    def _run(self) -> None:
        """Main worker loop"""
        try:
            # Create asyncio loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Create aiohttp session
            self.session = self.loop.run_until_complete(self._create_session())
            
            print(f"[{datetime.now()}] Download worker {self.worker_id} started")
            
            while True:
                try:
                    # Get download task from queue
                    task: Optional[Tuple[int, str]] = self.download_queue.get(timeout=10)
                    if task is None:  # Shutdown signal
                        break
                    
                    message_id, url = task
                    
                    # Download the file
                    if self.loop:
                        self.loop.run_until_complete(self._download_single_file(url, message_id))
                    
                    self.download_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"[{datetime.now()}] ERROR: Worker {self.worker_id} error: {e}")
                    self.download_queue.task_done()
                    
        except Exception as e:
            print(f"[{datetime.now()}] FATAL ERROR: Worker {self.worker_id} fatal error: {e}")
        finally:
            if self.session and self.loop:
                self.loop.run_until_complete(self.session.close())
            if self.loop:
                self.loop.close()
            print(f"[{datetime.now()}] Download worker {self.worker_id} stopped")
    
    async def _create_session(self) -> aiohttp.ClientSession:
        """Create aiohttp session"""
        return aiohttp.ClientSession()
    
    async def _download_single_file(self, url: str, message_id: int) -> None:
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
            if self.session:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        # Read the entire file into memory
                        file_data: bytes = await response.read()
                        
                        # Upload to MinIO
                        if self.minio_manager.upload_file(file_data, filename):
                            print(f"[{datetime.now()}] Worker {self.worker_id}: Downloaded and uploaded to MinIO: {filename}")
                        else:
                            print(f"[{datetime.now()}] ERROR: Worker {self.worker_id}: Failed to upload {filename} to MinIO")
                    else:
                        print(f"[{datetime.now()}] ERROR: Worker {self.worker_id}: Failed to download {url}: HTTP {response.status}")
        except Exception as e:
            print(f"[{datetime.now()}] ERROR: Worker {self.worker_id}: Error downloading {url}: {e}")

class DownloadManager:
    def __init__(self) -> None:
        self.num_workers: int = NUM_DOWNLOAD_THREADS
        self.download_queue: queue.Queue = queue.Queue()
        self.minio_manager: MinioManager = MinioManager()
        self.workers: list[threading.Thread] = []
    
    def start_workers(self) -> None:
        """Start all download worker threads"""
        for i in range(self.num_workers):
            worker = DownloadWorker(i + 1, self.download_queue, self.minio_manager)
            thread = worker.start()
            self.workers.append(thread)
        
        print(f"[{datetime.now()}] Started {self.num_workers} download worker threads")
    
    def add_download_task(self, message_id: int, url: str) -> None:
        """Add a download task to the queue"""
        self.download_queue.put((message_id, url))
    
    def wait_for_completion(self) -> None:
        """Wait for all downloads to complete"""
        print(f"[{datetime.now()}] Waiting for remaining downloads to complete...")
        self.download_queue.join()
    
    def shutdown_workers(self) -> None:
        """Signal worker threads to shutdown"""
        for _ in range(self.num_workers):
            self.download_queue.put(None)
        
        # Wait for all threads to finish
        for thread in self.workers:
            thread.join(timeout=5) 