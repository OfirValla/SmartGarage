# Smart Garage Collection System

This repository contains a comprehensive data collection system for monitoring a smart garage. The system consists of two main components that work together to collect and process garage status data from multiple sources.

## 📁 Project Structure

```
Collection/
├── DiscordHistoryCollector/    # Historical Discord message collector
│   ├── main.py                # Main Discord bot application
│   ├── config.py              # Configuration management
│   ├── database.py            # SQLite database operations
│   ├── download_worker.py     # Multi-threaded download manager
│   ├── label_studio_client.py # Label Studio integration
│   ├── minio_client.py        # MinIO storage client
│   └── requirements.txt       # Python dependencies
│
└── LiveCollector/             # Real-time camera stream collector
    ├── main.py                # Main camera application
    ├── camera_handler.py      # RTSP camera connection handler
    ├── image_consumer.py      # Image processing consumer
    ├── config.py              # Configuration management
    ├── utils.py               # Utility functions
    └── requirements.txt       # Python dependencies
```

## 🎯 System Overview

The Smart Garage Collection System is designed to monitor and collect data from a smart garage setup that includes:

1. **Discord Bot Integration**: A Discord bot that posts garage status updates with images
2. **Live Camera Stream**: Real-time RTSP camera feed monitoring the garage
3. **Data Storage**: MinIO object storage for images and SQLite for metadata
4. **Data Labeling**: Optional Label Studio integration for image annotation

## 🚀 Components

### DiscordHistoryCollector

A Discord bot that collects historical message data from a specific channel. It processes messages containing garage status information and downloads associated images.

**Key Features:**
- Collects message history from Discord channels
- Downloads attachments and uploads to MinIO storage
- Stores message metadata in SQLite database
- Multi-threaded download processing
- Optional Label Studio integration for data labeling
- Environment-based configuration for security

**Use Case:** Historical data collection from Discord bot messages containing garage status updates with embedded images.

### LiveCollector

A real-time camera stream processor that connects to an RTSP camera feed and continuously captures images.

**Key Features:**
- Connects to RTSP camera streams
- Saves images and grayscale versions
- Threaded image processing for efficiency
- Configurable output directory
- Environment-based configuration

**Use Case:** Real-time monitoring of garage status through live camera feed.

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.12+
- Discord Bot Token
- RTSP Camera URL
- MinIO Server (optional, for storing dataset)
- Label Studio Server (optional, for data labeling)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Collection
   ```

2. **Install dependencies for both projects:**
   ```bash
   # DiscordHistoryCollector
   cd DiscordHistoryCollector
   pip install -r requirements.txt
   
   # LiveCollector
   cd ../LiveCollector
   pip install -r requirements.txt
   ```

### Configuration

#### DiscordHistoryCollector Setup

1. **Create environment file:**
   ```bash
   cd DiscordHistoryCollector
   cp env.example .env
   ```

2. **Configure required variables:**
   ```env
   DISCORD_TOKEN=your_discord_bot_token
   DISCORD_CHANNEL_ID=your_channel_id
   ```

3. **Optional MinIO configuration:**
   ```env
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=admin
   MINIO_SECRET_KEY=minio_admin
   MINIO_BUCKET=garage
   ```

#### LiveCollector Setup

1. **Create environment file:**
   ```bash
   cd LiveCollector
   cp env.example .env
   ```

2. **Configure camera URL:**
   ```env
   CAMERA_URL=rtsp://your_camera_ip:port/stream
   OUTPUT_DIR=./output
   ```

## 🚀 Usage

### Running DiscordHistoryCollector

```bash
cd DiscordHistoryCollector
python main.py
```

The bot will:
- Connect to Discord using your bot token
- Collect message history from the specified channel
- Download attachments and upload to MinIO
- Store metadata in SQLite database
- Optionally sync with Label Studio

### Running LiveCollector

```bash
cd LiveCollector
python main.py
```

The application will:
- Connect to the RTSP camera stream
- Continuously capture and save images
- Process images in threaded consumers
- Save both color and grayscale versions

## 📊 Data Flow

```
Discord Bot → DiscordHistoryCollector → MinIO Storage
                                    ↓
                                SQLite DB
                                    ↓
                              Label Studio (optional)

RTSP Camera → LiveCollector → Local Storage
```

## 🔧 Database Schema

The DiscordHistoryCollector creates a SQLite database (`messages.db`) with the following schema:

- `message_id`: Discord message ID
- `gate_status`: Status field from message embeds
- `gate_status_confidence`: Confidence percentage
- `garage_occupancy`: Occupancy status
- `timestamp`: Message creation timestamp

## 🔐 Security Notes

- Never commit `.env` files to version control
- Keep Discord bot tokens secure
- Use strong MinIO credentials in production
- Secure your Label Studio API key if using integration
- Ensure RTSP camera streams are properly secured

## 🤝 Integration

### Label Studio Integration

If enabled, the DiscordHistoryCollector will:
1. Automatically add downloaded images to Label Studio projects
2. Include message metadata as task data
3. Use MinIO URLs for image storage
4. Sync after downloads complete

### MinIO Storage

Images are stored in MinIO buckets with organized structure:
- Original Discord attachments
- Processed images from live camera feed
- Metadata stored separately in SQLite

## 📝 License

MIT License - see individual project README files for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues or questions:
- Check individual project README files for specific details
- Review configuration examples in each project
- Ensure all environment variables are properly set 