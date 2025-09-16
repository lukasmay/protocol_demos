# MQTT Industrial IoT Protocol Demo

A comprehensive demonstration of MQTT protocol in an industrial IoT environment, showing real-world communication patterns between PLCs, HMIs, databases, and cloud systems.

## 🏭 Demo Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    INDUSTRIAL MQTT DEMO                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PLC1 (Manufacturing) ──┐                                      │
│  Topic: factory/line1   │    ┌─────────────────┐               │
│                         ├───▶│  Local MQTT     │               │
│  PLC2 (Energy)      ────┤    │  Broker         │               │
│  Topic: factory/energy  │    │  Port: 1883     │               │
│                         │    └─────────────────┘               │
│  PLC3 (Environment) ────┤           │                          │
│  Topic: factory/environment          │                          │
│                         │           │                          │
│  ┌─────────────────────┐│           │                          │
│  │ HMI1 (Manufacturing)││           │                          │
│  │ Subscribes to topic1││           │                          │
│  └─────────────────────┘│           │                          │
│                         │           │                          │
│  ┌─────────────────────┐│           │                          │
│  │ HMI2 (Energy)       ││           │                          │
│  │ Subscribes to topic2││           │                          │
│  └─────────────────────┘│           │                          │
│                         │           │                          │
│  ┌─────────────────────┐│           │                          │
│  │ Historian DB        ││           │                          │
│  │ Subscribes to 1,2,3 ││           │                          │
│  └─────────────────────┘│           │                          │
│                         │           │                          │
│  ┌─────────────────────┐│           │                          │
│  │ Bridge Client       ││           │                          │
│  │ Subs: topics 2,3    ││           │                          │
│  │ Pubs: topic 4       │├───────────┘                          │
│  └─────────────────────┘│                                      │
│                         │    ┌─────────────────┐               │
│                         └───▶│  Cloud MQTT     │               │
│                              │  Broker         │               │
│                              │  Port: 1884     │               │
│                              └─────────────────┘               │
│                                     │                          │
│  ┌─────────────────────┐            │                          │
│  │ Cloud Dashboard     │◀───────────┤                          │
│  │ Subscribes to topic4│            │                          │
│  └─────────────────────┘            │                          │
│                                     │                          │
│  ┌─────────────────────┐            │                          │
│  │ Analytics Engine    │◀───────────┘                          │
│  │ Subscribes to topic4│                                       │
│  │ AI Insights & Pred. │                                       │
│  └─────────────────────┘                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 📋 Components Overview

### Data Publishers (PLCs)
- **PLC1** - Manufacturing Line Controller
  - Publishes production metrics to `factory/line1`
  - Data: production count, line speed, temperature, pressure, quality rates
  
- **PLC2** - Energy Management System  
  - Publishes energy data to `factory/energy`
  - Data: power consumption, voltages, currents, power factor, grid status
  
- **PLC3** - Environmental Monitoring
  - Publishes environmental data to `factory/environment`
  - Data: temperature, humidity, air quality, CO2 levels, comfort metrics

### Data Subscribers (HMIs)
- **HMI1** - Manufacturing Dashboard
  - Subscribes to `factory/line1`
  - Real-time production monitoring with alarms
  
- **HMI2** - Energy Management Dashboard
  - Subscribes to `factory/energy`
  - Power monitoring with efficiency metrics

### Data Storage & Processing
- **Historian** - Industrial Database
  - Subscribes to all factory topics (`factory/line1`, `factory/energy`, `factory/environment`)
  - Stores timestamped data in SQLite database
  - Automatic data cleanup (7-day retention)

- **Bridge** - Cloud Data Aggregator
  - Subscribes to `factory/energy` and `factory/environment`
  - Aggregates and analyzes data every 10 seconds
  - Publishes combined analytics to `cloud/factory/analytics`
  - Generates critical alerts and facility health metrics

### Cloud Components
- **Cloud Dashboard** - Executive Analytics
  - Subscribes to `cloud/factory/analytics`
  - High-level facility overview with KPIs
  - Performance trends and recommendations

- **Analytics Engine** - AI Insights
  - Subscribes to `cloud/factory/analytics`
  - Predictive analytics and maintenance forecasting
  - Automated insight generation with impact scoring

