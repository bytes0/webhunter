from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import json
import os
from datetime import datetime
import sqlite3
from pathlib import Path

router = APIRouter()

# Database setup
DB_PATH = Path("telegram_config.db")

def init_db():
    """Initialize the Telegram configuration database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create config table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telegram_config (
            id INTEGER PRIMARY KEY,
            bot_token TEXT,
            chat_id TEXT,
            is_connected BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telegram_notifications (
            id INTEGER PRIMARY KEY,
            scan_started BOOLEAN DEFAULT TRUE,
            scan_completed BOOLEAN DEFAULT TRUE,
            scan_failed BOOLEAN DEFAULT TRUE,
            vulnerabilities_found BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create notification history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_history (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            target TEXT,
            sent BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default notification settings if not exists
    cursor.execute('SELECT COUNT(*) FROM telegram_notifications')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO telegram_notifications 
            (scan_started, scan_completed, scan_failed, vulnerabilities_found)
            VALUES (TRUE, TRUE, TRUE, TRUE)
        ''')
    
    conn.commit()
    conn.close()

# Initialize database on module import
init_db()

class TelegramConfig(BaseModel):
    bot_token: str
    chat_id: Optional[str] = None

class NotificationSettings(BaseModel):
    scan_started: bool = True
    scan_completed: bool = True
    scan_failed: bool = True
    vulnerabilities_found: bool = True

class TestResponse(BaseModel):
    message: str
    success: bool

async def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """Send a message via Telegram bot"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, timeout=10.0)
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False

async def send_telegram_document(bot_token: str, chat_id: str, file_path: str, caption: str = "") -> bool:
    """Send a document via Telegram bot"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        files = {'document': (os.path.basename(file_path), open(file_path, 'rb'))}
        data = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": "HTML"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, files=files, timeout=30.0)
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Error sending Telegram document: {e}")
        return False
    finally:
        if 'files' in locals() and files['document'][1]:
            files['document'][1].close()

def get_config() -> Dict[str, Any]:
    """Get current Telegram configuration"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT bot_token, chat_id, is_connected FROM telegram_config ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    
    config = {
        "bot_token": "",
        "chat_id": "",
        "is_connected": False
    }
    
    if result:
        config["bot_token"] = result[0] or ""
        config["chat_id"] = result[1] or ""
        config["is_connected"] = bool(result[2])
    
    conn.close()
    return config

def save_config(bot_token: str, chat_id: Optional[str] = None):
    """Save Telegram configuration"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO telegram_config (bot_token, chat_id, is_connected, updated_at)
        VALUES (?, ?, FALSE, CURRENT_TIMESTAMP)
    ''', (bot_token, chat_id))
    
    conn.commit()
    conn.close()

def get_notification_settings() -> Dict[str, bool]:
    """Get current notification settings"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT scan_started, scan_completed, scan_failed, vulnerabilities_found FROM telegram_notifications ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    
    settings = {
        "scan_started": True,
        "scan_completed": True,
        "scan_failed": True,
        "vulnerabilities_found": True
    }
    
    if result:
        settings["scan_started"] = bool(result[0])
        settings["scan_completed"] = bool(result[1])
        settings["scan_failed"] = bool(result[2])
        settings["vulnerabilities_found"] = bool(result[3])
    
    conn.close()
    return settings

