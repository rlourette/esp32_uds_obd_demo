from machine import Pin
from esp32 import CAN
import time

# Initialize CAN interface (GPIO21 TX, GPIO22 RX)
can = CAN(0, tx=Pin(21), rx=Pin(22), baudrate=500000, mode=CAN.NORMAL)

# Example OBD-II PIDs: 0x0C = RPM, 0x0D = Speed, 0x05 = Coolant Temp, 0x0F = Intake Air Temp
pids = [0x0C, 0x0D]  # Start with basic PIDs - uncomment others as needed
# Additional PIDs you can try: [0x05, 0x0F, 0x11, 0x21, 0x2F]

def build_pid_request(pid):
    # OBD-II request: [Length, Mode, PID, padding...]
    # Mode 01 = Show current data, Length = 2 (mode + pid)
    return bytearray([0x02, 0x01, pid, 0x00, 0x00, 0x00, 0x00, 0x00])

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

def loop_poll():
    print("Starting OBD-II polling...")
    print("PIDs to poll:", [f"0x{pid:02X}" for pid in pids])
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            for pid in pids:
                send_and_receive(pid)
            print()  # Add blank line between polling cycles
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nPolling stopped by user")
    except Exception as e:
        print(f"Polling error: {e}")

# Only run if this is the main module
if __name__ == "__main__":
    try:
        print("ESP32 UDS OBD-II Demo")
        print("=" * 25)
        print("Hardware: ESP32 with built-in CAN transceiver")
        print("Baudrate: 500 kbps")
        print("CAN ID: 0x7DF (OBD-II broadcast)")
        print()
        loop_poll()
    except Exception as e:
        print(f"Initialization error: {e}")
        print("Check hardware connections and CAN bus wiring.")