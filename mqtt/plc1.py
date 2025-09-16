#!/usr/bin/env python3
"""
PLC1 Simulator - Manufacturing Line Controller
Publishes production data to topic1
"""
import paho.mqtt.client as mqtt
import json
import time
import random
import threading
import os
from datetime import datetime

# Configuration
BROKER = os.getenv("BROKER", "localhost")
PORT = int(os.getenv("PORT", "1883"))
CLIENT_ID = "PLC1"
TOPIC = "factory/line1"
PUBLISH_INTERVAL = 2  # seconds

class PLC1Simulator:
    def __init__(self):
        self.client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.running = False
        
        # Manufacturing line state
        self.production_count = 0
        self.line_speed = 100  # items per minute
        self.temperature = 25.0  # °C
        self.pressure = 1.2  # bar
        self.vibration = 0.5  # mm/s
        self.quality_rate = 98.5  # %
        self.alarm_state = False
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connected to broker")
            # Publish online status
            client.publish(f"status/{CLIENT_ID}", "online", retain=True)
            self.running = True
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connection failed: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Disconnected")
        self.running = False
    
    def simulate_data(self):
        """Simulate realistic manufacturing data"""
        # Production count increases
        self.production_count += random.randint(1, 3)
        
        # Line speed varies
        self.line_speed += random.uniform(-5, 5)
        self.line_speed = max(50, min(150, self.line_speed))
        
        # Temperature varies with production
        base_temp = 25 + (self.line_speed - 100) * 0.1
        self.temperature = base_temp + random.uniform(-2, 2)
        
        # Pressure correlates with speed
        self.pressure = 1.0 + (self.line_speed / 100) * 0.5 + random.uniform(-0.1, 0.1)
        
        # Vibration increases with speed and wear
        self.vibration = 0.3 + (self.line_speed / 100) * 0.4 + random.uniform(0, 0.2)
        
        # Quality rate varies
        self.quality_rate += random.uniform(-0.5, 0.5)
        self.quality_rate = max(95, min(99.5, self.quality_rate))
        
        # Random alarms
        if random.random() < 0.05:  # 5% chance
            self.alarm_state = not self.alarm_state
    
    def publish_data(self):
        """Publish manufacturing data"""
        while self.running:
            try:
                self.simulate_data()
                
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "plc_id": CLIENT_ID,
                    "production_count": self.production_count,
                    "line_speed": round(self.line_speed, 1),
                    "temperature": round(self.temperature, 1),
                    "pressure": round(self.pressure, 2),
                    "vibration": round(self.vibration, 2),
                    "quality_rate": round(self.quality_rate, 1),
                    "alarm": self.alarm_state,
                    "status": "running" if not self.alarm_state else "alarm"
                }
                
                payload = json.dumps(data)
                self.client.publish(TOPIC, payload, qos=1)
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Published: "
                      f"Count={self.production_count}, Speed={self.line_speed:.1f}, "
                      f"Temp={self.temperature:.1f}°C, Status={data['status']}")
                
                time.sleep(PUBLISH_INTERVAL)
                
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error: {e}")
                time.sleep(1)
    
    def start(self):
        """Start the PLC simulator"""
        try:
            # Set will message for clean disconnect detection
            self.client.will_set(f"status/{CLIENT_ID}", "offline", retain=True)
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connecting to {BROKER}:{PORT}")
            self.client.connect(BROKER, PORT, 60)
            
            # Start MQTT loop in background
            self.client.loop_start()
            
            # Start publishing thread
            publish_thread = threading.Thread(target=self.publish_data, daemon=True)
            publish_thread.start()
            
            # Keep main thread alive
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Shutting down...")
            self.running = False
            self.client.publish(f"status/{CLIENT_ID}", "offline", retain=True)
            self.client.disconnect()
            self.client.loop_stop()

if __name__ == "__main__":
    plc = PLC1Simulator()
    plc.start()
