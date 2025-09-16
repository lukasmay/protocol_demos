#!/usr/bin/env python3
"""
Cloud Dashboard - Factory Analytics Dashboard
Subscribes to topic 4 (cloud/factory/analytics) and displays aggregated data
"""
import paho.mqtt.client as mqtt
import json
import time
import threading
import os
from datetime import datetime

# Configuration
BROKER = os.getenv("BROKER", "localhost")
PORT = int(os.getenv("PORT", "1884"))  # Cloud broker port
CLIENT_ID = "CloudDashboard"
SUBSCRIBE_TOPIC = "cloud/factory/analytics"

class CloudDashboard:
    def __init__(self):
        self.client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Dashboard state
        self.connected = False
        self.last_analytics = None
        self.message_count = 0
        self.alerts_history = []
        self.facility_metrics = []
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connected to cloud broker")
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
            self.last_analytics = data
            
            # Track facility metrics
            facility_status = data.get('facility_status', {})
            if len(self.facility_metrics) > 50:
                self.facility_metrics.pop(0)
            self.facility_metrics.append({
                'timestamp': data.get('timestamp'),
                'energy_efficiency': facility_status.get('energy_efficiency', 0),
                'environmental_comfort': facility_status.get('environmental_comfort', 0),
                'overall_health': facility_status.get('overall_health', False)
            })
            
            # Track critical alerts
            alerts = data.get('critical_alerts', [])
            for alert in alerts:
                alert['received_at'] = datetime.now().isoformat()
                self.alerts_history.append(alert)
            
            # Keep only recent alerts
            if len(self.alerts_history) > 100:
                self.alerts_history = self.alerts_history[-100:]
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Received analytics data")
            
        except json.JSONDecodeError as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] JSON decode error: {e}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error processing message: {e}")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_health_status_icon(self, health):
        """Get health status icon"""
        return "🟢" if health else "🔴"
    
    def get_trend_icon(self, trend):
        """Get trend icon"""
        if trend == 'increasing':
            return "📈"
        elif trend == 'decreasing':
            return "📉"
        else:
            return "➡️"
    
    def display_dashboard(self):
        """Display the cloud dashboard"""
        while True:
            try:
                self.clear_screen()
                
                # Header
                print("="*100)
                print(f"  ☁️  CLOUD FACTORY ANALYTICS DASHBOARD")
                print(f"  Connection: {'ONLINE' if self.connected else 'OFFLINE'} | Analytics Reports: {self.message_count}")
                print(f"  Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*100)
                
                if self.last_analytics:
                    data_points = self.last_analytics.get('data_points', {})
                    energy_analytics = self.last_analytics.get('energy_analytics', {})
                    env_analytics = self.last_analytics.get('environment_analytics', {})
                    facility_status = self.last_analytics.get('facility_status', {})
                    alerts = self.last_analytics.get('critical_alerts', [])
                    
                    # Facility Overview
                    overall_health = facility_status.get('overall_health', False)
                    health_icon = self.get_health_status_icon(overall_health)
                    
                    print(f"\n🏭 FACILITY STATUS: {health_icon} {'HEALTHY' if overall_health else 'ATTENTION REQUIRED'}")
                    print(f"   Energy Efficiency:      {facility_status.get('energy_efficiency', 0):.1f}%")
                    print(f"   Environmental Comfort:  {facility_status.get('environmental_comfort', 0):.1f}%")
                    print(f"   Data Samples:           Energy: {data_points.get('energy_samples', 0)}, Environment: {data_points.get('environment_samples', 0)}")
                    
                    # Energy Analytics
                    if energy_analytics:
                        power_data = energy_analytics.get('power_consumption', {})
                        power_trend = self.get_trend_icon(power_data.get('trend', 'stable'))
                        
                        print(f"\n⚡ ENERGY ANALYTICS:")
                        print(f"   Power Consumption:      {power_data.get('average', 0):.1f} kW (avg) {power_trend} {power_data.get('trend', 'stable')}")
                        print(f"   Range:                  {power_data.get('min', 0):.1f} - {power_data.get('max', 0):.1f} kW")
                        print(f"   Power Factor:           {energy_analytics.get('power_factor', {}).get('average', 0):.3f} (avg)")
                        print(f"   System Efficiency:      {energy_analytics.get('efficiency', {}).get('average', 0):.1f}%")
                        print(f"   Grid Stability:         {energy_analytics.get('grid_stability', 0):.1f}%")
                        print(f"   Total Energy:           {energy_analytics.get('energy_total', 0):,.1f} kWh")
                    
                    # Environment Analytics
                    if env_analytics:
                        temp_data = env_analytics.get('temperature', {})
                        temp_trend = self.get_trend_icon(temp_data.get('trend', 'stable'))
                        co2_data = env_analytics.get('co2_level', {})
                        co2_trend = self.get_trend_icon(co2_data.get('trend', 'stable'))
                        
                        print(f"\n🌡️  ENVIRONMENTAL ANALYTICS:")
                        print(f"   Temperature:            {temp_data.get('average', 0):.1f}°C (avg) {temp_trend} {temp_data.get('trend', 'stable')}")
                        print(f"   Range:                  {temp_data.get('min', 0):.1f} - {temp_data.get('max', 0):.1f}°C")
                        print(f"   Humidity:               {env_analytics.get('humidity', {}).get('average', 0):.1f}% (avg)")
                        print(f"   CO2 Level:              {co2_data.get('average', 0):.1f} ppm (avg) {co2_trend} {co2_data.get('trend', 'stable')}")
                        print(f"   Air Quality Index:      {env_analytics.get('air_quality', {}).get('average_index', 0):.1f}")
                        print(f"   Comfort Index:          {env_analytics.get('comfort_index', {}).get('average', 0):.1f}%")
                    
                    # Critical Alerts
                    if alerts:
                        print(f"\n🚨 CRITICAL ALERTS ({len(alerts)}):")
                        for alert in alerts:
                            severity_icon = "🔴" if alert['severity'] == 'high' else "🟡" if alert['severity'] == 'medium' else "🔵"
                            print(f"   {severity_icon} [{alert['type'].upper()}] {alert['message']}")
                    else:
                        print(f"\n✅ NO CRITICAL ALERTS")
                    
                    # Performance Trends
                    if len(self.facility_metrics) > 1:
                        recent_metrics = self.facility_metrics[-10:]  # Last 10 readings
                        avg_efficiency = sum(m['energy_efficiency'] for m in recent_metrics) / len(recent_metrics)
                        avg_comfort = sum(m['environmental_comfort'] for m in recent_metrics) / len(recent_metrics)
                        health_rate = sum(1 for m in recent_metrics if m['overall_health']) / len(recent_metrics) * 100
                        
                        print(f"\n📊 PERFORMANCE TRENDS (Last 10 Reports):")
                        print(f"   Average Energy Efficiency:  {avg_efficiency:.1f}%")
                        print(f"   Average Environmental Comfort: {avg_comfort:.1f}%")
                        print(f"   System Health Rate:         {health_rate:.1f}%")
                    
                    # Recent Alert Summary
                    recent_alerts = [a for a in self.alerts_history[-20:] if a]  # Last 20 alerts
                    if recent_alerts:
                        high_alerts = len([a for a in recent_alerts if a['severity'] == 'high'])
                        medium_alerts = len([a for a in recent_alerts if a['severity'] == 'medium'])
                        print(f"\n📋 RECENT ALERT SUMMARY (Last 20):")
                        print(f"   High Priority:          {high_alerts}")
                        print(f"   Medium Priority:        {medium_alerts}")
                        print(f"   Low Priority:           {len(recent_alerts) - high_alerts - medium_alerts}")
                
                else:
                    print(f"\n⏳ Waiting for analytics data from {SUBSCRIBE_TOPIC}...")
                
                # Footer with recommendations
                if self.last_analytics:
                    print(f"\n💡 RECOMMENDATIONS:")
                    facility_status = self.last_analytics.get('facility_status', {})
                    energy_analytics = self.last_analytics.get('energy_analytics', {})
                    env_analytics = self.last_analytics.get('environment_analytics', {})
                    
                    if facility_status.get('energy_efficiency', 0) < 80:
                        print(f"   • Consider energy optimization measures")
                    if facility_status.get('environmental_comfort', 0) < 70:
                        print(f"   • Review HVAC settings for better comfort")
                    if energy_analytics and energy_analytics.get('power_factor', {}).get('average', 1) < 0.85:
                        print(f"   • Install power factor correction equipment")
                    if env_analytics and env_analytics.get('co2_level', {}).get('average', 0) > 800:
                        print(f"   • Increase ventilation to reduce CO2 levels")
                    
                    if facility_status.get('overall_health', True) and facility_status.get('energy_efficiency', 0) > 85:
                        print(f"   ✅ Facility operating optimally")
                
                print("\n" + "="*100)
                print("  Press Ctrl+C to exit")
                print("="*100)
                
                time.sleep(3)  # Update every 3 seconds
                
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Display error: {e}")
                time.sleep(3)
    
    def start(self):
        """Start the cloud dashboard"""
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
    dashboard = CloudDashboard()
    dashboard.start()
