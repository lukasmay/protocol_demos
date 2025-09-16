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
   # See all traffic (recommended for demos)
   docker-compose logs -f
   
   # Or view individual components:
   docker-compose logs -f mqtt_broker      # Broker message routing
   docker-compose logs -f plc_publisher    # PLC publishing data
   docker-compose logs -f database_subscriber  # Database receiving data
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

## What You'll See in the Logs

When you run `docker-compose logs -f`, you'll see:

**MQTT Broker:**
- Connection messages when clients connect/disconnect
- Message routing details (publish/subscribe events)
- Debug information about message flow

**PLC Publisher:**
- Connection status to broker
- Each message being published with payload
- Message IDs for tracking

**Database Subscriber:**
- Connection and subscription status
- Detailed message reception info
- Database storage confirmations
- Raw JSON payloads being processed

The logs will show the complete data flow: PLC → Broker → Database with full visibility into the MQTT message exchange.
