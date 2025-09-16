# Modbus RTU (Serial Connection) Demo

1. Install the latest release from (Virtual Serial Ports Emulator (VSPE))[https://eterlogic.com/Products.VSPE_Download.html] to emulate ports used for the demo. 

2. Install Modbus Poll and Modbus Slave from (Modbus Tools)[https://www.modbustools.com/]. 

3. From the Modbus Poll application, connect to the Virtual Port you setup from VSPE. Choose 19200 Baud and set the `Delay between Polls` to 1000 ms.

4. From the Modbus Slave application, connect to the same Virtual Port as the Modbus Poll.

5. Try writing to registers from the Modbus Slave.