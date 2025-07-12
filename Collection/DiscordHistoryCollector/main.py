import discord
from datetime import datetime
from typing import Optional
from discord import Object

# Import our modules
from config import (
    DISCORD_TOKEN, DISCORD_CHANNEL_ID, NUM_DOWNLOAD_THREADS,
    validate_config
)
from database import DatabaseManager
from download_worker import DownloadManager
from label_studio_client import LabelStudioManager

def main() -> None:
    """Main function to run the Discord History Collector"""
    # Validate configuration
    validate_config()
    
    # Initialize components
    db_manager: DatabaseManager = DatabaseManager()
    download_manager: DownloadManager = DownloadManager()
    label_studio_manager: LabelStudioManager = LabelStudioManager()
    
    # Set up Discord client
    intents: discord.Intents = discord.Intents.default()
    intents.message_content = True
    client: discord.Client = discord.Client(intents=discord.Intents.all())
    
    @client.event
    async def on_ready() -> None:
        print(f'[{datetime.now()}] Logged in as {client.user}')
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        
        if channel is None:
            print(f"[{datetime.now()}] ERROR: Could not find channel {DISCORD_CHANNEL_ID}")
            await client.close()
            return
        
        # Start download workers
        download_manager.start_workers()
        
        # Get last saved message ID if any
        last_message_id: Optional[int] = db_manager.get_last_message_id()
        after_message: Optional[Object] = None
        if last_message_id:
            print(f"[{datetime.now()}] Resuming after message ID: {last_message_id}")
            after_message = Object(id=last_message_id)
        
        counter: int = 0
        
        async for message in channel.history(after=after_message, oldest_first=True, limit=None):
            print(f"[{datetime.now()}] Processing message {message.id} from {message.created_at}")
            
            gate_status: Optional[str] = None
            confidence: int = 0
            
            # Find the embed fields
            for embed in message.embeds:
                for f in embed.fields:
                    if f.name and f.value:
                        fname: str = f.name.lower().strip()
                        fvalue: str = f.value.strip()
                        
                        if fname == "status":
                            gate_status = fvalue
                        elif fname == "confidence":
                            try:
                                confidence = int(fvalue.strip('%'))
                            except ValueError:
                                confidence = 0
            
            # Always store first attachment URL from embeds
            attachment_url: Optional[str] = None
            for embed in message.embeds:
                if embed.thumbnail and embed.thumbnail.url:
                    attachment_url = embed.thumbnail.url
                    break
            
            if not attachment_url:
                print(f"[{datetime.now()}] No attachment found for message {message.id}")
                continue  # Skip if no attachment URL
            
            # Add download task to queue
            download_manager.add_download_task(message.id, attachment_url)
            
            # Store message in database
            if db_manager.save_message(message.id, gate_status, confidence, message.created_at):
                counter += 1
            
            if counter % 100 == 0:
                db_manager.commit()
                print(f"[{datetime.now()}] INFO: Processed {counter} messages")
        
        # Wait for remaining downloads to complete
        download_manager.wait_for_completion()
        
        # Shutdown workers
        download_manager.shutdown_workers()
        
        # Final commit
        db_manager.commit()
        print(f"[{datetime.now()}] INFO: Fetched and saved {counter} new messages.")
        
        # Run Label Studio sync
        label_studio_manager.sync_storages()
        
        await client.close()
    
    # Run the client
    if DISCORD_TOKEN:
        client.run(DISCORD_TOKEN)
    else:
        print("[ERROR] DISCORD_TOKEN is None")

if __name__ == "__main__":
    main()