# MQTT QoS=1 Demo - Guaranteed Delivery

An MQTT demonstration showing **Quality of Service Level 1** with 3 components:
- **MQTT Broker**: Routes messages and handles delivery confirmations
- **PLC Publisher**: Sends data with QoS=1 and waits for PUBACK confirmation
- **Database Subscriber**: Receives messages with QoS=1 and auto-acknowledges

## Architecture - QoS=1 Two-Step Handshake

```
PLC Publisher  ──PUBLISH(QoS=1)──→  MQTT Broker  ──PUBLISH(QoS=1)──→  Database Subscriber
              ←────PUBACK─────────               ←────PUBACK──────────
```

**QoS=1 Flow:**
1. Publisher sends PUBLISH message with QoS=1
2. Broker acknowledges with PUBACK (Publisher → Broker confirmed)
3. Broker forwards message to subscriber with QoS=1
4. Subscriber automatically sends PUBACK (Broker → Subscriber confirmed)

## Quick Start

1. **Start all services:**
   ```bash
   cd part2-mqtt
   docker-compose up
   ```

2. **View logs to see QoS=1 handshake:**
   ```bash
   # See all traffic (recommended for demos)
   docker-compose logs -f
   
   # Or view individual components:
   docker-compose logs -f mqtt_broker_qos1      # Broker QoS=1 routing
   docker-compose logs -f plc_publisher_qos1    # PLC with PUBACK confirmations
   docker-compose logs -f database_subscriber_qos1  # Database with auto-ACK
   ```

   **Note**: This demo runs on port **1884** to avoid conflicts with simple-mqtt (port 1883)

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

### PLC Publisher (plc1.py) - QoS=1
```python
# Publish with QoS=1 for guaranteed delivery
result = client.publish("sensor/data", json.dumps(data), qos=1)

# Callback when PUBACK is received
def on_publish(client, userdata, mid):
    print(f"✅ PUBACK received! Message {mid} delivery confirmed")
```

### Database Subscriber (database_subscriber.py) - QoS=1
```python
# Subscribe with QoS=1 for guaranteed delivery
client.subscribe("sensor/data", qos=1)

# Messages received with QoS=1 are automatically acknowledged
def on_message(client, userdata, msg):
    print(f"QoS: {msg.qos}")  # Will show QoS=1
    # Process message - client auto-sends acknowledgment
```

## MQTT QoS=1 Concepts Demonstrated

- **QoS=1 (At Least Once)**: Guaranteed message delivery with acknowledgments
- **PUBLISH/PUBACK Handshake**: Two-step confirmation process
- **Message IDs**: Unique identifiers for tracking acknowledgments
- **Automatic Acknowledgment**: Client libraries handle PUBACK automatically
- **Reliability**: Messages are retransmitted if PUBACK not received

This demo shows **guaranteed delivery**: the publisher waits for PUBACK confirmation from the broker, ensuring the message was received and will be delivered to subscribers.

## What You'll See in the Logs

When you run `docker-compose logs -f`, you'll see:

**MQTT Broker:**
- Connection messages when clients connect/disconnect
- Message routing details (publish/subscribe events)
- Debug information about message flow

**PLC Publisher:**
- Connection status with QoS=1 indication
- PUBLISH messages sent with Message IDs
- **PUBACK confirmations** received from broker
- Two-step handshake completion messages

**Database Subscriber:**
- QoS=1 subscription confirmation
- QoS=1 message reception details
- **Automatic acknowledgment** notifications
- Database storage confirmations

**MQTT Broker:**
- PUBLISH message routing with QoS=1
- PUBACK acknowledgment handling
- Message delivery confirmations

The logs will show the complete **QoS=1 handshake**: PUBLISH → PUBACK → Message Processing → Auto-ACK with full visibility into guaranteed delivery.
