#!/usr/bin/env python3
"""
MQTT Bridge Client - Cloud Data Aggregator
Subscribes to topics 2 & 3 (energy + environment), combines important data, 
and publishes aggregated data to topic 4 for cloud consumption
"""
import paho.mqtt.client as mqtt
import json
import time
import threading
import os
import statistics
from datetime import datetime

# Configuration
LOCAL_BROKER = os.getenv("LOCAL_BROKER", "localhost")
LOCAL_PORT = int(os.getenv("LOCAL_PORT", "1883"))
CLOUD_BROKER = os.getenv("CLOUD_BROKER", "localhost")  # In real scenario, this would be a cloud broker
CLOUD_PORT = int(os.getenv("CLOUD_PORT", "1884"))  # Different port to simulate cloud broker
CLIENT_ID = "Bridge"
SUBSCRIBE_TOPICS = ["factory/energy", "factory/environment"]
PUBLISH_TOPIC = "cloud/factory/analytics"
AGGREGATION_INTERVAL = 10  # seconds

class MQTTBridge:
    def __init__(self):
        # Local broker client (subscriber)
        self.local_client = mqtt.Client(client_id=f"{CLIENT_ID}_local", protocol=mqtt.MQTTv311)
        self.local_client.on_connect = self.on_local_connect
        self.local_client.on_message = self.on_message
        self.local_client.on_disconnect = self.on_local_disconnect
        
        # Cloud broker client (publisher)
        self.cloud_client = mqtt.Client(client_id=f"{CLIENT_ID}_cloud", protocol=mqtt.MQTTv311)
        self.cloud_client.on_connect = self.on_cloud_connect
        self.cloud_client.on_disconnect = self.on_cloud_disconnect
        
        # Data buffers for aggregation
        self.energy_buffer = []
        self.environment_buffer = []
        self.buffer_lock = threading.Lock()
        
        # Connection status
        self.local_connected = False
        self.cloud_connected = False
        self.message_count = 0
        self.published_count = 0
        
    def on_local_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connected to local broker")
            
            # Subscribe to energy and environment topics
            for topic in SUBSCRIBE_TOPICS:
                client.subscribe(topic, qos=1)
                print(f"[{CLIENT_ID}] Subscribed to: {topic}")
            
            client.publish(f"status/{CLIENT_ID}", "online", retain=True)
            self.local_connected = True
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Local connection failed: {rc}")
    
    def on_cloud_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connected to cloud broker")
            self.cloud_connected = True
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Cloud connection failed: {rc}")
    
    def on_local_disconnect(self, client, userdata, rc):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Disconnected from local broker")
        self.local_connected = False
    
    def on_cloud_disconnect(self, client, userdata, rc):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Disconnected from cloud broker")
        self.cloud_connected = False
    
    def on_message(self, client, userdata, msg):
        try:
            self.message_count += 1
            topic = msg.topic
            payload = msg.payload.decode()
            data = json.loads(payload)
            
            with self.buffer_lock:
                # Buffer data based on topic
                if topic == "factory/energy":
                    self.energy_buffer.append({
                        'timestamp': data.get('timestamp'),
                        'power_consumption': data.get('power_consumption'),
                        'power_factor': data.get('power_factor'),
                        'energy_total': data.get('energy_total'),
                        'grid_status': data.get('grid_status'),
                        'efficiency': data.get('efficiency')
                    })
                    
                    # Keep buffer size manageable
                    if len(self.energy_buffer) > 50:
                        self.energy_buffer.pop(0)
                        
                elif topic == "factory/environment":
                    self.environment_buffer.append({
                        'timestamp': data.get('timestamp'),
                        'temperature': data.get('temperature'),
                        'humidity': data.get('humidity'),
                        'co2_level': data.get('co2_level'),
                        'air_quality': data.get('air_quality', {}),
                        'comfort_index': data.get('comfort_index')
                    })
                    
                    # Keep buffer size manageable
                    if len(self.environment_buffer) > 50:
                        self.environment_buffer.pop(0)
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Buffered data from {topic}")
            
        except json.JSONDecodeError as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] JSON decode error: {e}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error processing message: {e}")
    
    def calculate_energy_analytics(self, energy_data):
        """Calculate energy analytics from buffered data"""
        if not energy_data:
            return None
        
        try:
            power_values = [d['power_consumption'] for d in energy_data if d.get('power_consumption')]
            pf_values = [d['power_factor'] for d in energy_data if d.get('power_factor')]
            efficiency_values = [d['efficiency'] for d in energy_data if d.get('efficiency')]
            
            # Grid status analysis
            grid_statuses = [d['grid_status'] for d in energy_data if d.get('grid_status')]
            normal_status_pct = (grid_statuses.count('normal') / len(grid_statuses) * 100) if grid_statuses else 0
            
            analytics = {
                'power_consumption': {
                    'average': statistics.mean(power_values) if power_values else 0,
                    'min': min(power_values) if power_values else 0,
                    'max': max(power_values) if power_values else 0,
                    'trend': self.calculate_trend(power_values) if len(power_values) > 1 else 'stable'
                },
                'power_factor': {
                    'average': statistics.mean(pf_values) if pf_values else 0,
                    'min': min(pf_values) if pf_values else 0
                },
                'efficiency': {
                    'average': statistics.mean(efficiency_values) if efficiency_values else 0
                },
                'grid_stability': normal_status_pct,
                'energy_total': energy_data[-1].get('energy_total', 0) if energy_data else 0
            }
            
            return analytics
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error calculating energy analytics: {e}")
            return None
    
    def calculate_environment_analytics(self, env_data):
        """Calculate environmental analytics from buffered data"""
        if not env_data:
            return None
        
        try:
            temp_values = [d['temperature'] for d in env_data if d.get('temperature')]
            humidity_values = [d['humidity'] for d in env_data if d.get('humidity')]
            co2_values = [d['co2_level'] for d in env_data if d.get('co2_level')]
            comfort_values = [d['comfort_index'] for d in env_data if d.get('comfort_index')]
            
            # Air quality analysis
            aqi_values = []
            for d in env_data:
                air_quality = d.get('air_quality', {})
                if air_quality.get('index'):
                    aqi_values.append(air_quality['index'])
            
            analytics = {
                'temperature': {
                    'average': statistics.mean(temp_values) if temp_values else 0,
                    'min': min(temp_values) if temp_values else 0,
                    'max': max(temp_values) if temp_values else 0,
                    'trend': self.calculate_trend(temp_values) if len(temp_values) > 1 else 'stable'
                },
                'humidity': {
                    'average': statistics.mean(humidity_values) if humidity_values else 0,
                    'min': min(humidity_values) if humidity_values else 0,
                    'max': max(humidity_values) if humidity_values else 0
                },
                'co2_level': {
                    'average': statistics.mean(co2_values) if co2_values else 0,
                    'max': max(co2_values) if co2_values else 0,
                    'trend': self.calculate_trend(co2_values) if len(co2_values) > 1 else 'stable'
                },
                'air_quality': {
                    'average_index': statistics.mean(aqi_values) if aqi_values else 0,
                    'max_index': max(aqi_values) if aqi_values else 0
                },
                'comfort_index': {
                    'average': statistics.mean(comfort_values) if comfort_values else 0,
                    'min': min(comfort_values) if comfort_values else 0
                }
            }
            
            return analytics
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error calculating environment analytics: {e}")
            return None
    
    def calculate_trend(self, values):
        """Calculate trend direction from a list of values"""
        if len(values) < 2:
            return 'stable'
        
        # Simple trend calculation using first half vs second half
        mid = len(values) // 2
        first_half_avg = statistics.mean(values[:mid])
        second_half_avg = statistics.mean(values[mid:])
        
        diff_pct = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg != 0 else 0
        
        if diff_pct > 5:
            return 'increasing'
        elif diff_pct < -5:
            return 'decreasing'
        else:
            return 'stable'
    
    def generate_critical_alerts(self, energy_analytics, env_analytics):
        """Generate critical alerts based on analytics"""
        alerts = []
        
        if energy_analytics:
            # High power consumption alert
            if energy_analytics['power_consumption']['average'] > 280:
                alerts.append({
                    'type': 'energy',
                    'severity': 'high',
                    'message': f"High average power consumption: {energy_analytics['power_consumption']['average']:.1f} kW"
                })
            
            # Low power factor alert
            if energy_analytics['power_factor']['average'] < 0.8:
                alerts.append({
                    'type': 'energy',
                    'severity': 'medium',
                    'message': f"Low power factor: {energy_analytics['power_factor']['average']:.3f}"
                })
            
            # Grid instability alert
            if energy_analytics['grid_stability'] < 80:
                alerts.append({
                    'type': 'energy',
                    'severity': 'high',
                    'message': f"Grid instability: {energy_analytics['grid_stability']:.1f}% normal status"
                })
        
        if env_analytics:
            # High CO2 alert
            if env_analytics['co2_level']['average'] > 800:
                alerts.append({
                    'type': 'environment',
                    'severity': 'medium',
                    'message': f"High CO2 levels: {env_analytics['co2_level']['average']:.1f} ppm"
                })
            
            # Poor air quality alert
            if env_analytics['air_quality']['average_index'] > 100:
                alerts.append({
                    'type': 'environment',
                    'severity': 'high',
                    'message': f"Poor air quality: AQI {env_analytics['air_quality']['average_index']:.1f}"
                })
            
            # Low comfort index alert
            if env_analytics['comfort_index']['average'] < 70:
                alerts.append({
                    'type': 'environment',
                    'severity': 'low',
                    'message': f"Low comfort index: {env_analytics['comfort_index']['average']:.1f}%"
                })
        
        return alerts
    
    def aggregate_and_publish(self):
        """Aggregate data and publish to cloud topic"""
        while True:
            try:
                time.sleep(AGGREGATION_INTERVAL)
                
                if not self.cloud_connected:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Cloud broker not connected, skipping publish")
                    continue
                
                with self.buffer_lock:
                    # Copy and clear buffers
                    energy_data = self.energy_buffer.copy()
                    env_data = self.environment_buffer.copy()
                    
                    # Keep some data for overlap
                    if len(self.energy_buffer) > 5:
                        self.energy_buffer = self.energy_buffer[-5:]
                    if len(self.environment_buffer) > 5:
                        self.environment_buffer = self.environment_buffer[-5:]
                
                if not energy_data and not env_data:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] No data to aggregate")
                    continue
                
                # Calculate analytics
                energy_analytics = self.calculate_energy_analytics(energy_data)
                env_analytics = self.calculate_environment_analytics(env_data)
                
                # Generate alerts
                alerts = self.generate_critical_alerts(energy_analytics, env_analytics)
                
                # Create aggregated payload
                aggregated_data = {
                    'timestamp': datetime.now().isoformat(),
                    'bridge_id': CLIENT_ID,
                    'aggregation_period': AGGREGATION_INTERVAL,
                    'data_points': {
                        'energy_samples': len(energy_data),
                        'environment_samples': len(env_data)
                    },
                    'energy_analytics': energy_analytics,
                    'environment_analytics': env_analytics,
                    'critical_alerts': alerts,
                    'facility_status': {
                        'energy_efficiency': energy_analytics['efficiency']['average'] if energy_analytics else 0,
                        'environmental_comfort': env_analytics['comfort_index']['average'] if env_analytics else 0,
                        'overall_health': len([a for a in alerts if a['severity'] == 'high']) == 0
                    }
                }
                
                # Publish to cloud
                payload = json.dumps(aggregated_data, indent=2)
                result = self.cloud_client.publish(PUBLISH_TOPIC, payload, qos=1)
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    self.published_count += 1
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Published analytics to cloud "
                          f"(Energy: {len(energy_data)} samples, Env: {len(env_data)} samples, Alerts: {len(alerts)})")
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Failed to publish to cloud")
                
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error in aggregation: {e}")
    
    def start(self):
        """Start the bridge service"""
        try:
            # Set will messages
            self.local_client.will_set(f"status/{CLIENT_ID}", "offline", retain=True)
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connecting to local broker {LOCAL_BROKER}:{LOCAL_PORT}")
            self.local_client.connect(LOCAL_BROKER, LOCAL_PORT, 60)
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connecting to cloud broker {CLOUD_BROKER}:{CLOUD_PORT}")
            self.cloud_client.connect(CLOUD_BROKER, CLOUD_PORT, 60)
            
            # Start MQTT loops
            self.local_client.loop_start()
            self.cloud_client.loop_start()
            
            # Start aggregation thread
            aggregation_thread = threading.Thread(target=self.aggregate_and_publish, daemon=True)
            aggregation_thread.start()
            
            # Keep main thread alive
            while True:
                time.sleep(5)
                if self.message_count > 0 and self.message_count % 20 == 0:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Status: "
                          f"Received {self.message_count}, Published {self.published_count}")
                
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Shutting down...")
            self.local_client.publish(f"status/{CLIENT_ID}", "offline", retain=True)
            self.local_client.disconnect()
            self.cloud_client.disconnect()
            self.local_client.loop_stop()
            self.cloud_client.loop_stop()

if __name__ == "__main__":
    bridge = MQTTBridge()
    bridge.start()