### Infrastructure
- **Local MQTT Broker** (Port 1883)
  - Handles local factory communication
  - Topics: `factory/*`, `status/*`
  
- **Cloud MQTT Broker** (Port 1884)
  - Simulates cloud infrastructure
  - Topics: `cloud/*`

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone and navigate to the MQTT demo
cd mqtt

# Start the complete demo
./start_demo.sh

# View logs from specific components
docker-compose logs -f plc1
docker-compose logs -f hmi1
docker-compose logs -f cloud_dashboard

# Stop the demo
./stop_demo.sh
```

### Option 2: Standalone Mode

```bash
# Install dependencies
pip install paho-mqtt

# Install Mosquitto MQTT broker
# Ubuntu/Debian: sudo apt-get install mosquitto
# macOS: brew install mosquitto
# Windows: Download from https://mosquitto.org/download/

# Run standalone demo
cd mqtt
python run_standalone.py
```

### Option 3: Manual Component Testing

```bash
# Terminal 1: Start local broker
mosquitto -c config/mosquitto.conf

# Terminal 2: Start cloud broker  
mosquitto -c config/cloud_mosquitto.conf

# Terminal 3: Start PLC1
python plc1.py

# Terminal 4: Start HMI1
python hmi1.py

# Add more components as needed...
```

## 📊 Viewing Real-time Data

### MQTT Topic Monitoring

```bash
# Monitor all factory data
mosquitto_sub -h localhost -p 1883 -t 'factory/#'

# Monitor specific PLC
mosquitto_sub -h localhost -p 1883 -t 'factory/line1'
mosquitto_sub -h localhost -p 1883 -t 'factory/energy'

# Monitor cloud analytics
mosquitto_sub -h localhost -p 1884 -t 'cloud/#'

# Monitor system status
mosquitto_sub -h localhost -p 1883 -t 'status/#'
```

### Interactive Dashboards

```bash
# Manufacturing Line Dashboard
docker exec -it hmi1 python main.py

# Energy Management Dashboard  
docker exec -it hmi2 python main.py

# Cloud Analytics Dashboard
docker exec -it cloud_dashboard python main.py
```

## 🔧 Configuration

### MQTT Topics Structure

```
factory/
├── line1           # PLC1 → HMI1, Historian
├── energy          # PLC2 → HMI2, Historian, Bridge
└── environment     # PLC3 → Historian, Bridge

cloud/
└── factory/
    └── analytics   # Bridge → Cloud Dashboard, Analytics

status/
├── PLC1           # Connection status
├── PLC2
├── HMI1
└── [component]
```

### Data Formats

#### Manufacturing Data (factory/line1)
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "plc_id": "PLC1",
  "production_count": 1247,
  "line_speed": 105.2,
  "temperature": 26.8,
  "pressure": 1.25,
  "vibration": 0.45,
  "quality_rate": 98.7,
  "alarm": false,
  "status": "running"
}
```

#### Energy Data (factory/energy)
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "plc_id": "PLC2", 
  "power_consumption": 267.5,
  "voltages": {"L1": 402.1, "L2": 399.8, "L3": 401.3},
  "currents": {"L1": 185.2, "L2": 182.7, "L3": 187.1},
  "power_factor": 0.867,
  "frequency": 50.02,
  "energy_total": 12847.3,
  "grid_status": "normal",
  "efficiency": 86.7
}
```

#### Environmental Data (factory/environment)
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "plc_id": "PLC3",
  "temperature": 23.2,
  "humidity": 47.8,
  "co2_level": 456.2,
  "air_quality": {"index": 28.5, "status": "good"},
  "noise_level": 67.3,
  "comfort_index": 87.2
}
```

