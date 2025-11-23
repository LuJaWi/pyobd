#!/usr/bin/env python3
"""
Hardware diagnostic script for testing PyOBD with a real ELM327 adapter.

This script performs a series of tests to verify the OBD-II connection and
basic functionality with actual hardware. Run this with your car's ignition ON
and OBD-II adapter plugged in.

Usage:
    python test_hardware.py                    # Auto-detect port
    python test_hardware.py /dev/ttyUSB0       # Specific port
    python test_hardware.py --list-ports       # List available ports
"""

import sys
import time
from pathlib import Path
from typing import Optional

# Add parent directory to path to import obd2 module
sys.path.insert(0, str(Path(__file__).parent.parent))

from obd2.obd_connection import OBDConnection
from obd2.utils.obd_status import OBDStatus
from serial.tools import list_ports


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")


def print_test(name: str, status: str, details: str = ""):
    """Print a test result"""
    if status == "PASS":
        symbol = "✓"
        color = Colors.GREEN
    elif status == "FAIL":
        symbol = "✗"
        color = Colors.RED
    elif status == "WARN":
        symbol = "⚠"
        color = Colors.YELLOW
    else:
        symbol = "ℹ"
        color = Colors.BLUE
    
    print(f"{color}{symbol} {name}: {status}{Colors.END}")
    if details:
        print(f"  {details}")


def list_available_ports():
    """List all available serial ports"""
    print_header("Available Serial Ports")
    
    ports = list(list_ports.comports())
    
    if not ports:
        print_test("Port Detection", "WARN", "No serial ports found")
        print("\nMake sure your OBD-II adapter is plugged in.")
        return
    
    print("Found the following serial ports:\n")
    for i, port in enumerate(ports, 1):
        print(f"{i}. {Colors.BOLD}{port.device}{Colors.END}")
        print(f"   Description: {port.description}")
        print(f"   Hardware ID: {port.hwid}")
        
        # Highlight likely OBD adapters
        if any(keyword in port.description.lower() for keyword in ['usb', 'uart', 'serial', 'ch340', 'cp210', 'ftdi']):
            print(f"   {Colors.GREEN}→ Likely OBD-II adapter{Colors.END}")
        print()


def test_connection(port: Optional[str] = None) -> Optional[OBDConnection]:
    """Test 1: Establish connection to ELM327"""
    print_header("Test 1: Connection")
    
    try:
        if port:
            print(f"Attempting to connect to: {Colors.BOLD}{port}{Colors.END}")
        else:
            print(f"Attempting auto-detection...")
        
        print("(This may take 10-15 seconds...)\n")
        
        connection = OBDConnection(portstr=port, fast=False)
        
        if connection.is_connected():
            print_test("Connection", "PASS", 
                      f"Connected to {connection.port_name()}")
            print_test("Protocol", "INFO", 
                      f"Using protocol: {connection.protocol_name()}")
            return connection
        else:
            print_test("Connection", "FAIL", 
                      f"Status: {connection.status()}")
            return None
            
    except Exception as e:
        print_test("Connection", "FAIL", f"Exception: {str(e)}")
        return None


def test_adapter_info(connection: OBDConnection):
    """Test 2: Get adapter information"""
    print_header("Test 2: Adapter Information")
    
    print_test("Port", "INFO", connection.port_name())
    print_test("Protocol", "INFO", 
              f"{connection.protocol_name()} (ID: {connection.protocol_id()})")
    
    # Check if we can get voltage
    try:
        status = connection.status()
        if status == OBDStatus.CAR_CONNECTED:
            print_test("Connection Status", "PASS", "Car connected")
        elif status == OBDStatus.ELM_CONNECTED:
            print_test("Connection Status", "WARN", 
                      "Adapter connected but no car detected")
        else:
            print_test("Connection Status", "FAIL", str(status))
    except Exception as e:
        print_test("Status Check", "FAIL", str(e))


def test_supported_commands(connection: OBDConnection):
    """Test 3: Check supported commands"""
    print_header("Test 3: Supported Commands")
    
    # Key commands to check
    important_commands = [
        "STATUS",
        "ENGINE_RPM",
        "VEHICLE_SPEED",
        "COOLANT_TEMP",
        "THROTTLE_POS",
        "ENGINE_LOAD",
    ]
    
    supported_count = 0
    
    try:
        for cmd_name in important_commands:
            cmd = connection.commands.get(cmd_name)
            if cmd:
                is_supported = connection.supports(cmd)
                if is_supported:
                    print_test(cmd_name, "PASS", "Supported by vehicle")
                    supported_count += 1
                else:
                    print_test(cmd_name, "WARN", "Not supported by vehicle")
            else:
                print_test(cmd_name, "FAIL", "Command not found in library")
        
        print(f"\n{Colors.BOLD}Summary:{Colors.END} {supported_count}/{len(important_commands)} key commands supported")
        
    except Exception as e:
        print_test("Command Support Check", "FAIL", str(e))


def test_basic_queries(connection: OBDConnection):
    """Test 4: Query basic sensor data"""
    print_header("Test 4: Basic Sensor Queries")
    
    queries = [
        ("ENGINE_RPM", "RPM"),
        ("VEHICLE_SPEED", "km/h"),
        ("COOLANT_TEMP", "°C"),
        ("THROTTLE_POS", "%"),
    ]
    
    successful = 0
    
    for cmd_name, unit in queries:
        try:
            cmd = connection.commands.get(cmd_name)
            if not cmd:
                print_test(cmd_name, "FAIL", "Command not found")
                continue
            
            if not connection.supports(cmd):
                print_test(cmd_name, "WARN", "Not supported by vehicle")
                continue
            
            response = connection.query(cmd)
            
            if response and response.value is not None:
                print_test(cmd_name, "PASS", 
                          f"Value: {response.value} {unit}")
                successful += 1
            else:
                print_test(cmd_name, "FAIL", "No data received")
                
        except Exception as e:
            print_test(cmd_name, "FAIL", f"Exception: {str(e)}")
    
    print(f"\n{Colors.BOLD}Summary:{Colors.END} {successful}/{len(queries)} queries successful")


