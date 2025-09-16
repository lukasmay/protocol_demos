# Logger for traffic in the intake enclave

### What you should see:
```sh
[2025-06-01 21:06:25] [INIT] Known Clients & Subscriptions:


- water_level_sensor [online] subscribed to: intake/valve_state


- flow_sensor [online] subscribed to: intake/valve_state


- intake_plc [online] subscribed to: intake/turbidity, intake/valve_state, intake/doser_state, intake/flow, intake/water_level


- chemical_dosing [online] subscribed to: None


- turbidity_sensor [online] subscribed to: None


- intake_valve_actuator [online] subscribed to: None








[2025-06-01 21:06:25] [MODBUS] Registers: Turbidity=11, Flow=0, Valve=Closed, Level=6, Doser=Off


[2025-06-01 21:06:30] [MQTT MSG] intake/water_level → 5.68


[2025-06-01 21:06:30] [MQTT MSG] intake/turbidity → 31.47


[2025-06-01 21:06:30] [MQTT MSG] intake/chemical_doser → dose_off


[2025-06-01 21:06:30] [MQTT MSG] intake/valve_actuator → close


[2025-06-01 21:06:30] [MQTT MSG] intake/flow → 0.0


[2025-06-01 21:06:35] [MQTT MSG] intake/water_level → 4.91


[2025-06-01 21:06:35] [MQTT MSG] intake/turbidity → 51.18


[2025-06-01 21:06:35] [MQTT MSG] intake/valve_actuator → open


[2025-06-01 21:06:35] [MQTT MSG] intake/flow → 0.0




[2025-06-01 21:06:35] [MODBUS] Registers: Turbidity=51, Flow=0, Valve=Closed, Level=4, Doser=Off


[2025-06-01 21:06:40] [MQTT MSG] intake/water_level → 4.39


[2025-06-01 21:06:40] [MQTT MSG] intake/turbidity → 40.09


[2025-06-01 21:06:40] [MQTT MSG] intake/chemical_doser → dose_off


[2025-06-01 21:06:40] [MQTT MSG] intake/valve_actuator → close


[2025-06-01 21:06:40] [MQTT MSG] intake/flow → 0.0


[2025-06-01 21:06:45] [MQTT MSG] intake/water_level → 3.87


[2025-06-01 21:06:45] [MQTT MSG] intake/turbidity → 86.09


[2025-06-01 21:06:45] [MQTT MSG] intake/valve_actuator → open


[2025-06-01 21:06:45] [MQTT MSG] intake/flow → 0.0
```