import sqlite3
from datetime import datetime
from typing import Optional

class DatabaseManager:
    def __init__(self, db_path: str = "messages.db") -> None:
        self.db_path: str = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database connection and create tables"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Create table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE,
                gate_status TEXT,
                gate_status_confidence INTEGER,
                garage_occupancy TEXT,
                timestamp TEXT
            )
        ''')
        self.conn.commit()
    
    def get_last_message_id(self) -> Optional[int]:
        """Get the last saved message ID"""
        if self.cursor is None:
            return None
        self.cursor.execute("SELECT message_id FROM messages ORDER BY message_id DESC LIMIT 1")
        row = self.cursor.fetchone()
        return int(row[0]) if row else None
    
    def save_message(self, message_id: int, gate_status: Optional[str] = None, 
                    confidence: Optional[int] = None, timestamp: Optional[datetime] = None) -> bool:
        """Save a message to the database"""
        if self.cursor is None:
            return False
        try:
            self.cursor.execute('''
                INSERT INTO messages (message_id, gate_status, gate_status_confidence, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (
                str(message_id),
                gate_status,
                confidence,
                str(timestamp) if timestamp else None
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"[{datetime.now()}] WARNING: Message {message_id} already exists in database")
            return False
    
    def commit(self) -> None:
        """Commit pending changes"""
        if self.conn:
            self.conn.commit()
    
    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close() 