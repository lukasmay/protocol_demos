# Simple MQTT Demo

A minimal MQTT demonstration with 3 components:
- **MQTT Broker**: Routes messages between publisher and subscriber
- **PLC Publisher**: Simulates an industrial sensor sending temperature and pressure data
- **Database Subscriber**: Receives and stores sensor data in SQLite database

## Architecture

```
PLC Publisher → MQTT Broker → Database Subscriber
```

## Quick Start

1. **Start all services:**
   ```bash
   docker-compose up
   ```

2. **View logs to see data flow:**
   ```bash
   # PLC publishing data
   docker-compose logs -f plc_publisher
   
   # Database receiving data  
   docker-compose logs -f database_subscriber
   ```

3. **Stop the demo:**
   ```bash
   docker-compose down
   ```

## What Each Component Does

### MQTT Broker (`mqtt_broker`)
- Uses Eclipse Mosquitto
- Listens on port 1883
- Routes messages from publishers to subscribers
- **Key concept**: Acts as a message hub - publishers send to it, subscribers receive from it

### PLC Publisher (`plc_publisher`)
- Simulates an industrial sensor
- Generates random temperature (20-30°C) and pressure (1-2 bar) readings
- Publishes data to topic `sensor/data` every 3 seconds
- **Key concept**: Producer of data - sends messages to the broker

### Database Subscriber (`database_subscriber`)  
- Listens for messages on topic `sensor/data`
- Stores received data in SQLite database
- Database persists in Docker volume `database_data`
- **Key concept**: Consumer of data - receives messages from the broker

## Code Explanation

### PLC Publisher (plc1.py)
```python
# Connect to MQTT broker
client = mqtt.Client()
client.connect(BROKER, PORT, 60)

# Generate sensor data
data = {
    "temperature": 25 + random.uniform(-5, 5),
    "pressure": 1.5 + random.uniform(-0.5, 0.5)
}

# Publish to topic
client.publish("sensor/data", json.dumps(data))
```

### Database Subscriber (database_subscriber.py)
```python
# Subscribe to topic
client.subscribe("sensor/data")

# Handle incoming messages
def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    # Store in SQLite database
    cursor.execute("INSERT INTO sensor_readings ...")
```

## MQTT Concepts Demonstrated

- **Topics**: Named channels for messages (`sensor/data`)
- **Publish/Subscribe**: Decoupled communication pattern
- **Quality of Service**: Reliable message delivery
- **JSON Payloads**: Structured data exchange

This demo shows the core MQTT pattern: devices publish data to topics, and applications subscribe to topics to receive that data, all coordinated by a central broker.