def test_dtc_reading(connection: OBDConnection):
    """Test 5: Read Diagnostic Trouble Codes"""
    print_header("Test 5: Diagnostic Trouble Codes (DTCs)")
    
    try:
        get_dtc = connection.commands.get("GET_DTC")
        if not get_dtc:
            print_test("DTC Reading", "FAIL", "GET_DTC command not found")
            return
        
        response = connection.query(get_dtc)
        
        if response and response.value is not None:
            dtcs = response.value
            if isinstance(dtcs, list) and len(dtcs) > 0:
                print_test("DTC Reading", "WARN", 
                          f"Found {len(dtcs)} trouble code(s):")
                for code, description in dtcs:
                    print(f"  • {code}: {description}")
            else:
                print_test("DTC Reading", "PASS", "No trouble codes present")
        else:
            print_test("DTC Reading", "FAIL", "Could not read DTCs")
            
    except Exception as e:
        print_test("DTC Reading", "FAIL", f"Exception: {str(e)}")


def test_continuous_monitoring(connection: OBDConnection, duration: int = 5):
    """Test 6: Continuous data monitoring"""
    print_header(f"Test 6: Continuous Monitoring ({duration}s)")
    
    cmd = connection.commands.get("ENGINE_RPM")
    if not cmd or not connection.supports(cmd):
        print_test("Continuous Monitoring", "WARN", 
                  "ENGINE_RPM not supported, skipping test")
        return
    
    print(f"Monitoring RPM for {duration} seconds...\n")
    
    samples = []
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            response = connection.query(cmd)
            if response and response.value is not None:
                samples.append(response.value)
                print(f"  RPM: {response.value:>6.0f}", end='\r')
                time.sleep(0.5)
        
        print()  # New line after monitoring
        
        if samples:
            avg_rpm = sum(samples) / len(samples)
            min_rpm = min(samples)
            max_rpm = max(samples)
            
            print_test("Continuous Monitoring", "PASS", 
                      f"Collected {len(samples)} samples")
            print(f"  Average: {avg_rpm:.0f} RPM")
            print(f"  Range: {min_rpm:.0f} - {max_rpm:.0f} RPM")
        else:
            print_test("Continuous Monitoring", "FAIL", "No samples collected")
            
    except KeyboardInterrupt:
        print("\n  Monitoring interrupted by user")
        print_test("Continuous Monitoring", "WARN", "Test interrupted")
    except Exception as e:
        print_test("Continuous Monitoring", "FAIL", f"Exception: {str(e)}")


def run_all_tests(port: Optional[str] = None):
    """Run complete hardware test suite"""
    print(f"\n{Colors.BOLD}PyOBD Hardware Test Suite{Colors.END}")
    print(f"Testing with real ELM327 adapter and vehicle\n")
    
    if port:
        print(f"Target port: {Colors.BOLD}{port}{Colors.END}")
    else:
        print(f"Mode: {Colors.BOLD}Auto-detect{Colors.END}")
    
    print(f"\n{Colors.YELLOW}⚠  Make sure:{Colors.END}")
    print(f"  • OBD-II adapter is plugged into your vehicle")
    print(f"  • Vehicle ignition is ON (engine can be off)")
    print(f"  • You have permission to access the serial port")
    
    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.END}")
    
    # Test 1: Connection
    connection = test_connection(port)
    if not connection:
        print(f"\n{Colors.RED}Connection failed. Cannot continue with other tests.{Colors.END}")
        print(f"\n{Colors.YELLOW}Troubleshooting:{Colors.END}")
        print(f"  1. Check adapter is plugged in and powered")
        print(f"  2. Try running: python test_hardware.py --list-ports")
        print(f"  3. Try specifying port: python test_hardware.py /dev/ttyUSB0")
        print(f"  4. Check permissions: ls -l /dev/ttyUSB*")
        return False
    
    # Test 2: Adapter info
    test_adapter_info(connection)
    
    # Test 3: Supported commands
    test_supported_commands(connection)
    
    # Test 4: Basic queries
    test_basic_queries(connection)
    
    # Test 5: DTC reading
    test_dtc_reading(connection)
    
    # Test 6: Continuous monitoring
    try:
        test_continuous_monitoring(connection, duration=5)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.END}")
    
    # Close connection
    print_header("Cleanup")
    try:
        connection.close()
        print_test("Connection Close", "PASS", "Connection closed successfully")
    except Exception as e:
        print_test("Connection Close", "FAIL", f"Exception: {str(e)}")
    
    print_header("Test Suite Complete")
    print(f"{Colors.GREEN}Hardware testing finished!{Colors.END}\n")
    
    return True


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--list-ports', '-l', '--list']:
            list_available_ports()
            return
        elif sys.argv[1] in ['--help', '-h']:
            print(__doc__)
            return
        else:
            # Use specified port
            port = sys.argv[1]
            run_all_tests(port)
    else:
        # Auto-detect
        run_all_tests(None)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Testing interrupted by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
