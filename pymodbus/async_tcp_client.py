import asyncio
from pymodbus.client import AsyncModbusTcpClient

async def main():
    client = AsyncModbusTcpClient("127.0.0.1", port=5020)
    await client.connect()

    print("=== Modbus TCP Client Demo ===")
    
    # Wait a moment for server to be fully ready
    print("Waiting for server to be ready...")
    await asyncio.sleep(1)
    
    # NOTE: Using device_id=1 (slave address)
    print("1. Reading initial holding registers 0-3 from device_id=1...")
    rr = await client.read_holding_registers(0, count=4, device_id=1)
    if not rr.isError():
        print(f"   ✓ Initial values: HR[0]={rr.registers[0]}, HR[1]={rr.registers[1]}, HR[2]={rr.registers[2]}, HR[3]={rr.registers[3]}")
    else:
        print(f"   ⚠ First read failed (server may still be initializing): {rr}")
        print("   Retrying read after brief delay...")
        await asyncio.sleep(1)
        rr = await client.read_holding_registers(0, count=4, device_id=1)
        if not rr.isError():
            print(f"   ✓ Initial values: HR[0]={rr.registers[0]}, HR[1]={rr.registers[1]}, HR[2]={rr.registers[2]}, HR[3]={rr.registers[3]}")
        else:
            print(f"   ⚠ Retry also failed: {rr}")
            print("   (This is expected during server startup - continuing with write/read demo...)")

    print("2. Writing value 9999 to register 0 on device_id=1...")
    await client.write_register(0, 9999, device_id=1)
    print("   ✓ Write operation completed")
    
    print("3. Reading register 0 to verify write...")
    rr2 = await client.read_holding_registers(0, count=1, device_id=1)
    if not rr2.isError():
        print(f"   ✓ New value: HR[0]={rr2.registers[0]}")
        print("   ✓ Write/Read operation successful!")
    else:
        print(f"   ✗ Read failed: {rr2}")

    client.close()
    print("=== Demo completed ===")

if __name__ == "__main__":
    asyncio.run(main())
