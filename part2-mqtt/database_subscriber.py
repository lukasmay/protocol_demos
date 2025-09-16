#!/usr/bin/env python3
"""
QoS=1 Database Subscriber - Demonstrates reliable message reception
This shows guaranteed message delivery with automatic acknowledgment to broker
"""
import paho.mqtt.client as mqtt
import json
import sqlite3
import os
from datetime import datetime

# Configuration - Environment variables for Docker deployment
BROKER = os.getenv("BROKER", "localhost")  # MQTT broker hostname
PORT = int(os.getenv("PORT", "1883"))      # MQTT broker port
TOPIC = "sensor/data"                      # Topic to subscribe to
DB_FILE = os.getenv("DB_FILE", "sensor_data.db")  # SQLite database file

def setup_database():
    """Create database table if it doesn't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create table for sensor data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            temperature REAL,
            pressure REAL,
            unit_id TEXT,
            received_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database ready: {DB_FILE}")

def on_connect(client, userdata, flags, rc):
    """Callback when MQTT client connects to broker"""
    if rc == 0:
        print(f"Connected to MQTT broker at {BROKER}:{PORT}")
        # Subscribe to the sensor data topic with QoS=1
        result = client.subscribe(TOPIC, qos=1)
        print(f"Subscribed to topic: {TOPIC} with QoS=1 (guaranteed delivery)")
    else:
        print(f"Failed to connect to broker. Error code: {rc}")

def on_subscribe(client, userdata, mid, granted_qos):
    """Callback when subscription is successful"""
    print(f"Subscription confirmed (MsgID: {mid}, Granted QoS: {granted_qos})")

def on_message(client, userdata, msg):
    """Callback when a message is received from MQTT"""
    try:
        # Show message details with QoS=1 info
        print(f"   Received QoS=1 message on topic: {msg.topic}")
        print(f"   Message ID: {msg.mid}, QoS: {msg.qos}")
        print(f"   Client will automatically send acknowledgment to broker")
        
        # Decode the JSON message
        payload = msg.payload.decode('utf-8')
        print(f"   Raw payload: {payload}")
        
        data = json.loads(payload)
        
        # Extract sensor values
        timestamp = data.get('timestamp', 0)
        temperature = data.get('temperature', 0)
        pressure = data.get('pressure', 0)
        unit_id = data.get('unit_id', 'unknown')
        received_at = datetime.now().isoformat()
        
        # Store in database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_readings 
            (timestamp, temperature, pressure, unit_id, received_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, temperature, pressure, unit_id, received_at))
        
        conn.commit()
        conn.close()
        
        # Print what we received and stored
        print(f"Stored: Temp={temperature}°C, Pressure={pressure} bar from {unit_id}")
        print(f"Received at: {received_at}")
        print(f"Message processed - acknowledgment sent to broker automatically")
        print("─" * 60)
        
    except Exception as e:
        print(f"Error processing message: {e}")
        print(f"❌ Raw payload was: {msg.payload}")
        # Note: Even if processing fails, MQTT client will still acknowledge the message

def main():
    """Main function - sets up database and MQTT subscriber"""
    # Initialize database
    setup_database()
    
    # Create MQTT client with unique ID
    client_id = "Database_Subscriber_QoS1"
    client = mqtt.Client(client_id=client_id)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    
    try:
        # Connect to broker
        print(f"Connecting to MQTT broker at {BROKER}:{PORT} with Client ID: {client_id}")
        client.connect(BROKER, PORT, 60)
        
        # Start listening for messages (blocking call)
        print("Listening for sensor data...")
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\nShutting down database subscriber...")
        client.disconnect()

if __name__ == "__main__":
    main()
