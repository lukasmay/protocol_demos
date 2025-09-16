#!/usr/bin/env python3
"""
QoS=1 PLC Publisher - Demonstrates reliable message delivery
This shows the two-step handshake: PUBLISH → PUBACK for guaranteed delivery
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
        print(f"Connected to MQTT broker at {BROKER}:{PORT}")
        print(f"Will publish to topic: {TOPIC} with QoS=1")
    else:
        print(f"Failed to connect to broker. Error code: {rc}")

def on_publish(client, userdata, mid):
    """Callback when PUBACK is received from broker (QoS=1 handshake complete)"""
    print(f"✅ PUBACK received! Message {mid} delivery confirmed by broker")
    print(f"   Two-step handshake complete: PUBLISH → PUBACK")

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
    # Create MQTT client with unique ID
    client_id = "PLC_Publisher_QoS1"
    client = mqtt.Client(client_id=client_id)
    client.on_connect = on_connect
    client.on_publish = on_publish
    
    try:
        # Connect to broker
        print(f"Connecting to MQTT broker at {BROKER}:{PORT} with Client ID: {client_id}")
        client.connect(BROKER, PORT, 60)
        client.loop_start()  # Start background network loop
        
        # Main publishing loop
        while True:
            # Generate new sensor data
            sensor_data = generate_sensor_data()
            
            # Convert to JSON string
            payload = json.dumps(sensor_data)
            
            # Publish to MQTT topic with QoS=1 (guaranteed delivery)
            result = client.publish(TOPIC, payload, qos=1)
            
            # Print what we sent with message ID
            print(f"📤 PUBLISH sent: Temp={sensor_data['temperature']}°C, "
                  f"Pressure={sensor_data['pressure']} bar (MsgID: {result.mid}, QoS=1)")
            print(f"   Payload: {payload}")
            print(f"   Waiting for PUBACK from broker...")
            
            # Wait before next reading
            time.sleep(PUBLISH_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nShutting down PLC publisher...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
