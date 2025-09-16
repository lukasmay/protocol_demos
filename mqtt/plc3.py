#!/usr/bin/env python3
"""
PLC3 Simulator - Environmental Monitoring System
Publishes environmental data to topic3
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
CLIENT_ID = "PLC3"
TOPIC = "factory/environment"
PUBLISH_INTERVAL = 4  # seconds

class PLC3Simulator:
    def __init__(self):
        self.client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.running = False
        
        # Environmental monitoring state
        self.temperature = 22.0  # °C
        self.humidity = 45.0  # %
        self.air_pressure = 1013.25  # hPa
        self.co2_level = 400.0  # ppm
        self.air_quality_index = 25  # AQI
        self.noise_level = 65.0  # dB
        self.light_level = 500.0  # lux
        self.particulate_pm25 = 12.0  # μg/m³
        self.particulate_pm10 = 20.0  # μg/m³
        self.wind_speed = 2.5  # m/s
        self.wind_direction = 180  # degrees
        self.uv_index = 3.0
        
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
        """Simulate realistic environmental data"""
        # Time-based variations
        hour = datetime.now().hour
        
        # Temperature follows daily cycle
        daily_temp_variation = 3 * math.sin((hour - 6) * math.pi / 12)
        self.temperature = 22 + daily_temp_variation + random.uniform(-1, 1)
        
        # Humidity inversely related to temperature
        base_humidity = 50 - (self.temperature - 22) * 2
        self.humidity = base_humidity + random.uniform(-5, 5)
        self.humidity = max(20, min(80, self.humidity))
        
        # Air pressure variations
        self.air_pressure += random.uniform(-2, 2)
        self.air_pressure = max(1000, min(1030, self.air_pressure))
        
        # CO2 levels higher during work hours
        work_hour_factor = 1.5 if 8 <= hour <= 17 else 1.0
        self.co2_level = 400 * work_hour_factor + random.uniform(-50, 100)
        self.co2_level = max(350, min(1000, self.co2_level))
        
        # Air quality index based on CO2 and particulates
        base_aqi = (self.co2_level - 400) / 10 + self.particulate_pm25
        self.air_quality_index = max(0, min(150, base_aqi + random.uniform(-5, 5)))
        
        # Noise level higher during work hours
        base_noise = 70 if 8 <= hour <= 17 else 55
        self.noise_level = base_noise + random.uniform(-5, 10)
        
        # Light level based on time of day
        if 6 <= hour <= 18:
            base_light = 800 * math.sin((hour - 6) * math.pi / 12)
        else:
            base_light = 50  # Artificial lighting
        self.light_level = max(10, base_light + random.uniform(-50, 50))
        
        # Particulate matter variations
        self.particulate_pm25 += random.uniform(-2, 2)
        self.particulate_pm25 = max(5, min(50, self.particulate_pm25))
        
        self.particulate_pm10 = self.particulate_pm25 * 1.6 + random.uniform(-3, 3)
        self.particulate_pm10 = max(10, min(80, self.particulate_pm10))
        
        # Wind conditions
        self.wind_speed += random.uniform(-0.5, 0.5)
        self.wind_speed = max(0, min(10, self.wind_speed))
        
        self.wind_direction += random.uniform(-15, 15)
        self.wind_direction = self.wind_direction % 360
        
        # UV index based on time and weather
        if 10 <= hour <= 16:
            self.uv_index = 5 * math.sin((hour - 10) * math.pi / 6) + random.uniform(-1, 1)
        else:
            self.uv_index = 0
        self.uv_index = max(0, min(11, self.uv_index))
    
    def get_air_quality_status(self):
        """Determine air quality status based on AQI"""
        if self.air_quality_index <= 50:
            return "good"
        elif self.air_quality_index <= 100:
            return "moderate"
        elif self.air_quality_index <= 150:
            return "unhealthy_sensitive"
        else:
            return "unhealthy"
    
    def publish_data(self):
        """Publish environmental monitoring data"""
        while self.running:
            try:
                self.simulate_data()
                
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "plc_id": CLIENT_ID,
                    "temperature": round(self.temperature, 1),
                    "humidity": round(self.humidity, 1),
                    "air_pressure": round(self.air_pressure, 2),
                    "co2_level": round(self.co2_level, 1),
                    "air_quality": {
                        "index": round(self.air_quality_index, 1),
                        "status": self.get_air_quality_status()
                    },
                    "noise_level": round(self.noise_level, 1),
                    "light_level": round(self.light_level, 1),
                    "particulates": {
                        "pm2_5": round(self.particulate_pm25, 1),
                        "pm10": round(self.particulate_pm10, 1)
                    },
                    "wind": {
                        "speed": round(self.wind_speed, 1),
                        "direction": round(self.wind_direction, 0)
                    },
                    "uv_index": round(self.uv_index, 1),
                    "comfort_index": round((100 - abs(self.temperature - 22) * 5 - abs(self.humidity - 50) * 0.5), 1)
                }
                
                payload = json.dumps(data)
                self.client.publish(TOPIC, payload, qos=1)
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Published: "
                      f"Temp={self.temperature:.1f}°C, Humidity={self.humidity:.1f}%, "
                      f"AQI={self.air_quality_index:.1f} ({self.get_air_quality_status()})")
                
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
    plc = PLC3Simulator()
    plc.start()
