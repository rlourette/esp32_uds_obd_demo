from machine import Pin
from esp32 import CAN
import time

# Initialize CAN interface (GPIO21 TX, GPIO22 RX)
can = CAN(0, tx=Pin(21), rx=Pin(22), baudrate=500000, mode=CAN.NORMAL)

# Configuration
DEMO_MODE = "basic"  # Options: "basic", "dtc", "security", "full"
BASIC_PIDS = [0x0C, 0x0D]  # RPM, Speed
EXTENDED_PIDS = [0x0C, 0x0D, 0x05, 0x0F, 0x11]  # Add temp and throttle

# Current demo PIDs based on mode
pids = BASIC_PIDS if DEMO_MODE == "basic" else EXTENDED_PIDS

def build_pid_request(pid):
    # OBD-II request: [Length, Mode, PID, padding...]
    # Mode 01 = Show current data, Length = 2 (mode + pid)
    return bytearray([0x02, 0x01, pid, 0x00, 0x00, 0x00, 0x00, 0x00])

def build_uds_request(service_id, data=None):
    """Build a UDS request frame"""
    if data is None:
        data = []
    request = [len(data) + 1, service_id] + data
    # Pad to 8 bytes
    while len(request) < 8:
        request.append(0x00)
    return bytearray(request)

def parse_response(pid, data):
    """Parse OBD-II response data into human-readable values"""
    if len(data) < 3:
        return "Invalid response length"
    
    # Check if it's a positive response (0x41 = mode 0x01 response)
    if data[1] != 0x41 or data[2] != pid:
        return "Invalid response format"
    
    if pid == 0x0C:  # RPM
        if len(data) >= 5:
            rpm = ((data[3] << 8) + data[4]) / 4
            return f"RPM: {rpm:.0f}"
    elif pid == 0x0D:  # Vehicle Speed
        if len(data) >= 4:
            speed = data[3]
            return f"Speed: {speed} km/h"
    elif pid == 0x05:  # Engine Coolant Temperature
        if len(data) >= 4:
            temp = data[3] - 40  # Convert from offset
            return f"Coolant Temp: {temp}°C"
    elif pid == 0x0F:  # Intake Air Temperature
        if len(data) >= 4:
            temp = data[3] - 40  # Convert from offset
            return f"Intake Air Temp: {temp}°C"
    elif pid == 0x11:  # Throttle Position
        if len(data) >= 4:
            throttle = (data[3] * 100) / 255
            return f"Throttle: {throttle:.1f}%"
    
    return f"Raw data: {[hex(b) for b in data[3:]]}"

def get_nrc_description(nrc):
    """Get description for Negative Response Code"""
    nrc_codes = {
        0x10: "generalReject",
        0x11: "serviceNotSupported", 
        0x12: "subFunctionNotSupported",
        0x13: "incorrectMessageLengthOrInvalidFormat",
        0x22: "conditionsNotCorrect",
        0x31: "requestOutOfRange",
        0x33: "securityAccessDenied",
        0x35: "invalidKey",
        0x36: "exceedNumberOfAttempts",
        0x37: "requiredTimeDelayNotExpired",
        0x78: "requestCorrectlyReceived-ResponsePending"
    }
    return nrc_codes.get(nrc, f"Unknown NRC: 0x{nrc:02X}")

def format_dtc(high_byte, low_byte):
    """Format DTC from two bytes into P0XXX format"""
    # Extract the first two bits for DTC type
    dtc_type = (high_byte >> 6) & 0x03
    type_chars = ['P', 'C', 'B', 'U']  # Powertrain, Chassis, Body, Network
    
    # Extract remaining 14 bits for the number
    dtc_number = ((high_byte & 0x3F) << 8) | low_byte
    
    return f"{type_chars[dtc_type]}{dtc_number:04X}"

def parse_dtc_response(data):
    """Parse DTC response data"""
    if len(data) < 4:
        return "Invalid DTC response"
    
    dtc_count = data[3]
    if dtc_count == 0:
        return "No DTCs stored"
    
    dtcs = []
    for i in range(4, min(len(data)-1, 4 + dtc_count*3), 3):
        if i+2 < len(data):
            dtc_high = data[i]
            dtc_low = data[i+1]
            status = data[i+2]
            dtc_code = format_dtc(dtc_high, dtc_low)
            dtcs.append(f"{dtc_code} (Status: 0x{status:02X})")
    
    return f"DTCs found: {dtcs}"

def read_dtcs():
    """Read Diagnostic Trouble Codes (Service 0x19)"""
    print("Reading Diagnostic Trouble Codes...")
    # Sub-function 0x02: reportDTCByStatusMask
    # Status mask 0xFF: all DTCs
    req = build_uds_request(0x19, [0x02, 0xFF])
    can.send(req, 0x7DF)
    time.sleep(0.1)
    
    try:
        msg = can.recv(timeout=1000)
        if msg and len(msg) >= 3:
            if msg[1] == 0x59:  # Positive response (0x19 + 0x40)
                result = parse_dtc_response(msg)
                print(f"DTC Result: {result}")
                return True
            elif msg[1] == 0x7F:  # Negative response
                error = get_nrc_description(msg[3])
                print(f"DTC Error: {error}")
                return False
        print("No DTC response received")
        return False
    except Exception as e:
        print(f"DTC CAN error: {e}")
        return False

