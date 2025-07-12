# Discord History Collector

A Discord bot that collects message history from a specific channel and downloads attachments to MinIO storage.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   
   Copy `env.example` to `.env` and fill in your values:
   ```bash
   cp env.example .env
   ```

   Required environment variables:
   - `DISCORD_TOKEN`: Your Discord bot token
   - `DISCORD_CHANNEL_ID`: The channel ID to collect messages from

   Optional environment variables:
   - `NUM_DOWNLOAD_THREADS`: Number of download worker threads (default: 10)
   - `MINIO_ENDPOINT`: MinIO server endpoint (default: localhost:9000)
   - `MINIO_ACCESS_KEY`: MinIO access key (default: admin)
   - `MINIO_SECRET_KEY`: MinIO secret key (default: minio_admin)
   - `MINIO_BUCKET`: MinIO bucket name (default: garage)
   - `MINIO_SECURE`: Use HTTPS for MinIO (default: false)
   - `LABEL_STUDIO_ENABLED`: Enable Label Studio integration (default: false)
   - `LABEL_STUDIO_URL`: Label Studio server URL (default: http://localhost:8080)
   - `LABEL_STUDIO_API_KEY`: Label Studio API key
   - `LABEL_STUDIO_PROJECT_ID`: Label Studio project ID

3. **Run the collector:**
   ```bash
   python main.py
   ```

## Features

- Collects message history from a Discord channel
- Downloads attachments and uploads them to MinIO storage
- Stores message metadata in SQLite database
- Multi-threaded download processing
- Environment variable configuration for security
- Optional Label Studio integration for data labeling
- Automatic Label Studio sync after downloads complete

## Database Schema

The SQLite database (`messages.db`) contains:
- `message_id`: Discord message ID
- `gate_status`: Status field from message embeds
- `gate_status_confidence`: Confidence percentage
- `garage_occupancy`: Occupancy status
- `timestamp`: Message creation timestamp

## Security Notes

- Never commit your `.env` file to version control
- Keep your Discord bot token secure
- Use strong MinIO credentials in production
- Keep your Label Studio API key secure if using Label Studio integration

## Label Studio Integration

If you enable Label Studio integration, the script will:

1. Automatically add downloaded images to your Label Studio project
2. Include message metadata (gate status, confidence) as task data
3. Use MinIO URLs for image storage in Label Studio
4. Automatically run Label Studio sync after downloads complete

To enable Label Studio integration:
1. Set `LABEL_STUDIO_ENABLED=true`
2. Provide your Label Studio API key
3. Set the correct project ID
4. Ensure Label Studio is running and accessible

## License
MIT 