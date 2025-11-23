# Hardware Tests

Real-world tests for PyOBD with actual ELM327 adapters and vehicles.

⚠️ **These tests require actual hardware** - an OBD-II adapter plugged into a vehicle.

## Quick Start

```bash
# List available ports
python hardware_tests/test_hardware.py --list-ports

# Auto-detect and test
python hardware_tests/test_hardware.py

# Test specific port
python hardware_tests/test_hardware.py /dev/ttyUSB0
```

## Requirements

- ELM327 OBD-II adapter (USB, Bluetooth, or WiFi)
- Vehicle with OBD-II port (1996+ in US)
- Vehicle ignition ON (engine can be on or off)

## What Gets Tested

1. **Connection** - Can we connect to the adapter?
2. **Adapter Info** - Port, protocol, connection status
3. **Supported Commands** - Which OBD commands does your car support?
4. **Basic Queries** - Read RPM, speed, temperature, throttle
5. **DTC Reading** - Check for trouble codes
6. **Continuous Monitoring** - 5 seconds of real-time RPM monitoring

## Typical Output

```
✓ Connection: PASS
  Connected to /dev/ttyUSB0
  
✓ ENGINE_RPM: PASS
  Value: 850 RPM
  
✓ VEHICLE_SPEED: PASS
  Value: 0 km/h
```

## Troubleshooting

### No ports found
```bash
python hardware_tests/test_hardware.py --list-ports
```
Make sure your adapter is plugged in.

### Permission denied
```bash
sudo chmod 666 /dev/ttyUSB0
# or add yourself to dialout group (Linux)
sudo usermod -a -G dialout $USER
```

### Connection timeout
- Check vehicle ignition is ON
- Try unplugging and replugging adapter
- Some adapters need a few seconds after plugging in

### No data from queries
- Engine may need to be running for some sensors
- Not all cars support all OBD commands
- Check for DTCs that might indicate sensor issues

## Files

- `test_hardware.py` - Main hardware test suite
- `README.md` - This file

## vs Unit Tests

- **Unit tests** (`tests/`) - Mock hardware, test logic, run anywhere
- **Hardware tests** (`hardware_tests/`) - Real hardware, test integration, need car

Both are important! Unit tests prove the code works, hardware tests prove it works with **your** car.
