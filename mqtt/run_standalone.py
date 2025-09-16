#!/usr/bin/env python3
"""
Standalone MQTT Demo Runner
Run the complete MQTT demo without Docker for development/testing
"""
import subprocess
import time
import threading
import signal
import sys
import os

# Configuration
COMPONENTS = [
    {"name": "Local Broker", "cmd": ["mosquitto", "-c", "config/mosquitto.conf"], "delay": 2},
    {"name": "Cloud Broker", "cmd": ["mosquitto", "-c", "config/cloud_mosquitto.conf"], "delay": 2},
    {"name": "PLC1", "cmd": ["python", "plc1.py"], "delay": 3},
    {"name": "PLC2", "cmd": ["python", "plc2.py"], "delay": 3},
    {"name": "PLC3", "cmd": ["python", "plc3.py"], "delay": 3},
    {"name": "Historian", "cmd": ["python", "historian.py"], "delay": 5},
    {"name": "Bridge", "cmd": ["python", "bridge.py"], "delay": 7},
]

class DemoRunner:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_component(self, component):
        """Start a single component"""
        try:
            print(f"🚀 Starting {component['name']}...")
            
            # Set environment variables for Python processes
            env = os.environ.copy()
            if component['name'] not in ['Local Broker', 'Cloud Broker']:
                env['BROKER'] = 'localhost'
                env['PORT'] = '1883'
                if component['name'] == 'Bridge':
                    env['CLOUD_BROKER'] = 'localhost'
                    env['CLOUD_PORT'] = '1884'
            
            process = subprocess.Popen(
                component['cmd'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes.append({
                'name': component['name'],
                'process': process,
                'cmd': component['cmd']
            })
            
            print(f"✅ {component['name']} started (PID: {process.pid})")
            return process
            
        except Exception as e:
            print(f"❌ Failed to start {component['name']}: {e}")
            return None
    
    def monitor_process(self, proc_info):
        """Monitor a process and print its output"""
        process = proc_info['process']
        name = proc_info['name']
        
        try:
            while self.running and process.poll() is None:
                output = process.stdout.readline()
                if output:
                    print(f"[{name}] {output.strip()}")
                time.sleep(0.1)
                
        except Exception as e:
            if self.running:
                print(f"❌ Error monitoring {name}: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.shutdown()
        sys.exit(0)
    
    def shutdown(self):
        """Shutdown all processes"""
        self.running = False
        
        print("\n🛑 Shutting down all components...")
        for proc_info in reversed(self.processes):
            try:
                process = proc_info['process']
                name = proc_info['name']
                
                if process.poll() is None:
                    print(f"🛑 Stopping {name}...")
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                        print(f"✅ {name} stopped gracefully")
                    except subprocess.TimeoutExpired:
                        print(f"⚠️  Force killing {name}...")
                        process.kill()
                        process.wait()
                        print(f"💀 {name} force killed")
                        
            except Exception as e:
                print(f"❌ Error stopping {proc_info['name']}: {e}")
        
        print("✅ All components stopped")
    
    def check_dependencies(self):
        """Check if required dependencies are available"""
        print("🔍 Checking dependencies...")
        
        # Check for mosquitto
        try:
            result = subprocess.run(['mosquitto', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Mosquitto MQTT broker found")
            else:
                print("❌ Mosquitto not working properly")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Mosquitto MQTT broker not found")
            print("   Please install: apt-get install mosquitto (Linux) or brew install mosquitto (macOS)")
            return False
        
        # Check for Python and required modules
        try:
            import paho.mqtt.client
            print("✅ paho-mqtt found")
        except ImportError:
            print("❌ paho-mqtt not found. Install with: pip install paho-mqtt")
            return False
        
        # Check if config files exist
        if not os.path.exists('config/mosquitto.conf'):
            print("❌ config/mosquitto.conf not found")
            return False
        
        if not os.path.exists('config/cloud_mosquitto.conf'):
            print("❌ config/cloud_mosquitto.conf not found")
            return False
        
        print("✅ All dependencies satisfied")
        return True
    
    def run(self):
        """Run the complete demo"""
        print("="*60)
        print("  MQTT Industrial IoT Demo - Standalone Mode")
        print("="*60)
        
        # Check dependencies
        if not self.check_dependencies():
            print("\n❌ Dependency check failed. Please install missing components.")
            return
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Start components with delays
            for component in COMPONENTS:
                if not self.running:
                    break
                    
                self.start_component(component)
                
                if component['delay'] > 0:
                    print(f"⏳ Waiting {component['delay']} seconds...")
                    time.sleep(component['delay'])
            
            print("\n" + "="*60)
            print("🎉 All components started successfully!")
            print("="*60)
            print("\n📊 Demo Status:")
            for proc_info in self.processes:
                status = "🟢 Running" if proc_info['process'].poll() is None else "🔴 Stopped"
                print(f"  {proc_info['name']}: {status}")
            
            print(f"\n🏭 MQTT Topics:")
            print(f"  • factory/line1 (PLC1 → HMI1)")
            print(f"  • factory/energy (PLC2 → HMI2)")
            print(f"  • factory/environment (PLC3)")
            print(f"  • cloud/factory/analytics (Bridge → Cloud)")
            
            print(f"\n🔍 View Real-time Data:")
            print(f"  mosquitto_sub -h localhost -p 1883 -t 'factory/#'")
            print(f"  mosquitto_sub -h localhost -p 1884 -t 'cloud/#'")
            
            print(f"\n🖥️  Interactive Dashboards:")
            print(f"  python hmi1.py")
            print(f"  python hmi2.py")
            print(f"  python cloud_dashboard.py")
            
            print(f"\n🛑 Stop Demo: Ctrl+C")
            print("="*60)
            
            # Start monitoring threads
            monitor_threads = []
            for proc_info in self.processes:
                thread = threading.Thread(target=self.monitor_process, args=(proc_info,), daemon=True)
                thread.start()
                monitor_threads.append(thread)
            
            # Keep main thread alive
            while self.running:
                time.sleep(1)
                
                # Check if any critical process died
                for proc_info in self.processes[:2]:  # Check brokers
                    if proc_info['process'].poll() is not None:
                        print(f"💀 Critical component {proc_info['name']} died, shutting down...")
                        self.shutdown()
                        return
            
        except KeyboardInterrupt:
            print(f"\n🛑 Interrupted by user")
            self.shutdown()
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            self.shutdown()

if __name__ == "__main__":
    runner = DemoRunner()
    runner.run()
