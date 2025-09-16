# OT Networking Protocols Demos
This repository contains all the Industrial Protocol Demos for the [RITSEC OT Security Interest Group](https://ritsec.club/groups#:~:text=presentations%20and%20demos.-,OT%20Security,-Tuesday%205%3A00) meeting on OT Protocols.

## OPC UA Demo
The demo used in the presentation is just server and client example but there are many more in the provided repo.
[Demo Repository](https://github.com/FreeOpcUa/opcua-asyncio)

## Modbus RTU Demo
Go to `modbus/modbus-rtu-demo.md`, the instructions for how to install and setup the demo are in that file.

## MQTT Protocol Demos

This repository includes three comprehensive MQTT demonstrations showcasing different Quality of Service (QoS) levels:

### Demo Overview

| Demo | QoS Level | Port | Description |
|------|-----------|------|-------------|
| **part1-mqtt** | QoS=0 | 1883 | Fire-and-forget messaging (no acknowledgments) |
| **part2-mqtt** | QoS=1 | 1884 | At-least-once delivery (two-step handshake) |
| **part3-mqtt** | QoS=2 | 1885 | Exactly-once delivery (four-step handshake) |

Each demo includes:
- **MQTT Broker**: Eclipse Mosquitto for message routing
- **PLC Publisher**: Simulates a component publishing data
- **Database Subscriber**: Subscribes to topic and stores data in SQLite

### Architecture

```
PLC Publisher → MQTT Broker → Database Subscriber
```
- **QoS=0 (part1-mqtt)**: `PUBLISH` (fire and forget)
- **QoS=1 (part2-mqtt)**: `PUBLISH → PUBACK` (guaranteed delivery)
- **QoS=2 (part3-mqtt)**: `PUBLISH → PUBREC → PUBREL → PUBCOMP` (exactly once)

## Prerequisites

### Windows Installation

1. **Install Docker Desktop for Windows**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Enable WSL 2 backend during installation
   - Restart computer after installation

2. **Install Git for Windows**
   - Download from: https://git-scm.com/download/win
   - Use default installation settings

3. **Verify Installation**
   ```cmd
   docker --version
   docker-compose --version
   git --version
   ```

### Mac Installation

1. **Install Docker Desktop for Mac**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Drag to Applications folder and launch

2. **Install Git (if not already installed)**
   ```bash
   # Using Homebrew (recommended)
   brew install git
   
   # Or download from: https://git-scm.com/download/mac
   ```

3. **Verify Installation**
   ```bash
   docker --version
   docker-compose --version
   git --version
   ```

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd protocol_demos
```

### 2. Run Individual Demos

**QoS=0 Demo (Fire and Forget)**
```bash
cd part1-mqtt
docker-compose up
```

**QoS=1 Demo (At Least Once)**
```bash
cd part2-mqtt
docker-compose up
```

**QoS=2 Demo (Exactly Once)**
```bash
cd part3-mqtt
docker-compose up
```

### 3. View Traffic Logs

**View all traffic (recommended for demos):**
```bash
docker-compose logs -f
```

**View specific components:**
```bash
# Broker traffic
docker-compose logs -f mqtt_broker_qos1

# Publisher traffic  
docker-compose logs -f plc_publisher_qos1

# Subscriber traffic
docker-compose logs -f database_subscriber_qos1
```

### 4. Stop Demos
```bash
docker-compose down
```

## Understanding the Protocol

### What You'll See in the Logs

**MQTT Broker Logs:**
- Client connections with unique IDs (e.g., `PLC_Publisher_QoS1`)
- Message routing between publisher and subscriber
- QoS-specific handshake messages (PUBACK, PUBREC, PUBREL, PUBCOMP)

**Publisher Logs:**
- Connection status and client ID
- Message publishing with QoS level
- Handshake confirmations (QoS=1/2 only)

**Subscriber Logs:**
- Subscription confirmations
- Message reception details
- Database storage confirmations
- Handshake participation (QoS=1/2 only)

### Key MQTT Concepts Demonstrated

- **Topics**: Named channels for message routing (`sensor/data`)
- **Client IDs**: Unique identifiers for tracking (`PLC_Publisher_QoS1`)
- **Quality of Service**: Delivery guarantees (0, 1, 2)
- **Publish/Subscribe**: Decoupled communication pattern
- **Message Handshakes**: Reliability mechanisms

## Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Check what's using the port
netstat -an | findstr :1883  # Windows
lsof -i :1883                 # Mac

# Stop conflicting services or use different ports
```

**Docker Permission Issues (Mac/Linux):**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

**Container Won't Start:**
```bash
# Check Docker is running
docker ps

# Check logs for errors
docker-compose logs
```

### Getting Help

- Check container logs: `docker-compose logs [service_name]`
- Verify Docker is running: `docker ps`
- Restart Docker Desktop if needed
- Ensure ports 1883-1885 are available

