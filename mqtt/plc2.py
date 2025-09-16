#!/usr/bin/env python3
"""
PLC2 Simulator - Energy Management System
Publishes energy data to topic2
"""
import paho.mqtt.client as mqtt
import json
import time
import random
import threading
import math
import os
from datetime import datetime

# Configuration
BROKER = os.getenv("BROKER", "localhost")
PORT = int(os.getenv("PORT", "1883"))
CLIENT_ID = "PLC2"
TOPIC = "factory/energy"
PUBLISH_INTERVAL = 3  # seconds

class PLC2Simulator:
    def __init__(self):
        self.client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.running = False
        
        # Energy management state
        self.power_consumption = 250.0  # kW
        self.voltage_l1 = 400.0  # V
        self.voltage_l2 = 400.0  # V
        self.voltage_l3 = 400.0  # V
        self.current_l1 = 180.0  # A
        self.current_l2 = 180.0  # A
        self.current_l3 = 180.0  # A
        self.power_factor = 0.85
        self.frequency = 50.0  # Hz
        self.energy_total = 12450.0  # kWh
        self.demand_peak = 280.0  # kW
        self.grid_status = "normal"
        
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
        """Simulate realistic energy data"""
        # Time-based load variation (higher during work hours)
        hour = datetime.now().hour
        load_factor = 0.7 + 0.3 * math.sin((hour - 6) * math.pi / 12) if 6 <= hour <= 18 else 0.4
        
        # Base power consumption with variation
        base_power = 200 + 100 * load_factor
        self.power_consumption = base_power + random.uniform(-20, 20)
        
        # Voltage variations (small fluctuations)
        self.voltage_l1 = 400 + random.uniform(-5, 5)
        self.voltage_l2 = 400 + random.uniform(-5, 5)
        self.voltage_l3 = 400 + random.uniform(-5, 5)
        
        # Current based on power and voltage
        avg_voltage = (self.voltage_l1 + self.voltage_l2 + self.voltage_l3) / 3
        base_current = (self.power_consumption * 1000) / (avg_voltage * math.sqrt(3) * self.power_factor)
        
        self.current_l1 = base_current + random.uniform(-10, 10)
        self.current_l2 = base_current + random.uniform(-10, 10)
        self.current_l3 = base_current + random.uniform(-10, 10)
        
        # Power factor variations
        self.power_factor += random.uniform(-0.02, 0.02)
        self.power_factor = max(0.75, min(0.95, self.power_factor))
        
        # Frequency stability
        self.frequency = 50.0 + random.uniform(-0.1, 0.1)
        
        # Accumulate energy
        self.energy_total += (self.power_consumption * PUBLISH_INTERVAL) / 3600  # kWh
        
        # Track peak demand
        if self.power_consumption > self.demand_peak:
            self.demand_peak = self.power_consumption
        
        # Grid status changes
        if random.random() < 0.02:  # 2% chance
            statuses = ["normal", "high_demand", "voltage_sag", "frequency_drift"]
            self.grid_status = random.choice(statuses)
        elif self.grid_status != "normal" and random.random() < 0.3:
            self.grid_status = "normal"
    
    def publish_data(self):
        """Publish energy management data"""
        while self.running:
            try:
                self.simulate_data()
                
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "plc_id": CLIENT_ID,
                    "power_consumption": round(self.power_consumption, 1),
                    "voltages": {
                        "L1": round(self.voltage_l1, 1),
                        "L2": round(self.voltage_l2, 1),
                        "L3": round(self.voltage_l3, 1)
                    },
                    "currents": {
                        "L1": round(self.current_l1, 1),
                        "L2": round(self.current_l2, 1),
                        "L3": round(self.current_l3, 1)
                    },
                    "power_factor": round(self.power_factor, 3),
                    "frequency": round(self.frequency, 2),
                    "energy_total": round(self.energy_total, 1),
                    "demand_peak": round(self.demand_peak, 1),
                    "grid_status": self.grid_status,
                    "efficiency": round((self.power_factor * 100), 1)
                }
                
                payload = json.dumps(data)
                self.client.publish(TOPIC, payload, qos=1)
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Published: "
                      f"Power={self.power_consumption:.1f}kW, PF={self.power_factor:.3f}, "
                      f"Grid={self.grid_status}")
                
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
    plc = PLC2Simulator()
    plc.start()
