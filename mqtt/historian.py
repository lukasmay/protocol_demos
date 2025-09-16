#!/usr/bin/env python3
"""
Historian Database - Industrial Data Historian
Subscribes to topics 1, 2, 3 and stores all data with timestamps
"""
import paho.mqtt.client as mqtt
import json
import time
import sqlite3
import threading
import os
from datetime import datetime, timedelta

# Configuration
BROKER = os.getenv("BROKER", "localhost")
PORT = int(os.getenv("PORT", "1883"))
CLIENT_ID = "Historian"
SUBSCRIBE_TOPICS = ["factory/line1", "factory/energy", "factory/environment"]
DB_FILE = os.getenv("DB_FILE", "historian.db")

class HistorianDB:
    def __init__(self):
        self.client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Database connection
        self.db_connection = None
        self.message_count = 0
        self.connected = False
        
        # Initialize database
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database with tables for each data type"""
        try:
            self.db_connection = sqlite3.connect(DB_FILE, check_same_thread=False)
            cursor = self.db_connection.cursor()
            
            # Manufacturing Line Data Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS manufacturing_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    plc_id TEXT NOT NULL,
                    production_count INTEGER,
                    line_speed REAL,
                    temperature REAL,
                    pressure REAL,
                    vibration REAL,
                    quality_rate REAL,
                    alarm BOOLEAN,
                    status TEXT,
                    raw_data TEXT
                )
            ''')
            
            # Energy Data Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS energy_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    plc_id TEXT NOT NULL,
                    power_consumption REAL,
                    voltage_l1 REAL,
                    voltage_l2 REAL,
                    voltage_l3 REAL,
                    current_l1 REAL,
                    current_l2 REAL,
                    current_l3 REAL,
                    power_factor REAL,
                    frequency REAL,
                    energy_total REAL,
                    demand_peak REAL,
                    grid_status TEXT,
                    efficiency REAL,
                    raw_data TEXT
                )
            ''')
            
            # Environmental Data Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS environmental_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    plc_id TEXT NOT NULL,
                    temperature REAL,
                    humidity REAL,
                    air_pressure REAL,
                    co2_level REAL,
                    air_quality_index REAL,
                    air_quality_status TEXT,
                    noise_level REAL,
                    light_level REAL,
                    pm2_5 REAL,
                    pm10 REAL,
                    wind_speed REAL,
                    wind_direction REAL,
                    uv_index REAL,
                    comfort_index REAL,
                    raw_data TEXT
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_manufacturing_timestamp ON manufacturing_data(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_energy_timestamp ON energy_data(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_environmental_timestamp ON environmental_data(timestamp)')
            
            self.db_connection.commit()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Database initialized: {DB_FILE}")
            
        except sqlite3.Error as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Database error: {e}")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connected to broker")
            
            # Subscribe to all topics
            for topic in SUBSCRIBE_TOPICS:
                client.subscribe(topic, qos=1)
                print(f"[{CLIENT_ID}] Subscribed to: {topic}")
            
            client.publish(f"status/{CLIENT_ID}", "online", retain=True)
            self.connected = True
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connection failed: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Disconnected")
        self.connected = False
    
    def on_message(self, client, userdata, msg):
        try:
            self.message_count += 1
            topic = msg.topic
            payload = msg.payload.decode()
            data = json.loads(payload)
            
            # Store data based on topic
            if topic == "factory/line1":
                self.store_manufacturing_data(data, payload)
            elif topic == "factory/energy":
                self.store_energy_data(data, payload)
            elif topic == "factory/environment":
                self.store_environmental_data(data, payload)
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Stored data from {topic} (Total: {self.message_count})")
            
        except json.JSONDecodeError as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] JSON decode error: {e}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error processing message: {e}")
    
    def store_manufacturing_data(self, data, raw_data):
        """Store manufacturing line data"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO manufacturing_data 
                (timestamp, plc_id, production_count, line_speed, temperature, pressure, 
                 vibration, quality_rate, alarm, status, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('timestamp'),
                data.get('plc_id'),
                data.get('production_count'),
                data.get('line_speed'),
                data.get('temperature'),
                data.get('pressure'),
                data.get('vibration'),
                data.get('quality_rate'),
                data.get('alarm'),
                data.get('status'),
                raw_data
            ))
            self.db_connection.commit()
            
        except sqlite3.Error as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error storing manufacturing data: {e}")
    
    def store_energy_data(self, data, raw_data):
        """Store energy management data"""
        try:
            cursor = self.db_connection.cursor()
            voltages = data.get('voltages', {})
            currents = data.get('currents', {})
            
            cursor.execute('''
                INSERT INTO energy_data 
                (timestamp, plc_id, power_consumption, voltage_l1, voltage_l2, voltage_l3,
                 current_l1, current_l2, current_l3, power_factor, frequency, energy_total,
                 demand_peak, grid_status, efficiency, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('timestamp'),
                data.get('plc_id'),
                data.get('power_consumption'),
                voltages.get('L1'),
                voltages.get('L2'),
                voltages.get('L3'),
                currents.get('L1'),
                currents.get('L2'),
                currents.get('L3'),
                data.get('power_factor'),
                data.get('frequency'),
                data.get('energy_total'),
                data.get('demand_peak'),
                data.get('grid_status'),
                data.get('efficiency'),
                raw_data
            ))
            self.db_connection.commit()
            
        except sqlite3.Error as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error storing energy data: {e}")
    
    def store_environmental_data(self, data, raw_data):
        """Store environmental monitoring data"""
        try:
            cursor = self.db_connection.cursor()
            air_quality = data.get('air_quality', {})
            particulates = data.get('particulates', {})
            wind = data.get('wind', {})
            
            cursor.execute('''
                INSERT INTO environmental_data 
                (timestamp, plc_id, temperature, humidity, air_pressure, co2_level,
                 air_quality_index, air_quality_status, noise_level, light_level,
                 pm2_5, pm10, wind_speed, wind_direction, uv_index, comfort_index, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('timestamp'),
                data.get('plc_id'),
                data.get('temperature'),
                data.get('humidity'),
                data.get('air_pressure'),
                data.get('co2_level'),
                air_quality.get('index'),
                air_quality.get('status'),
                data.get('noise_level'),
                data.get('light_level'),
                particulates.get('pm2_5'),
                particulates.get('pm10'),
                wind.get('speed'),
                wind.get('direction'),
                data.get('uv_index'),
                data.get('comfort_index'),
                raw_data
            ))
            self.db_connection.commit()
            
        except sqlite3.Error as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error storing environmental data: {e}")
    
    def print_statistics(self):
        """Print database statistics periodically"""
        while True:
            try:
                time.sleep(30)  # Print every 30 seconds
                
                cursor = self.db_connection.cursor()
                
                # Count records in each table
                cursor.execute('SELECT COUNT(*) FROM manufacturing_data')
                mfg_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM energy_data')
                energy_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM environmental_data')
                env_count = cursor.fetchone()[0]
                
                # Get latest timestamps
                cursor.execute('SELECT MAX(timestamp) FROM manufacturing_data')
                latest_mfg = cursor.fetchone()[0]
                
                cursor.execute('SELECT MAX(timestamp) FROM energy_data')
                latest_energy = cursor.fetchone()[0]
                
                cursor.execute('SELECT MAX(timestamp) FROM environmental_data')
                latest_env = cursor.fetchone()[0]
                
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] DATABASE STATISTICS:")
                print(f"  Manufacturing Records: {mfg_count:,} (Latest: {latest_mfg or 'None'})")
                print(f"  Energy Records:        {energy_count:,} (Latest: {latest_energy or 'None'})")
                print(f"  Environmental Records: {env_count:,} (Latest: {latest_env or 'None'})")
                print(f"  Total Messages:        {self.message_count:,}")
                print(f"  Database Size:         {os.path.getsize(DB_FILE) / 1024:.1f} KB")
                
                # Cleanup old data (keep last 7 days)
                cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
                cursor.execute('DELETE FROM manufacturing_data WHERE timestamp < ?', (cutoff_date,))
                cursor.execute('DELETE FROM energy_data WHERE timestamp < ?', (cutoff_date,))
                cursor.execute('DELETE FROM environmental_data WHERE timestamp < ?', (cutoff_date,))
                self.db_connection.commit()
                
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Statistics error: {e}")
    
    def start(self):
        """Start the historian service"""
        try:
            # Set will message for clean disconnect detection
            self.client.will_set(f"status/{CLIENT_ID}", "offline", retain=True)
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connecting to {BROKER}:{PORT}")
            self.client.connect(BROKER, PORT, 60)
            
            # Start MQTT loop in background
            self.client.loop_start()
            
            # Start statistics thread
            stats_thread = threading.Thread(target=self.print_statistics, daemon=True)
            stats_thread.start()
            
            # Keep main thread alive
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Shutting down...")
            self.client.publish(f"status/{CLIENT_ID}", "offline", retain=True)
            self.client.disconnect()
            self.client.loop_stop()
            if self.db_connection:
                self.db_connection.close()

if __name__ == "__main__":
    historian = HistorianDB()
    historian.start()
