#!/usr/bin/env python3
"""
Simple PLC Publisher - Sends sensor data to MQTT broker
This simulates a basic industrial sensor publishing temperature and pressure data
"""
import paho.mqtt.client as mqtt
import json
import time
import random
import os

# Configuration - Environment variables for Docker deployment
BROKER = os.getenv("BROKER", "localhost")  # MQTT broker hostname
PORT = int(os.getenv("PORT", "1883"))      # MQTT broker port
TOPIC = "sensor/data"                      # Topic to publish data to
PUBLISH_INTERVAL = 3                       # Publish every 3 seconds

def on_connect(client, userdata, flags, rc):
    """Callback when MQTT client connects to broker"""
    if rc == 0:
        print(f"✅ Connected to MQTT broker at {BROKER}:{PORT}")
    else:
        print(f"❌ Failed to connect to broker. Error code: {rc}")

def generate_sensor_data():
    """Generate simulated sensor readings"""
    # Simulate temperature sensor (20-30°C with some variation)
    temperature = 25 + random.uniform(-5, 5)
    
    # Simulate pressure sensor (1.0-2.0 bar with some variation)  
    pressure = 1.5 + random.uniform(-0.5, 0.5)
    
    # Create data packet with timestamp
    data = {
        "timestamp": time.time(),
        "temperature": round(temperature, 2),
        "pressure": round(pressure, 2),
        "unit_id": "PLC-001"
    }
    
    return data

def main():
    """Main function - sets up MQTT client and publishes data"""
    # Create MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    
    try:
        # Connect to broker
        print(f"🔄 Connecting to MQTT broker at {BROKER}:{PORT}")
        client.connect(BROKER, PORT, 60)
        client.loop_start()  # Start background network loop
        
        # Main publishing loop
        while True:
            # Generate new sensor data
            sensor_data = generate_sensor_data()
            
            # Convert to JSON string
            payload = json.dumps(sensor_data)
            
            # Publish to MQTT topic
            client.publish(TOPIC, payload)
            
            # Print what we sent
            print(f"📤 Published: Temp={sensor_data['temperature']}°C, "
                  f"Pressure={sensor_data['pressure']} bar")
            
            # Wait before next reading
            time.sleep(PUBLISH_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down PLC publisher...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
