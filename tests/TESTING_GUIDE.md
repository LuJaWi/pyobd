# PyOBD Testing Guide

## Quick Start

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_decoders.py -v

# Run tests by marker
pytest -m decoders
```

## Test Structure

```
tests/
├── conftest.py              # Fixtures and mock infrastructure
├── test_commands.py         # OBD command definitions (19 tests)
├── test_connection.py       # OBD connection and interface (11 tests)
├── test_decoders.py         # Data decoder functions (18 tests)
├── test_protocols.py        # Protocol parsing (10 tests)
└── test_utils.py            # Utility functions (15 tests)
```

## Mock Infrastructure

### MockSerial
Simulates ELM327 adapter without hardware:

```python
from tests.conftest import MockSerial

mock = MockSerial(port='/dev/ttyUSB0')
mock.write(b'0100\r')  # Send command
data = mock.read(10)   # Read response
```

### MockOBDResponses
Realistic OBD-II test data:

```python
from tests.conftest import MockOBDResponses

responses = MockOBDResponses()
rpm_data = responses.ENGINE_RPM      # ["41 0C 1A F8"]
speed_data = responses.VEHICLE_SPEED # ["41 0D 3C"]
```

## Test Markers

Organize and filter tests by category:

```bash
pytest -m decoders     # Run decoder tests only
pytest -m connection   # Run connection tests only
pytest -m commands     # Run command tests only
pytest -m protocols    # Run protocol tests only
pytest -m utils        # Run utility tests only
```

## Writing New Tests

### 1. Basic Test Structure

```python
import pytest
from obd2.obd2 import OBD

@pytest.mark.connection
def test_my_feature(mock_serial):
    """Test description"""
    # Use mock_serial fixture for hardware-free testing
    connection = OBDConnection(portstr='/dev/ttyUSB0', fast=False)
    assert connection.is_connected()
```

### 2. Using Fixtures

```python
def test_with_custom_responses(mock_serial_factory, obd_responses):
    """Test with custom mock responses"""
    mock = mock_serial_factory(
        b'0100\r': obd_responses.PIDS_A,
        b'010C\r': obd_responses.ENGINE_RPM
    )
    # Test with custom responses
```

### 3. Testing Decoders

```python
from decoding.decoders import temp
from elm327.protocols.models.message import Message

def test_temperature_decoder():
    """Test temperature decoding"""
    msg = Message([])
    msg.data = bytearray([0x41, 0x05, 0x5F])  # Coolant temp
    
    result = temp(msg)
    assert result.value == 55  # 95 - 40 = 55°C
```

## Coverage Goals

- **Decoders**: Test each decoder with typical and edge case values
- **Commands**: Verify command properties and structure
- **Protocols**: Test frame/message parsing
- **Utils**: Test utility functions with various inputs
- **Connection**: Test initialization, querying, status

Current coverage: **79% overall**

## Debugging Failed Tests

### Verbose Output
```bash
pytest tests/test_decoders.py -v --tb=long
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Run Specific Test
```bash
pytest tests/test_decoders.py::TestBasicDecoders::test_drop_returns_none -v
```

### Print Debug Output
```bash
pytest tests/ -v -s  # Shows print statements
```

## CI/CD Integration

The test suite is configured for GitHub Actions (see `.github/workflows/tests.yml`):

- Runs on every push and pull request
- Tests on multiple Python versions
- Generates coverage reports
- Fails build if tests don't pass

## Common Issues

### Import Errors
Ensure you're running from project root:
```bash
cd /Users/lukewitt/Coding/pyobd
pytest tests/
```

### Mock Serial Issues
If connection tests fail, verify MockSerial has all required methods:
- `read()`, `write()`, `readline()`
- `open()`, `close()`
- `flush()`, `flushInput()`, `flushOutput()`
- Attributes: `port`, `portstr`, `baudrate`, `timeout`, `is_open`

### Coverage Not Working
Install coverage dependencies:
```bash
pip install pytest-cov
```

## Test Data

Mock responses match real ELM327 behavior:

- **ATZ**: `"ELM327 v1.5"`
- **ATE0**: `"OK"`
- **0100**: `"41 00 BE 3F B8 13"` (supported PIDs)
- **010C**: `"41 0C 1A F8"` (RPM ~1726)
- **010D**: `"41 0D 3C"` (Speed 60 km/h)
- **0105**: `"41 05 5F"` (Coolant 55°C)

## Best Practices

1. ✅ **Use fixtures** - Leverage `mock_serial` and `obd_responses`
2. ✅ **Add markers** - Categorize tests with `@pytest.mark.<category>`
3. ✅ **Test edge cases** - Include boundary values and error conditions
4. ✅ **Keep tests fast** - Mock external dependencies
5. ✅ **Document tests** - Clear docstrings explaining what's tested
6. ✅ **Verify fixes** - Add tests for any bugs discovered

## Resources

- **pytest docs**: https://docs.pytest.org/
- **Coverage.py**: https://coverage.readthedocs.io/
- **Test results**: See `TEST_RESULTS.md`
- **Coverage report**: Open `htmlcov/index.html` after running with `--cov-report=html`

---

*Last updated: November 22, 2025*  
*All 73 tests passing | 79% coverage*
