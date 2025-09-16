#!/usr/bin/env python3
"""
HMI1 - Manufacturing Line Human Machine Interface
Subscribes to topic1 (factory/line1) and displays production data
"""
import paho.mqtt.client as mqtt
import json
import time
import threading
import os
from datetime import datetime

# Configuration
BROKER = os.getenv("BROKER", "localhost")
PORT = int(os.getenv("PORT", "1883"))
CLIENT_ID = "HMI1"
SUBSCRIBE_TOPIC = "factory/line1"

class HMI1Dashboard:
    def __init__(self):
        self.client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Display state
        self.connected = False
        self.last_data = None
        self.message_count = 0
        self.alarms = []
        self.production_history = []
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connected to broker")
            client.subscribe(SUBSCRIBE_TOPIC, qos=1)
            client.publish(f"status/{CLIENT_ID}", "online", retain=True)
            print(f"[{CLIENT_ID}] Subscribed to: {SUBSCRIBE_TOPIC}")
            self.connected = True
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connection failed: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Disconnected")
        self.connected = False
    
    def on_message(self, client, userdata, msg):
        try:
            self.message_count += 1
            payload = msg.payload.decode()
            data = json.loads(payload)
            self.last_data = data
            
            # Track production history
            if len(self.production_history) > 20:
                self.production_history.pop(0)
            self.production_history.append({
                'timestamp': data.get('timestamp'),
                'production_count': data.get('production_count', 0),
                'line_speed': data.get('line_speed', 0)
            })
            
            # Handle alarms
            if data.get('alarm', False) and data.get('status') == 'alarm':
                alarm_msg = f"ALARM: Line {data.get('plc_id', 'Unknown')} - Production issue detected"
                if alarm_msg not in [a['message'] for a in self.alarms]:
                    self.alarms.append({
                        'timestamp': datetime.now().isoformat(),
                        'message': alarm_msg,
                        'severity': 'HIGH'
                    })
            
            # Keep only recent alarms
            if len(self.alarms) > 10:
                self.alarms.pop(0)
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Received production data")
            
        except json.JSONDecodeError as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] JSON decode error: {e}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error processing message: {e}")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_dashboard(self):
        """Display the HMI dashboard"""
        while True:
            try:
                self.clear_screen()
                
                # Header
                print("="*80)
                print(f"  HMI1 - MANUFACTURING LINE CONTROL DASHBOARD")
                print(f"  Connection: {'ONLINE' if self.connected else 'OFFLINE'} | Messages: {self.message_count}")
                print(f"  Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*80)
                
                if self.last_data:
                    # Current Status
                    status = self.last_data.get('status', 'unknown').upper()
                    status_color = "🟢" if status == "RUNNING" else "🔴" if status == "ALARM" else "🟡"
                    
                    print(f"\n📊 CURRENT PRODUCTION STATUS: {status_color} {status}")
                    print(f"   Production Count: {self.last_data.get('production_count', 'N/A'):,} units")
                    print(f"   Line Speed:       {self.last_data.get('line_speed', 'N/A')} items/min")
                    print(f"   Quality Rate:     {self.last_data.get('quality_rate', 'N/A')}%")
                    
                    print(f"\n🌡️  ENVIRONMENTAL CONDITIONS:")
                    print(f"   Temperature:      {self.last_data.get('temperature', 'N/A')}°C")
                    print(f"   Pressure:         {self.last_data.get('pressure', 'N/A')} bar")
                    print(f"   Vibration:        {self.last_data.get('vibration', 'N/A')} mm/s")
                    
                    # Production Trend
                    if len(self.production_history) > 1:
                        recent = self.production_history[-5:]  # Last 5 readings
                        speeds = [h['line_speed'] for h in recent if h['line_speed']]
                        if speeds:
                            avg_speed = sum(speeds) / len(speeds)
                            trend = "📈 INCREASING" if speeds[-1] > avg_speed else "📉 DECREASING" if speeds[-1] < avg_speed else "➡️ STABLE"
                            print(f"\n📈 PRODUCTION TREND: {trend}")
                            print(f"   Average Speed (last 5): {avg_speed:.1f} items/min")
                
                else:
                    print(f"\n⏳ Waiting for data from {SUBSCRIBE_TOPIC}...")
                
                # Active Alarms
                if self.alarms:
                    print(f"\n🚨 ACTIVE ALARMS ({len(self.alarms)}):")
                    for alarm in self.alarms[-5:]:  # Show last 5 alarms
                        timestamp = alarm['timestamp'][:19]  # Remove microseconds
                        print(f"   [{timestamp}] {alarm['message']}")
                else:
                    print(f"\n✅ NO ACTIVE ALARMS")
                
                # Footer
                print("\n" + "="*80)
                print("  Press Ctrl+C to exit")
                print("="*80)
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Display error: {e}")
                time.sleep(2)
    
    def start(self):
        """Start the HMI dashboard"""
        try:
            # Set will message for clean disconnect detection
            self.client.will_set(f"status/{CLIENT_ID}", "offline", retain=True)
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connecting to {BROKER}:{PORT}")
            self.client.connect(BROKER, PORT, 60)
            
            # Start MQTT loop in background
            self.client.loop_start()
            
            # Start dashboard display
            self.display_dashboard()
            
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Shutting down...")
            self.client.publish(f"status/{CLIENT_ID}", "offline", retain=True)
            self.client.disconnect()
            self.client.loop_stop()

if __name__ == "__main__":
    hmi = HMI1Dashboard()
    hmi.start()
