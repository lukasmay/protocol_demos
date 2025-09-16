#!/usr/bin/env python3
"""
Modbus Broadcast Demo

This demo shows how Modbus master-slave communication works:
- Master (client) sends requests to specific slave addresses
- Slaves only respond when their address is specified
- Broadcast messages (address 0) are received by all slaves but they don't respond

Run this demo with:
1. Start the server: python async_tcp_server.py
2. Run this demo: python broadcast_demo.py
"""

import asyncio
from pymodbus.client import AsyncModbusTcpClient

class ModbusSlave:
    """Simulates a Modbus slave device"""
    
    def __init__(self, slave_id, name):
        self.slave_id = slave_id
        self.name = name
        self.client = AsyncModbusTcpClient("127.0.0.1", port=5020)
        self.connected = False
        
    async def connect(self):
        """Connect to the Modbus server"""
        await self.client.connect()
        self.connected = True
        print(f"  {self.name} (ID={self.slave_id}) connected to server")
        
    async def disconnect(self):
        """Disconnect from the server"""
        if self.connected:
            self.client.close()
            self.connected = False
            print(f"  {self.name} (ID={self.slave_id}) disconnected")

async def demo_broadcast_communication():
    """Demonstrate broadcast vs addressed communication"""
    
    print("=== Modbus Broadcast Communication Demo ===\n")
    
    # Create three slave clients
    slave1 = ModbusSlave(1, "Temperature Sensor")
    slave2 = ModbusSlave(2, "Pressure Sensor") 
    slave3 = ModbusSlave(3, "Flow Meter")
    
    # Connect all slaves
    print("1. Connecting slaves to Modbus server...")
    await slave1.connect()
    await slave2.connect()
    await slave3.connect()
    await asyncio.sleep(1)
    
    print("\n2. Testing addressed communication (normal Modbus behavior):")
    print("   - Master sends request to specific slave address")
    print("   - Only the addressed slave responds\n")
    
    # Test reading from each slave individually
    for slave in [slave1, slave2, slave3]:
        print(f"   Reading from {slave.name} (ID={slave.slave_id})...")
        try:
            rr = await slave.client.read_holding_registers(0, count=1, device_id=slave.slave_id)
            if not rr.isError():
                print(f"   ✓ {slave.name} responded: HR[0]={rr.registers[0]}")
            else:
                print(f"   ✗ {slave.name} error: {rr}")
        except Exception as e:
            print(f"   ✗ {slave.name} exception: {e}")
        await asyncio.sleep(0.5)
    
    print("\n3. Testing broadcast communication:")
    print("   - Master sends request to address 0 (broadcast)")
    print("   - All slaves receive the message but NONE respond")
    print("   - This is correct Modbus behavior\n")
    
    # Test broadcast (address 0)
    print("   Sending broadcast read request (address 0)...")
    try:
        # This should work but no slaves will respond to broadcast reads
        rr = await slave1.client.read_holding_registers(0, count=1, device_id=0)
        if not rr.isError():
            print(f"   ✓ Broadcast read successful: HR[0]={rr.registers[0]}")
        else:
            print(f"   ⚠ Broadcast read response: {rr}")
    except Exception as e:
        print(f"   ⚠ Broadcast read exception: {e}")
    
    print("\n4. Demonstrating write operations:")
    print("   - Write to specific slave: Only that slave updates")
    print("   - Write broadcast: All slaves receive but behavior varies\n")
    
    # Write to specific slave
    print("   Writing value 1234 to slave 1 only...")
    await slave1.client.write_register(0, 1234, device_id=1)
    
    # Read from all slaves to see the difference
    for slave in [slave1, slave2, slave3]:
        rr = await slave.client.read_holding_registers(0, count=1, device_id=slave.slave_id)
        if not rr.isError():
            print(f"   {slave.name} HR[0]={rr.registers[0]}")
        await asyncio.sleep(0.2)
    
    print("\n5. Key Modbus Communication Principles:")
    print("   ✓ Slaves are passive - they only respond when addressed")
    print("   ✓ Master controls all communication")
    print("   ✓ Broadcast messages (address 0) are received but not acknowledged")
    print("   ✓ Each slave has a unique address (1-247)")
    print("   ✓ Address 0 is reserved for broadcast")
    
    # Disconnect all slaves
    print("\n6. Disconnecting slaves...")
    await slave1.disconnect()
    await slave2.disconnect()
    await slave3.disconnect()
    
    print("\n=== Demo completed ===")

if __name__ == "__main__":
    asyncio.run(demo_broadcast_communication())