#### Cloud Analytics (cloud/factory/analytics)
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "bridge_id": "Bridge",
  "aggregation_period": 10,
  "energy_analytics": {
    "power_consumption": {"average": 265.2, "trend": "stable"},
    "efficiency": {"average": 85.4}
  },
  "environment_analytics": {
    "temperature": {"average": 23.1, "trend": "stable"},
    "air_quality": {"average_index": 29.1}
  },
  "critical_alerts": [],
  "facility_status": {
    "energy_efficiency": 85.4,
    "environmental_comfort": 86.8,
    "overall_health": true
  }
}
```

## 🛠️ Development

### Adding New Components

1. Create new Python file (e.g., `new_component.py`)
2. Add MQTT client configuration
3. Implement publish/subscribe logic
4. Add to `docker-compose.yml`
5. Update documentation

### Customizing Data

- Modify simulation parameters in PLC files
- Adjust aggregation intervals in `bridge.py`
- Change alert thresholds in HMI files
- Customize analytics in `analytics.py`

### Database Schema

#### Historian Database (historian.db)
- `manufacturing_data` - Production metrics
- `energy_data` - Power and electrical data
- `environmental_data` - Environmental sensors

#### Analytics Database (analytics.db)
- `analytics_data` - Aggregated metrics
- `predictions` - AI predictions with confidence
- `insights` - Generated recommendations

## 🔍 Troubleshooting

### Common Issues

**Containers not starting:**
```bash
# Check Docker status
docker-compose ps

# View detailed logs
docker-compose logs [service_name]

# Restart specific service
docker-compose restart [service_name]
```

**MQTT connection issues:**
```bash
# Test broker connectivity
mosquitto_pub -h localhost -p 1883 -t test -m "hello"
mosquitto_sub -h localhost -p 1883 -t test

# Check port availability
netstat -an | grep 1883
netstat -an | grep 1884
```

**Missing dependencies:**
```bash
# Install Python requirements
pip install -r requirements.txt

# Install system dependencies
sudo apt-get install mosquitto mosquitto-clients
```

### Performance Tuning

- Adjust `PUBLISH_INTERVAL` in PLC files for data frequency
- Modify `AGGREGATION_INTERVAL` in bridge for cloud update rate
- Change database retention periods in historian
- Tune buffer sizes for high-throughput scenarios

## 📈 Monitoring & Metrics

### Key Performance Indicators

- **Message Throughput**: Messages/second per topic
- **Data Latency**: Time from publish to subscribe
- **System Health**: Component uptime and connectivity
- **Data Quality**: Missing messages and error rates

### Logging

Each component provides structured logging:
- Timestamps for all events
- Connection status changes
- Data processing statistics
- Error conditions and recovery

## 🌟 Features Demonstrated

### MQTT Protocol Features
- ✅ Publish/Subscribe messaging
- ✅ Quality of Service (QoS) levels
- ✅ Retained messages for status
- ✅ Last Will and Testament
- ✅ Topic hierarchies
- ✅ Persistent connections

### Industrial IoT Patterns
- ✅ PLC data acquisition
- ✅ HMI real-time dashboards
- ✅ Historical data storage
- ✅ Edge-to-cloud bridging
- ✅ Analytics and insights
- ✅ Alarm management
- ✅ Predictive maintenance

### System Architecture
- ✅ Microservices design
- ✅ Containerized deployment
- ✅ Service discovery
- ✅ Data persistence
- ✅ Fault tolerance
- ✅ Scalable messaging

## 📚 Learning Objectives

After running this demo, you will understand:

1. **MQTT Fundamentals**
   - Topic-based messaging
   - Publisher-subscriber pattern
   - QoS levels and message delivery
   - Connection management

2. **Industrial IoT Architecture**
   - PLC data collection patterns
   - HMI design principles
   - Historical data management
   - Cloud integration strategies

3. **System Integration**
   - Protocol bridging
   - Data aggregation
   - Real-time processing
   - Analytics pipeline

4. **Operational Aspects**
   - Monitoring and alerting
   - Performance optimization
   - Fault handling
   - Maintenance scheduling

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add new components or improve existing ones
4. Update documentation
5. Submit pull request

## 📄 License

This demo is provided under the MIT License. See LICENSE file for details.

## 🆘 Support

For questions or issues:
1. Check the troubleshooting section
2. Review component logs
3. Test MQTT connectivity
4. Open an issue with detailed error information

---

**Happy Learning! 🎓**

This demo provides a comprehensive view of MQTT in industrial environments. Experiment with different configurations, add new components, and explore the rich ecosystem of MQTT-based IoT solutions.
