#!/usr/bin/env python3
"""
QoS=2 Database Subscriber - Demonstrates exactly-once message reception
This shows the four-step handshake for guaranteed exactly-once delivery
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
        # Subscribe to the sensor data topic with QoS=2
        result = client.subscribe(TOPIC, qos=2)
        print(f"Subscribed to topic: {TOPIC} with QoS=2 (exactly once delivery)")
    else:
        print(f"Failed to connect to broker. Error code: {rc}")

def on_subscribe(client, userdata, mid, granted_qos):
    """Callback when subscription is successful"""
    print(f"Subscription confirmed (MsgID: {mid}, Granted QoS: {granted_qos})")
    print(f"   Ready to receive QoS=2 messages with four-step handshake")

def on_message(client, userdata, msg):
    """Callback when a message is received from MQTT"""
    try:
        # Show message details with QoS=2 info
        print(f"   Received QoS=2 message on topic: {msg.topic}")
        print(f"   Message ID: {msg.mid}, QoS: {msg.qos}")
        print(f"   Four-step handshake in progress: PUBLISH → PUBREC → PUBREL → PUBCOMP")
        
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
        print(f"QoS=2 handshake completing - message delivered exactly once")
        print("─" * 70)
        
    except Exception as e:
        print(f"Error processing message: {e}")
        print(f"Raw payload was: {msg.payload}")
        # Note: QoS=2 ensures message is delivered exactly once even if processing fails

def main():
    """Main function - sets up database and MQTT subscriber"""
    # Initialize database
    setup_database()
    
    # Create MQTT client with unique ID
    client_id = "Database_Subscriber_QoS2"
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
