#!/usr/bin/env python3
import logging
import paho.mqtt.client as mqtt
from datetime import datetime
import threading
import time
import os

# ——— MQTT Configuration ———
BROKER = os.getenv("BROKER", "mqtt_local_broker")
PORT = int(os.getenv("PORT", "1883"))
TOPIC = "#"  # Subscribe to everything
TABLE_PRINT_INTERVAL = 30  # seconds (can be adjusted)

# Component tracking for MQTT demo
EXPECTED_COMPONENTS = ["PLC1", "PLC2", "PLC3", "HMI1", "HMI2", "Historian", "Bridge", "CloudDashboard", "Analytics"]


# ——— Global dictionaries ———
clients = {}  # { client_id: {'subs': [topics], 'status': 'online/offline'} }

# ——— Setup logging ———
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ——— Track component activity ———
def track_component_activity():
    """Monitor component activity and connection status"""
    while True:
        try:
            time.sleep(10)
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Check for expected components
            online_components = [cid for cid, info in clients.items() if info.get('status') == 'online']
            offline_components = [cid for cid in EXPECTED_COMPONENTS if cid not in online_components]
            
            if offline_components:
                print(f"[{now}] [LOGGER-STATUS] Offline components: {', '.join(offline_components)}")
            
            # Log activity summary
            total_messages = sum(info.get('message_count', 0) for info in clients.values())
            print(f"[{now}] [LOGGER-SUMMARY] Online: {len(online_components)}, Total messages: {total_messages}")
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [LOGGER-ERROR] Activity tracking error: {e}")
            time.sleep(5)

# ——— MQTT Traffic Listener ———
def mqtt_traffic_listener():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"[Logger] Connected to {BROKER}:{PORT}")
            client.subscribe(TOPIC)
            print(f"[Logger] Subscribed to {TOPIC}")
        else:
            print(f"[Logger] Connect failed, rc={rc}")

    def on_message(client, userdata, msg):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        topic = msg.topic
        payload = msg.payload.decode()

        # Track message count
        clients.setdefault("global", {'message_count': 0})
        clients["global"]['message_count'] = clients["global"].get('message_count', 0) + 1
        
        # Detect CONNECT/DISCONNECT based on status topics
        if topic.startswith("status/"):
            client_id = topic.split("/")[1]
            clients.setdefault(client_id, {'subs': [], 'status': 'unknown', 'message_count': 0})
            
            if payload == "online":
                clients[client_id]['status'] = 'online'
                print(f"[{now}] [CONNECT] {client_id} connected")
            elif payload == "offline":
                clients[client_id]['status'] = 'offline'
                print(f"[{now}] [DISCONNECT] {client_id} disconnected")
            else:
                print(f"[{now}] [STATUS] {client_id} → {payload}")
        
        # Track data messages by topic
        elif topic.startswith("factory/") or topic.startswith("cloud/"):
            # Count messages per topic
            topic_key = f"topic_{topic.replace('/', '_')}"
            clients.setdefault(topic_key, {'message_count': 0})
            clients[topic_key]['message_count'] = clients[topic_key].get('message_count', 0) + 1
            
            # Show data message with size info
            payload_size = len(payload)
            print(f"[{now}] [DATA] {topic} → {payload_size} bytes")
            
            # Show actual content for small messages or first few chars for large ones
            if payload_size < 200:
                print(f"[{now}] [CONTENT] {payload}")
            else:
                print(f"[{now}] [CONTENT] {payload[:100]}... [truncated]")
        
        # Other messages
        else:
            print(f"[{now}] [MSG] {topic} → {payload}")

    # Setup MQTT client
    client = mqtt.Client(client_id="logger", protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=30)  # Reduced keepalive for faster detection
    client.loop_forever()

# ——— Periodic System Status Report ———
def print_system_status():
    while True:
        time.sleep(TABLE_PRINT_INTERVAL)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*80}")
        print(f"[{now}] MQTT DEMO SYSTEM STATUS")
        print(f"{'='*80}")
        
        # Component status
        online_components = []
        offline_components = []
        
        for client_id, info in clients.items():
            if client_id.startswith("topic_") or client_id == "global":
                continue
                
            status = info.get('status', 'unknown')
            if status == 'online':
                online_components.append(client_id)
            else:
                offline_components.append(client_id)
        
        print(f"🟢 ONLINE COMPONENTS ({len(online_components)}):")
        for comp in online_components:
            msg_count = clients[comp].get('message_count', 0)
            print(f"   • {comp} ({msg_count} messages)")
        
        if offline_components:
            print(f"\n🔴 OFFLINE COMPONENTS ({len(offline_components)}):")
            for comp in offline_components:
                print(f"   • {comp}")
        
        # Topic statistics
        print(f"\n📊 TOPIC ACTIVITY:")
        topic_stats = [(k, v) for k, v in clients.items() if k.startswith("topic_")]
        if topic_stats:
            for topic_key, info in sorted(topic_stats):
                topic_name = topic_key.replace("topic_", "").replace("_", "/")
                msg_count = info.get('message_count', 0)
                print(f"   • {topic_name}: {msg_count} messages")
        else:
            print("   • No topic activity detected yet")
        
        # Global statistics
        global_msgs = clients.get("global", {}).get('message_count', 0)
        print(f"\n📈 TOTAL MESSAGES: {global_msgs}")
        print(f"{'='*80}\n")

# ——— Main ———
if __name__ == "__main__":
    print(f"{'='*80}")
    print(f"  MQTT DEMO LOGGER STARTING")
    print(f"  Broker: {BROKER}:{PORT}")
    print(f"  Monitoring all topics (#)")
    print(f"{'='*80}")
    
    # Start component activity tracking
    threading.Thread(target=track_component_activity, daemon=True).start()

    # Start MQTT traffic listener in parallel
    threading.Thread(target=mqtt_traffic_listener, daemon=True).start()

    # Start periodic system status printer
    print_system_status()
