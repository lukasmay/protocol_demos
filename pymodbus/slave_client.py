#!/usr/bin/env python3
"""
Modbus Slave Client Demo

This simulates a single Modbus slave device that:
- Connects to the Modbus server
- Only responds when addressed directly
- Shows the passive nature of Modbus slaves

Usage: python slave_client.py <slave_id> <name>
Example: python slave_client.py 2 "Temperature Sensor"
"""

import asyncio
import sys
from pymodbus.client import AsyncModbusTcpClient

async def run_slave(slave_id, name):
    """Run a Modbus slave client"""
    
    print(f"=== Modbus Slave: {name} (ID={slave_id}) ===\n")
    
    client = AsyncModbusTcpClient("127.0.0.1", port=5020)
    await client.connect()
    
    print(f"{name} connected to Modbus server")
    print(f"Slave ID: {slave_id}")
    print(f"Status: Passive - only responds when addressed directly\n")
    
    try:
        # Demonstrate that this slave can read from itself when addressed
        print("Testing self-communication...")
        rr = await client.read_holding_registers(0, count=4, device_id=slave_id)
        if not rr.isError():
            print(f"✓ {name} can read its own registers: HR[0-3]={rr.registers}")
        else:
            print(f"✗ {name} read error: {rr}")
        
        # Wait for a moment to show the slave is running
        print(f"\n{name} is running and waiting for master requests...")
        print("(Press Ctrl+C to stop)")
        
        # Keep the slave running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{name} shutting down...")
    finally:
        client.close()
        print(f"{name} disconnected")

def main():
    if len(sys.argv) != 3:
        print("Usage: python slave_client.py <slave_id> <name>")
        print("Example: python slave_client.py 2 'Temperature Sensor'")
        sys.exit(1)
    
    slave_id = int(sys.argv[1])
    name = sys.argv[2]
    
    if slave_id < 1 or slave_id > 247:
        print("Error: Slave ID must be between 1 and 247")
        sys.exit(1)
    
    asyncio.run(run_slave(slave_id, name))

if __name__ == "__main__":
    main()
