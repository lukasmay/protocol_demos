#!/usr/bin/env python3
"""
HMI2 - Energy Management Human Machine Interface
Subscribes to topic2 (factory/energy) and displays energy data
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
CLIENT_ID = "HMI2"
SUBSCRIBE_TOPIC = "factory/energy"

class HMI2Dashboard:
    def __init__(self):
        self.client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Display state
        self.connected = False
        self.last_data = None
        self.message_count = 0
        self.alerts = []
        self.power_history = []
        
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
            
            # Track power consumption history
            if len(self.power_history) > 20:
                self.power_history.pop(0)
            self.power_history.append({
                'timestamp': data.get('timestamp'),
                'power_consumption': data.get('power_consumption', 0),
                'power_factor': data.get('power_factor', 0)
            })
            
            # Handle energy alerts
            power = data.get('power_consumption', 0)
            power_factor = data.get('power_factor', 1)
            grid_status = data.get('grid_status', 'normal')
            
            # High power consumption alert
            if power > 300:
                alert_msg = f"HIGH POWER CONSUMPTION: {power:.1f} kW"
                if alert_msg not in [a['message'] for a in self.alerts]:
                    self.alerts.append({
                        'timestamp': datetime.now().isoformat(),
                        'message': alert_msg,
                        'severity': 'MEDIUM'
                    })
            
            # Low power factor alert
            if power_factor < 0.8:
                alert_msg = f"LOW POWER FACTOR: {power_factor:.3f}"
                if alert_msg not in [a['message'] for a in self.alerts]:
                    self.alerts.append({
                        'timestamp': datetime.now().isoformat(),
                        'message': alert_msg,
                        'severity': 'LOW'
                    })
            
            # Grid status alert
            if grid_status != 'normal':
                alert_msg = f"GRID STATUS: {grid_status.upper()}"
                if alert_msg not in [a['message'] for a in self.alerts]:
                    self.alerts.append({
                        'timestamp': datetime.now().isoformat(),
                        'message': alert_msg,
                        'severity': 'HIGH'
                    })
            
            # Keep only recent alerts
            if len(self.alerts) > 10:
                self.alerts.pop(0)
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Received energy data")
            
        except json.JSONDecodeError as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] JSON decode error: {e}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error processing message: {e}")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_power_status_icon(self, power):
        """Get status icon based on power consumption"""
        if power < 200:
            return "🟢"  # Low consumption
        elif power < 280:
            return "🟡"  # Normal consumption
        else:
            return "🔴"  # High consumption
    
    def display_dashboard(self):
        """Display the HMI dashboard"""
        while True:
            try:
                self.clear_screen()
                
                # Header
                print("="*80)
                print(f"  HMI2 - ENERGY MANAGEMENT DASHBOARD")
                print(f"  Connection: {'ONLINE' if self.connected else 'OFFLINE'} | Messages: {self.message_count}")
                print(f"  Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*80)
                
                if self.last_data:
                    # Current Power Status
                    power = self.last_data.get('power_consumption', 0)
                    power_icon = self.get_power_status_icon(power)
                    
                    print(f"\n⚡ POWER CONSUMPTION: {power_icon} {power:.1f} kW")
                    print(f"   Total Energy:     {self.last_data.get('energy_total', 'N/A'):,.1f} kWh")
                    print(f"   Peak Demand:      {self.last_data.get('demand_peak', 'N/A'):.1f} kW")
                    print(f"   Efficiency:       {self.last_data.get('efficiency', 'N/A'):.1f}%")
                    
                    # Electrical Parameters
                    voltages = self.last_data.get('voltages', {})
                    currents = self.last_data.get('currents', {})
                    
                    print(f"\n🔌 ELECTRICAL PARAMETERS:")
                    print(f"   Voltages (L1/L2/L3): {voltages.get('L1', 'N/A')}V / {voltages.get('L2', 'N/A')}V / {voltages.get('L3', 'N/A')}V")
                    print(f"   Currents (L1/L2/L3): {currents.get('L1', 'N/A')}A / {currents.get('L2', 'N/A')}A / {currents.get('L3', 'N/A')}A")
                    print(f"   Power Factor:        {self.last_data.get('power_factor', 'N/A'):.3f}")
                    print(f"   Frequency:           {self.last_data.get('frequency', 'N/A'):.2f} Hz")
                    
                    # Grid Status
                    grid_status = self.last_data.get('grid_status', 'unknown').upper()
                    grid_icon = "🟢" if grid_status == "NORMAL" else "🟡" if grid_status in ["HIGH_DEMAND", "VOLTAGE_SAG"] else "🔴"
                    print(f"\n🏭 GRID STATUS: {grid_icon} {grid_status}")
                    
                    # Power Trend
                    if len(self.power_history) > 1:
                        recent = self.power_history[-5:]  # Last 5 readings
                        powers = [h['power_consumption'] for h in recent if h['power_consumption']]
                        if powers:
                            avg_power = sum(powers) / len(powers)
                            trend = "📈 INCREASING" if powers[-1] > avg_power else "📉 DECREASING" if powers[-1] < avg_power else "➡️ STABLE"
                            print(f"\n📊 POWER TREND: {trend}")
                            print(f"   Average Power (last 5): {avg_power:.1f} kW")
                            
                            # Cost estimation (example: $0.12/kWh)
                            daily_cost = (avg_power * 24 * 0.12)
                            print(f"   Estimated Daily Cost: ${daily_cost:.2f}")
                
                else:
                    print(f"\n⏳ Waiting for data from {SUBSCRIBE_TOPIC}...")
                
                # Active Alerts
                if self.alerts:
                    print(f"\n⚠️  ACTIVE ALERTS ({len(self.alerts)}):")
                    for alert in self.alerts[-5:]:  # Show last 5 alerts
                        timestamp = alert['timestamp'][:19]  # Remove microseconds
                        severity_icon = "🔴" if alert['severity'] == 'HIGH' else "🟡" if alert['severity'] == 'MEDIUM' else "🔵"
                        print(f"   [{timestamp}] {severity_icon} {alert['message']}")
                else:
                    print(f"\n✅ NO ACTIVE ALERTS")
                
                # Energy Efficiency Tips
                if self.last_data:
                    pf = self.last_data.get('power_factor', 1)
                    if pf < 0.85:
                        print(f"\n💡 EFFICIENCY TIP: Consider power factor correction (current PF: {pf:.3f})")
                
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
    hmi = HMI2Dashboard()
    hmi.start()