def security_access(level=1):
    """Request security access (simplified example)"""
    print(f"Requesting security access level {level}...")
    # Request seed (odd levels request seed, even levels send key)
    req = build_uds_request(0x27, [level])
    can.send(req, 0x7DF)
    time.sleep(0.1)
    
    try:
        msg = can.recv(timeout=1000)
        if msg and msg[1] == 0x67:  # Positive response
            if len(msg) >= 4:
                seed = msg[3:]  # Extract seed
                print(f"Received seed: {[hex(b) for b in seed]}")
                print("Note: Key calculation not implemented - this is just a demo")
                return True
        elif msg and msg[1] == 0x7F:
            error = get_nrc_description(msg[3])
            print(f"Security access denied: {error}")
            return False
        print("No security access response")
        return False
    except Exception as e:
        print(f"Security access error: {e}")
        return False

def clear_dtcs():
    """Clear Diagnostic Trouble Codes (Service 0x14)"""
    print("Clearing Diagnostic Trouble Codes...")
    req = build_uds_request(0x14, [0xFF, 0xFF, 0xFF])  # Clear all DTCs
    can.send(req, 0x7DF)
    time.sleep(0.1)
    
    try:
        msg = can.recv(timeout=1000)
        if msg and msg[1] == 0x54:  # Positive response
            print("DTCs cleared successfully")
            return True
        elif msg and msg[1] == 0x7F:
            error = get_nrc_description(msg[3])
            print(f"Clear DTC error: {error}")
            return False
        print("No clear DTC response")
        return False
    except Exception as e:
        print(f"Clear DTC CAN error: {e}")
        return False

def read_vin():
    """Read Vehicle Identification Number (Service 0x22, DID 0xF190)"""
    print("Reading Vehicle Identification Number...")
    req = build_uds_request(0x22, [0xF1, 0x90])  # VIN DID
    can.send(req, 0x7DF)
    time.sleep(0.1)
    
    try:
        msg = can.recv(timeout=1000)
        if msg and msg[1] == 0x62:  # Positive response
            if len(msg) >= 5 and msg[2] == 0xF1 and msg[3] == 0x90:
                vin_data = msg[4:]
                # Convert to ASCII if printable
                vin = ''.join([chr(b) if 32 <= b <= 126 else f'\\x{b:02x}' for b in vin_data if b != 0])
                print(f"VIN: {vin}")
                return vin
        elif msg and msg[1] == 0x7F:
            error = get_nrc_description(msg[3])
            print(f"VIN read error: {error}")
        else:
            print("No VIN response or invalid format")
        return None
    except Exception as e:
        print(f"VIN read CAN error: {e}")
        return None

def send_and_receive(pid):
    req = build_pid_request(pid)
    can.send(req, 0x7DF)
    time.sleep(0.1)
    try:
        # Add timeout to prevent blocking indefinitely
        msg = can.recv(timeout=1000)  # 1 second timeout
        if msg:
            parsed = parse_response(pid, msg)
            print(f"PID 0x{pid:02X}: {parsed}")
        else:
            print(f"No response for PID 0x{pid:02X}")
    except Exception as e:
        print(f"CAN receive error for PID 0x{pid:02X}:", e)

def run_uds_demo():
    """Run UDS diagnostic demos"""
    print("\n" + "="*50)
    print("UDS Diagnostic Services Demo")
    print("="*50)
    
    # Test DTC reading
    if DEMO_MODE in ["dtc", "full"]:
        read_dtcs()
        time.sleep(1)
    
    # Test VIN reading
    if DEMO_MODE in ["full"]:
        read_vin()
        time.sleep(1)
    
    # Test security access (demonstration only)
    if DEMO_MODE in ["security", "full"]:
        security_access(1)
        time.sleep(1)
    
    print("="*50)
    print("Returning to OBD-II polling...\n")

def loop_poll():
    print("Starting OBD-II polling...")
    print("PIDs to poll:", [f"0x{pid:02X}" for pid in pids])
    print(f"Demo mode: {DEMO_MODE}")
    print("Press Ctrl+C to stop\n")
    
    # Run UDS demo first if enabled
    if DEMO_MODE != "basic":
        run_uds_demo()
    
    poll_count = 0
    try:
        while True:
            for pid in pids:
                send_and_receive(pid)
            print()  # Add blank line between polling cycles
            
            # Run UDS demo every 10 polling cycles in full mode
            poll_count += 1
            if DEMO_MODE == "full" and poll_count % 10 == 0:
                run_uds_demo()
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nPolling stopped by user")
    except Exception as e:
        print(f"Polling error: {e}")

def print_demo_info():
    """Print information about demo modes"""
    print("ESP32 UDS OBD-II Demo")
    print("=" * 25)
    print("Hardware: ESP32 with built-in CAN transceiver")
    print("Baudrate: 500 kbps")
    print("CAN ID: 0x7DF (OBD-II broadcast)")
    print(f"Demo Mode: {DEMO_MODE}")
    print()
    
    if DEMO_MODE == "basic":
        print("Basic Mode: OBD-II PID polling only")
    elif DEMO_MODE == "dtc":
        print("DTC Mode: OBD-II polling + DTC reading")
    elif DEMO_MODE == "security":
        print("Security Mode: OBD-II polling + Security Access demo")
    elif DEMO_MODE == "full":
        print("Full Mode: All UDS services demonstrated")
        print("- OBD-II PID polling")
        print("- DTC reading")
        print("- VIN reading") 
        print("- Security access demo")
    print()

# Only run if this is the main module
if __name__ == "__main__":
    try:
        print_demo_info()
        loop_poll()
    except Exception as e:
        print(f"Initialization error: {e}")
        print("Check hardware connections and CAN bus wiring.")
        print("\nTo change demo mode, edit DEMO_MODE variable in main.py:")
        print("- 'basic': OBD-II only")
        print("- 'dtc': Add DTC reading")
        print("- 'security': Add security access")
        print("- 'full': All UDS services")