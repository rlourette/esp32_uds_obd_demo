# ESP32 UDS OBD-II MicroPython Dem## 📥 Installation

1. Flash MicroPython to your ESP32 (https://micropython.org/download/esp32/)
2. Copy `main.py` to the ESP32 using ampy, rshell, or Thonny
3. Power the ESP32 and connect it to your vehicle's OBD-II port
4. Monitor output via serial terminal (115200 baud)

## 🚀 Usage

The code will automatically start polling when powered on and display:
```
ESP32 UDS OBD-II Demo
=========================
Hardware: ESP32 with built-in CAN transceiver
Baudrate: 500 kbps
CAN ID: 0x7DF (OBD-II broadcast)

Starting OBD-II polling...
PIDs to poll: ['0x0C', '0x0D']
Press Ctrl+C to stop

PID 0x0C: RPM: 850
PID 0x0D: Speed: 0 km/h
```

### Adding More PIDs
To poll additional parameters, modify the `pids` list in `main.py`:
```python
pids = [0x0C, 0x0D, 0x05, 0x0F, 0x11]  # RPM, Speed, Coolant Temp, Intake Temp, Throttle
```

### Supported PIDs
| PID  | Parameter | Formula | Output |
|------|-----------|---------|--------|
| 0x0C | Engine RPM | ((A*256)+B)/4 | "RPM: 850" |
| 0x0D | Vehicle Speed | A | "Speed: 65 km/h" |
| 0x05 | Coolant Temperature | A-40 | "Coolant Temp: 85°C" |
| 0x0F | Intake Air Temperature | A-40 | "Intake Air Temp: 25°C" |
| 0x11 | Throttle Position | A*100/255 | "Throttle: 15.7%" |s project demonstrates using the ISO 14229 (UDS) diagnostic standard over CAN bus using MicroPython on an ESP32 with a built-in CAN transceiver. It connects to a vehicle's OBD-II port and polls for vehicle data like RPM, speed, temperatures, and throttle position.

## 🚗 Features

- Communicates with a vehicle's ECU via UDS/OBD-II over CAN
- Polls service 0x01 PIDs with human-readable output
- Supports RPM, Speed, Coolant Temperature, Intake Air Temperature, and Throttle Position
- Robust error handling with timeout protection
- Runs on MicroPython on an ESP32 with built-in CAN transceiver
- Designed to work with vehicles supporting ISO 15765-4 (CAN 11-bit ID)
- Easy to extend with additional PIDs

## 🧰 Parts List

| Part | Description |
|------|-------------|
| [ESP32 with built-in CAN](https://www.waveshare.com/esp32-can.htm) | e.g. Waveshare ESP32 CAN Dev Board |
| OBD-II to DB9 adapter cable | Connects to vehicle OBD-II port |
| Dupont wires | For wiring connections |
| 12V to 5V power supply (optional) | If powering from car battery |

## 🔌 Wiring

| ESP32 Pin | Description | DB9 (OBD-II) |
|-----------|-------------|--------------|
| 21        | CAN TX      | DB9 pin 7    |
| 22        | CAN RX      | DB9 pin 2    |
| GND       | Ground      | DB9 pin 3    |
| 5V        | Power       | DB9 pin 9 (if needed) |

> Use an OBD-II to DB9 cable wired to match Waveshare/WireCan OBD-II pinout.

## 📥 Installation

1. Flash MicroPython to your ESP32 (https://micropython.org/download/esp32/)
2. Copy `main.py` to the ESP32 using ampy, rshell, or Thonny
3. Power the ESP32 and connect it to your vehicle’s OBD-II port
4. Monitor output via serial terminal

## 📄 Notes

- This example uses CAN ID `0x7DF` for broadcast requests and expects responses on `0x7E8-0x7EF`
- It implements basic Mode 0x01 PID polling. For full UDS, implement additional ISO 14229 services
- Actual supported PIDs vary by vehicle - unsupported PIDs will show "No response" or "Invalid response format"
- The code includes 1-second timeout protection to prevent blocking on unresponsive ECUs
- Response parsing converts raw CAN data into human-readable values
- Additional PIDs can be easily added by extending the `parse_response()` function

## 🔧 Troubleshooting

**No responses received:**
- Check CAN bus wiring and termination (120Ω resistors)
- Verify vehicle is in key-on position (engine doesn't need to be running)
- Some vehicles require engine running for certain PIDs

**Import errors:**
- Ensure you're using ESP32-specific MicroPython firmware with CAN support
- The `esp32.CAN` module requires compatible hardware and firmware

**Invalid response format:**
- Vehicle may not support requested PIDs
- Try basic PIDs first (0x0C, 0x0D) before adding others

## 📜 License

MIT License