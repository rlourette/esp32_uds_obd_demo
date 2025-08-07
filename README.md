# ESP32 UDS OBD-II MicroPython Demo

This project demonstrates using the ISO 14229 (UDS) diagnostic standard over CAN bus using MicroPython on an ESP32 with a built-in CAN transceiver. It connects to a vehicle's OBD-II port and demonstrates multiple UDS services including PID polling, DTC reading, VIN reading, and security access.

## 🚗 Features

- **Multi-Mode Operation**: Basic OBD-II, DTC diagnostics, Security access, or Full UDS demo
- **OBD-II PID Polling**: RPM, Speed, Coolant Temperature, Intake Air Temperature, and Throttle Position
- **UDS Diagnostic Services**:
  - Service 0x19: Read Diagnostic Trouble Codes (DTCs)
  - Service 0x22: Read Data by Identifier (VIN reading)
  - Service 0x27: Security Access (demonstration)
  - Service 0x14: Clear Diagnostic Information
  - Service 0x10: Diagnostic Session Control (stub, see below)
- **Robust Error Handling**: Timeout protection and negative response code interpretation
- **Human-Readable Output**: Parsed responses with meaningful descriptions
- **Easy Configuration**: Multiple demo modes for different use cases
- Runs on MicroPython on an ESP32 with built-in CAN transceiver
- Designed to work with vehicles supporting ISO 15765-4 (CAN 11-bit ID)

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
3. Power the ESP32 and connect it to your vehicle's OBD-II port
4. Monitor output via serial terminal (115200 baud)

## 🚀 Usage

### Demo Modes

The demo supports multiple operating modes. Edit the `DEMO_MODE` variable in `main.py`:

```python
DEMO_MODE = "basic"  # Options: "basic", "dtc", "security", "full"
```

#### Basic Mode (`DEMO_MODE = "basic"`)
OBD-II PID polling only - safest for initial testing:
```
ESP32 UDS OBD-II Demo
=========================
Hardware: ESP32 with built-in CAN transceiver
Baudrate: 500 kbps
CAN ID: 0x7DF (OBD-II broadcast)
Demo Mode: basic

Basic Mode: OBD-II PID polling only

Starting OBD-II polling...
PIDs to poll: ['0x0C', '0x0D']
Press Ctrl+C to stop

PID 0x0C: RPM: 850
PID 0x0D: Speed: 0 km/h
```

#### DTC Mode (`DEMO_MODE = "dtc"`)
Adds diagnostic trouble code reading:
```
==================================================
UDS Diagnostic Services Demo
==================================================
Reading Diagnostic Trouble Codes...
DTC Result: DTCs found: ['P0171 (Status: 0x81)', 'P0300 (Status: 0x01)']
==================================================
Returning to OBD-II polling...
```

#### Security Mode (`DEMO_MODE = "security"`)
Demonstrates security access (seed/key exchange):
```
Requesting security access level 1...
Received seed: ['0x12', '0x34', '0x56', '0x78']
Note: Key calculation not implemented - this is just a demo
```

#### Full Mode (`DEMO_MODE = "full"`)
Demonstrates all UDS services including VIN reading:
```
Full Mode: All UDS services demonstrated
- OBD-II PID polling
- DTC reading
- VIN reading
- Security access demo

Reading Vehicle Identification Number...
VIN: 1HGBH41JXMN109186
```

### Configuration Options

To modify polling behavior, edit these variables in `main.py`:

```python
# Demo mode selection
DEMO_MODE = "basic"  # "basic", "dtc", "security", "full"

# PID configuration
BASIC_PIDS = [0x0C, 0x0D]  # RPM, Speed
EXTENDED_PIDS = [0x0C, 0x0D, 0x05, 0x0F, 0x11]  # Add temp and throttle
```

### Supported PIDs

| PID  | Parameter | Formula | Output |
|------|-----------|---------|--------|
| 0x0C | Engine RPM | ((A*256)+B)/4 | "RPM: 850" |
| 0x0D | Vehicle Speed | A | "Speed: 65 km/h" |
| 0x05 | Coolant Temperature | A-40 | "Coolant Temp: 85°C" |
| 0x0F | Intake Air Temperature | A-40 | "Intake Air Temp: 25°C" |
| 0x11 | Throttle Position | A*100/255 | "Throttle: 15.7%" |

### UDS Services Implemented

| Service | ID | Function | Demo Mode | Status |
|---------|----|-----------|---------|---------| 
| Read Data by Identifier | 0x22 | VIN reading | full | ✅ Implemented |
| Security Access | 0x27 | Seed/key demo | security, full | ✅ Implemented (demo only) |
| Read DTC Information | 0x19 | Get fault codes | dtc, full | ✅ Implemented |
| Clear Diagnostic Information | 0x14 | Clear DTCs | Available in code | ✅ Implemented |
| Diagnostic Session Control | 0x10 | Change session | Available in code | 🟡 Stub only |

## 📄 Notes

- **Demo Modes**: Start with "basic" mode for initial testing, then progress to more advanced modes
- This example uses CAN ID `0x7DF` for broadcast requests and expects responses on `0x7E8-0x7EF`
- **UDS Services**: Currently implements 4 core ISO 14229 diagnostic services with full parsing
- **Implemented Services**: DTC reading/clearing, VIN reading, security access demo
- **Vehicle Compatibility**: Actual supported services vary by vehicle - unsupported requests show appropriate error messages
- **Security Access**: Current implementation demonstrates seed request only - key calculation templates provided
- **Error Handling**: Comprehensive negative response code interpretation for all 13 common NRC codes
- **DTC Support**: Full P/C/B/U code parsing with status interpretation
- **Timeout Protection**: 1-second timeouts prevent blocking on unresponsive ECUs
- **Response Parsing**: Converts raw CAN data into human-readable values for all implemented services

