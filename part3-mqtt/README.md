# MQTT QoS=2 Demo - Exactly Once Delivery

An MQTT demonstration showing **Quality of Service Level 2** with 3 components:
- **MQTT Broker**: Routes messages and handles four-step handshake protocol
- **PLC Publisher**: Sends data with QoS=2 and waits for PUBCOMP confirmation
- **Database Subscriber**: Receives messages with QoS=2 exactly once guarantee

## Architecture - QoS=2 Four-Step Handshake

```
PLC Publisher  ──PUBLISH(QoS=2)──→  MQTT Broker  ──PUBLISH(QoS=2)──→  Database Subscriber
              ←────PUBREC─────────               ←────PUBREC──────────
              ──────PUBREL────────→               ──────PUBREL────────→
              ←────PUBCOMP────────               ←────PUBCOMP─────────
```

**QoS=2 Flow (Exactly Once):**
1. Publisher sends PUBLISH message with QoS=2
2. Broker acknowledges with PUBREC (message received, not yet delivered)
3. Publisher sends PUBREL (release message for delivery)
4. Broker sends PUBCOMP (message delivered exactly once)
5. Same four-step process happens between Broker → Subscriber

## Quick Start

1. **Start all services:**
   ```bash
   cd part3-mqtt
   docker-compose up
   ```

2. **View logs to see QoS=2 four-step handshake:**
   ```bash
   # See all traffic (recommended for demos)
   docker-compose logs -f
   
   # Or view individual components:
   docker-compose logs -f mqtt_broker_qos2      # Broker QoS=2 routing
   docker-compose logs -f plc_publisher_qos2    # PLC with PUBCOMP confirmations
   docker-compose logs -f database_subscriber_qos2  # Database exactly-once delivery
   ```

   **Note**: This demo runs on port **1885** to avoid conflicts with simple-mqtt (1883) and part2-mqtt (1884)

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

### PLC Publisher (plc1.py) - QoS=2
```python
# Publish with QoS=2 for exactly-once delivery
result = client.publish("sensor/data", json.dumps(data), qos=2)

# Callback when PUBCOMP is received (four-step handshake complete)
def on_publish(client, userdata, mid):
    print(f"PUBCOMP received! Message {mid} delivered exactly once")
    print(f"Four-step handshake complete: PUBLISH → PUBREC → PUBREL → PUBCOMP")
```

### Database Subscriber (database_subscriber.py) - QoS=2
```python
# Subscribe with QoS=2 for exactly-once delivery
client.subscribe("sensor/data", qos=2)

# Messages received with QoS=2 use four-step handshake
def on_message(client, userdata, msg):
    print(f"QoS: {msg.qos}")  # Will show QoS=2
    # Process message - client handles four-step handshake automatically
```

## MQTT QoS=2 Concepts Demonstrated

- **QoS=2 (Exactly Once)**: Guaranteed exactly-once message delivery
- **Four-Step Handshake**: PUBLISH → PUBREC → PUBREL → PUBCOMP
- **Message Deduplication**: Broker ensures no duplicate deliveries
- **Highest Reliability**: Most robust delivery guarantee in MQTT
- **Performance Trade-off**: Higher overhead but strongest guarantees

This demo shows **exactly-once delivery**: the most reliable MQTT QoS level that guarantees messages are delivered once and only once, preventing duplicates even in network failure scenarios.

## What You'll See in the Logs

When you run `docker-compose logs -f`, you'll see:

**MQTT Broker:**
- Connection messages when clients connect/disconnect
- Message routing details (publish/subscribe events)
- Debug information about message flow

**PLC Publisher:**
- Connection status with QoS=2 indication
- PUBLISH messages sent with Message IDs
- **Four-step handshake progress** (PUBLISH → PUBREC → PUBREL → PUBCOMP)
- PUBCOMP confirmations for exactly-once delivery

**Database Subscriber:**
- QoS=2 subscription confirmation
- QoS=2 message reception details
- **Four-step handshake participation**
- Exactly-once delivery confirmations

**MQTT Broker:**
- PUBLISH message routing with QoS=2
- PUBREC, PUBREL, and PUBCOMP handling
- Message deduplication and exactly-once guarantees

The logs will show the complete **QoS=2 four-step handshake**: PUBLISH → PUBREC → PUBREL → PUBCOMP with full visibility into exactly-once delivery guarantees.
