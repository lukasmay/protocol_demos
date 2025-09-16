# async_tcp_server_311.py
import asyncio
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusDeviceContext,
    ModbusServerContext,
)
from pymodbus.server import StartAsyncTcpServer  # 3.x entrypoint

async def main():
    print("Starting Modbus TCP Server...")
    
    # Create a simple single device context
    device = ModbusDeviceContext(
        di=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [0]*100),
        hr=ModbusSequentialDataBlock(0, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] + [0]*90),  # holding regs 0..99
        ir=ModbusSequentialDataBlock(0, [100]*100),
    )
    
    # Create server context with device_id=1
    context = ModbusServerContext(devices={1: device}, single=False)
    print("Server context created with single device")
    print("Initial holding registers 0-9: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]")

    # Run server on localhost:5020
    print("Starting server on 127.0.0.1:5020...")
    print("Server is ready and listening for connections...")
    await StartAsyncTcpServer(context, address=("127.0.0.1", 5020))

if __name__ == "__main__":
    asyncio.run(main())