def save_notification_settings(settings: NotificationSettings):
    """Save notification settings"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO telegram_notifications 
        (scan_started, scan_completed, scan_failed, vulnerabilities_found, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (
        settings.scan_started,
        settings.scan_completed,
        settings.scan_failed,
        settings.vulnerabilities_found
    ))
    
    conn.commit()
    conn.close()

def save_notification_history(notification_type: str, message: str, target: Optional[str] = None):
    """Save notification to history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO notification_history (type, message, target, created_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ''', (notification_type, message, target))
    
    conn.commit()
    conn.close()

def get_notification_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Get notification history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, type, message, target, sent, created_at 
        FROM notification_history 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    results = cursor.fetchall()
    notifications = []
    
    for row in results:
        notifications.append({
            "id": row[0],
            "type": row[1],
            "message": row[2],
            "target": row[3],
            "sent": bool(row[4]),
            "timestamp": row[5]
        })
    
    conn.close()
    return notifications

@router.get("/config")
async def get_telegram_config():
    """Get current Telegram configuration"""
    config = get_config()
    settings = get_notification_settings()
    
    return {
        **config,
        "notifications": settings
    }

@router.post("/config")
async def save_telegram_config(config: TelegramConfig):
    """Save Telegram bot configuration"""
    try:
        save_config(config.bot_token, config.chat_id)
        return {"message": "Configuration saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving configuration: {str(e)}")

@router.post("/test")
async def test_telegram_connection():
    """Test Telegram bot connection"""
    config = get_config()
    
    if not config["bot_token"]:
        raise HTTPException(status_code=400, detail="Bot token not configured")
    
    if not config["chat_id"]:
        raise HTTPException(status_code=400, detail="Chat ID not configured")
    
    test_message = f"🧪 <b>Test Message</b>\n\nThis is a test message from your Bug Bounty Platform bot!\n\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    success = await send_telegram_message(config["bot_token"], config["chat_id"], test_message)
    
    if success:
        # Update connection status
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE telegram_config SET is_connected = TRUE WHERE bot_token = ?', (config["bot_token"],))
        conn.commit()
        conn.close()
        
        return TestResponse(
            message="Test message sent successfully! Check your Telegram chat.",
            success=True
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to send test message")

@router.post("/notifications")
async def save_notification_settings_endpoint(settings: NotificationSettings):
    """Save notification settings"""
    try:
        save_notification_settings(settings)
        return {"message": "Notification settings saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving notification settings: {str(e)}")

@router.get("/notifications")
async def get_notification_history_endpoint():
    """Get notification history"""
    try:
        notifications = get_notification_history()
        return {"notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading notifications: {str(e)}")

@router.post("/send")
async def send_notification(notification_type: str, message: str, target: Optional[str] = None):
    """Send a notification via Telegram"""
    config = get_config()
    settings = get_notification_settings()
    
    # Check if notifications are enabled for this type
    if notification_type == "scan_started" and not settings["scan_started"]:
        return {"message": "Scan started notifications are disabled"}
    elif notification_type == "scan_completed" and not settings["scan_completed"]:
        return {"message": "Scan completed notifications are disabled"}
    elif notification_type == "scan_failed" and not settings["scan_failed"]:
        return {"message": "Scan failed notifications are disabled"}
    elif notification_type == "vulnerability_found" and not settings["vulnerabilities_found"]:
        return {"message": "Vulnerability notifications are disabled"}
    
    if not config["bot_token"] or not config["chat_id"]:
        return {"message": "Telegram not configured"}
    
    # Format message based on type
    emoji_map = {
        "scan_started": "🚀",
        "scan_completed": "✅",
        "scan_failed": "❌",
        "vulnerability_found": "⚠️"
    }
    
    emoji = emoji_map.get(notification_type, "📢")
    formatted_message = f"{emoji} <b>{notification_type.replace('_', ' ').title()}</b>\n\n{message}"
    
    if target:
        formatted_message += f"\n\n🎯 Target: {target}"
    
    formatted_message += f"\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Save to history
    save_notification_history(notification_type, message, target)
    
    # Send via Telegram
    success = await send_telegram_message(config["bot_token"], config["chat_id"], formatted_message)
    
    if success:
        return {"message": "Notification sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send notification")

async def send_scan_notification(
    scan_type: str, 
    notification_type: str, 
    message: str, 
    target: Optional[str] = None,
    file_path: Optional[str] = None
):
    """
    Checks notification settings and sends a scan notification if enabled.
    Saves notification to history.
    Can also send a file along with the message.
    """
    config = get_config()
    settings = get_notification_settings()

    if not config["is_connected"] or not config["bot_token"] or not config["chat_id"]:
        print("Telegram not connected or configured. Skipping notification.")
        return

    notification_key = f"{notification_type}"
    # A simple mapping for now. Can be expanded.
    # e.g. vulnerabilities_found -> vulnerabilities_found
    # scan_completed -> scan_completed
    if notification_key not in settings:
        # Fallback for simple keys like 'scan_completed'
        if notification_type in settings:
            notification_key = notification_type
        else:
            print(f"Unknown notification type: {notification_type}. Skipping.")
            return

    if settings.get(notification_key):
        # Save to history before sending
        save_notification_history(f"{scan_type}:{notification_type}", message, target)

        # Send the main message
        await send_telegram_message(config["bot_token"], config["chat_id"], message)
        
        # If a file path is provided, send it as a document
        if file_path and os.path.exists(file_path):
            if target:
                file_caption = f"Full results for {scan_type} scan on {target}"
            else:
                file_caption = f"Full results for {scan_type} scan"
                
            await send_telegram_document(
                config["bot_token"], 
                config["chat_id"], 
                file_path,
                caption=file_caption
            )
    else:
        print(f"Notification type '{notification_type}' is disabled. Skipping.") 