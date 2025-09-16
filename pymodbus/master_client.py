#!/usr/bin/env python3
"""
Modbus Master Client Demo

This demonstrates a Modbus master that:
- Controls communication with multiple slaves
- Shows how to address specific slaves
- Demonstrates broadcast vs addressed communication

Usage: python master_client.py
"""

import asyncio
from pymodbus.client import AsyncModbusTcpClient

async def run_master():
    """Run a Modbus master client"""
    
    print("=== Modbus Master Client Demo ===\n")
    
    client = AsyncModbusTcpClient("127.0.0.1", port=5020)
    await client.connect()
    
    print("Master connected to Modbus server")
    print("Master controls all communication with slaves\n")
    
    # List of available slaves to test
    slaves = [
        (1, "Device 1"),
        (2, "Device 2"), 
        (3, "Device 3")
    ]
    
    print("1. Testing addressed communication:")
    print("   Master sends requests to specific slave addresses\n")
    
    for slave_id, name in slaves:
        print(f"   Reading from {name} (ID={slave_id})...")
        try:
            rr = await client.read_holding_registers(0, count=2, device_id=slave_id)
            if not rr.isError():
                print(f"   ✓ {name} responded: HR[0]={rr.registers[0]}, HR[1]={rr.registers[1]}")
            else:
                print(f"   ✗ {name} error: {rr}")
        except Exception as e:
            print(f"   ✗ {name} exception: {e}")
        await asyncio.sleep(0.5)
    
    print("\n2. Testing broadcast communication:")
    print("   Master sends request to address 0 (broadcast)")
    print("   Note: Broadcast reads typically don't get responses\n")
    
    try:
        rr = await client.read_holding_registers(0, count=1, device_id=0)
        if not rr.isError():
            print(f"   ✓ Broadcast read response: HR[0]={rr.registers[0]}")
        else:
            print(f"   ⚠ Broadcast read error: {rr}")
    except Exception as e:
        print(f"   ⚠ Broadcast read exception: {e}")
    
    print("\n3. Testing write operations:")
    print("   Master writes to specific slaves\n")
    
    for slave_id, name in slaves:
        test_value = 1000 + slave_id
        print(f"   Writing {test_value} to {name} (ID={slave_id})...")
        await client.write_register(0, test_value, device_id=slave_id)
        print(f"   ✓ Write command sent to {name}")
        
        # Verify the write
        rr = await client.read_holding_registers(0, count=1, device_id=slave_id)
        if not rr.isError():
            print(f"   ✓ Verified: {name} HR[0]={rr.registers[0]}")
        await asyncio.sleep(0.3)
    
    print("\n4. Key Modbus Master Behavior:")
    print("   ✓ Master initiates all communication")
    print("   ✓ Master specifies target slave address in each request")
    print("   ✓ Master can address individual slaves (1-247)")
    print("   ✓ Master can send broadcast messages (address 0)")
    print("   ✓ Only addressed slaves respond to requests")
    
    client.close()
    print("\n=== Master demo completed ===")

if __name__ == "__main__":
    asyncio.run(run_master())