### Notes on Multi-Frame and Session Requirements

- **Multi-Frame Support**: This demo only supports single-frame UDS messages. For longer responses (e.g., VIN on some vehicles), ISO-TP multi-frame handling is required. See template in README for future implementation.
- **Session Control**: Some ECUs require switching to an extended diagnostic session (0x10) before responding to advanced UDS services. The demo includes a stub for this; see main.py for usage.
- **Security Access**: Real ECUs require manufacturer-specific key calculation after seed request. This demo only requests the seed for educational purposes.
- **Vehicle Compatibility**: Not all vehicles/ECUs support all services or respond in all sessions. Always start with basic mode and consult ECU documentation for advanced features.

## 🔧 Troubleshooting

**No responses received:**
- Check CAN bus wiring and termination (120Ω resistors)
- Verify vehicle is in key-on position (engine doesn't need to be running)
- Some vehicles require engine running for certain PIDs
- Start with "basic" mode before trying advanced UDS services

**Import errors:**
- Ensure you're using ESP32-specific MicroPython firmware with CAN support
- The `esp32.CAN` module requires compatible hardware and firmware

**UDS service errors:**
- "serviceNotSupported": ECU doesn't implement this service
- "securityAccessDenied": Security access required first
- "conditionsNotCorrect": Vehicle conditions don't allow this operation
- Try basic OBD-II PIDs first (0x0C, 0x0D) before UDS services

**DTC reading issues:**
- Some vehicles only report DTCs when MIL (check engine light) is on
- Try different status masks in the `read_dtcs()` function
- Ensure vehicle has been driven recently to generate DTCs

## 🚀 Advanced Implementation Guide

### Currently Implemented UDS Services

The demo includes these fully functional UDS services:

#### Service 0x19 - Read Diagnostic Trouble Codes
```python
# Already implemented in main.py
read_dtcs()  # Reads DTCs with status mask, parses P/C/B/U codes
```

#### Service 0x22 - Read Data by Identifier (VIN)
```python
# Already implemented in main.py
read_vin()  # Reads VIN using DID 0xF190
```

#### Service 0x27 - Security Access (Demo)
```python
# Already implemented in main.py
security_access(level=1)  # Demonstrates seed request (key calc not included)
```

#### Service 0x14 - Clear Diagnostic Information
```python
# Already implemented in main.py
clear_dtcs()  # Clears all stored DTCs
```

#### Service 0x10 - Diagnostic Session Control (Stub)
```python
# Stub for session control, see main.py for usage
# Example: request default or extended diagnostic session
# Not all ECUs require this, but some do for advanced services
# Usage: diagnostic_session_control(0x01)  # Default session
#        diagnostic_session_control(0x03)  # Extended session
```

### Utility Functions Implemented

The demo includes these supporting functions:
- `build_uds_request(service_id, data)` - Builds UDS request frames
- `get_nrc_description(nrc)` - Interprets negative response codes
- `parse_dtc_response(data)` - Parses DTC response data
- `format_dtc(high_byte, low_byte)` - Formats DTCs as P/C/B/U codes

### Template for Adding New UDS Services

To add more UDS services, follow this pattern:

```python
def new_uds_service():
    """Template for new UDS service"""
    req = build_uds_request(SERVICE_ID, [data])
    can.send(req, 0x7DF)
    time.sleep(0.1)
    
    try:
        msg = can.recv(timeout=1000)
        if msg and msg[1] == (SERVICE_ID + 0x40):  # Positive response
            # Parse response
            return parse_response(msg)
        elif msg and msg[1] == 0x7F:  # Negative response
            return f"Error: {get_nrc_description(msg[3])}"
    except Exception as e:
        return f"Error: {e}"
```

### Multi-Frame Support (ISO-TP) - Future Enhancement

For services requiring longer messages, this template can be implemented:

```python
def send_multi_frame(data, can_id=0x7DF):
    """Send multi-frame UDS message using ISO-TP (template for future implementation)"""
    if len(data) <= 7:
        # Single frame
        frame = [len(data)] + list(data)
        while len(frame) < 8:
            frame.append(0x00)
        can.send(bytearray(frame), can_id)
    else:
        # First frame + consecutive frames implementation needed
        pass
```

### Security Access Key Calculation - Future Enhancement

For production use, implement proper seed/key algorithms:

```python
def calculate_key(seed, security_level):
    """Vehicle-specific key calculation (template for future implementation)"""
    # Implement manufacturer-specific algorithm
    # This varies by ECU manufacturer and model
    pass
```

### Additional UDS Services - Implementation Roadmap

The framework supports implementing these additional services:

| Service ID | Service Name | Implementation Complexity | Status |
|------------|--------------|---------------------------|---------|
| 0x10 | Diagnostic Session Control | Low - Session state management | 🔄 Template available |
| 0x11 | ECU Reset | Low - Simple command | 🔄 Template available |
| 0x2E | Write Data By Identifier | Medium - Data validation needed | 🔄 Template available |
| 0x31 | Routine Control | Medium - ECU-specific routines | 🔄 Template available |
| 0x34/36/37 | Download Services | High - Flash programming | 🔄 Template available |

## 📜 License

MIT License
