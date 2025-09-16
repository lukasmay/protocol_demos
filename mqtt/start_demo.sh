#!/bin/bash

echo "=========================================="
echo "  MQTT Industrial IoT Demo Startup"
echo "=========================================="

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start all services
echo "🚀 Building and starting MQTT demo..."
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Show status
echo ""
echo "📊 Container Status:"
docker-compose ps

echo ""
echo "=========================================="
echo "  MQTT Demo Started Successfully!"
echo "=========================================="
echo ""
echo "🏭 Services Running:"
echo "  • Local MQTT Broker:     localhost:1883"
echo "  • Cloud MQTT Broker:     localhost:1884"
echo "  • PLC1 (Manufacturing):  Publishing to factory/line1"
echo "  • PLC2 (Energy):         Publishing to factory/energy"
echo "  • PLC3 (Environment):    Publishing to factory/environment"
echo "  • HMI1:                  Monitoring manufacturing"
echo "  • HMI2:                  Monitoring energy"
echo "  • Historian:             Storing all data"
echo "  • Bridge:                Aggregating data to cloud"
echo "  • Cloud Dashboard:       Analytics dashboard"
echo "  • Analytics Engine:      AI insights & predictions"
echo ""
echo "📋 View Logs:"
echo "  docker-compose logs -f [service_name]"
echo ""
echo "🔍 Available Services:"
echo "  plc1, plc2, plc3, hmi1, hmi2, historian, bridge,"
echo "  cloud_dashboard, analytics, logger"
echo ""
echo "🖥️  Interactive Dashboards:"
echo "  docker exec -it hmi1 python main.py"
echo "  docker exec -it hmi2 python main.py"
echo "  docker exec -it cloud_dashboard python main.py"
echo ""
echo "🛑 Stop Demo:"
echo "  ./stop_demo.sh"
echo ""
echo "=========================================="
