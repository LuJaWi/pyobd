# PyOBD Test Suite

Comprehensive test suite for both legacy and new PyOBD codebase implementations.

## Overview

This test suite ensures:
- ✅ **100% functionality parity** between legacy and new code
- ✅ **No hardware required** - all tests use mocks
- ✅ **Comprehensive coverage** - decoders, protocols, connections, commands, utils
- ✅ **Parametrized tests** - same tests run against both codebases

## Quick Start

### Install Test Dependencies

```bash
pip install pytest pytest-cov pytest-mock
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test Categories

```bash
# Run only decoder tests
pytest -m decoders

# Run only connection tests
pytest -m connection

# Run only command tests
pytest -m commands

# Run only utility tests
pytest -m utils
```

### Run Tests for Specific Codebase

```bash
# Run tests only for new codebase
pytest tests/new/

# Run tests only for legacy codebase
pytest tests/legacy/
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_decoders.py
```

### Run Specific Test Function

```bash
pytest tests/test_decoders.py::TestTemperatureDecoders::test_temp_decoder_coolant
```

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared fixtures and configuration
├── test_decoders.py            # Decoder function tests
├── test_utils.py               # Utility function tests
├── test_commands.py            # Command definition tests
├── test_connection.py          # OBD connection tests
├── mocks/                      # Mock objects and data
├── legacy/                     # Legacy-specific tests (if needed)
└── new/                        # New-code-specific tests (if needed)
```

## Test Categories

### ✅ Decoders (`@pytest.mark.decoders`)
Tests all 40+ decoder functions with realistic OBD responses:
- Temperature decoders (coolant, intake)
- Pressure decoders (fuel, intake manifold)
- Percentage decoders (throttle, load, fuel trim)
- UAS (Units and Scaling) decoders
- DTC (trouble code) decoders
- Status decoders
- Voltage decoders
- Count decoders

### ✅ Utilities (`@pytest.mark.utils`)
Tests utility functions:
- Hex conversion tools (`bytes_to_int`, `bytes_to_hex`, `twos_comp`, `is_hex`)
- BitArray class functionality
- OBDStatus enum/class
- Contiguous list checking
- Serial port scanning (mocked)

### ✅ Commands (`@pytest.mark.commands`)
Tests command definitions:
- All Mode 1 commands (live data)
- Mode 3 commands (DTCs)
- Mode 4 commands (clear DTCs)
- Mode 9 commands (vehicle info)
- Command access methods
- Command properties
- Total command count validation

### ✅ Connection (`@pytest.mark.connection`)
Tests OBD connection class:
- Connection initialization
- Status checking
- Port and protocol properties
- Command support checking
- Power mode management
- Connection closing

## Parametrized Tests

Many tests use the `codebase` fixture which automatically runs the same test against both legacy and new code:

```python
def test_something(codebase):
    # This test runs twice: once with legacy code, once with new code
    result = codebase.decoders.temp(messages)
    assert result is not None
```

## Mock Data

The test suite includes realistic mock OBD-II responses in `conftest.py`:

- `MockOBDResponses` - Collection of realistic adapter responses
- `MockSerial` - Mock serial port that simulates ELM327 adapter
- Sample messages for testing decoders
- Fixtures for both legacy and new message objects

## Writing New Tests

### Basic Test Structure

```python
import pytest

@pytest.mark.decoders
def test_my_decoder(codebase):
    """Test a decoder function"""
    # Create mock message
    class MockFrame:
        def __init__(self):
            self.data = bytearray([0x41, 0x0C, 0x1A, 0xF8])
    
    class MockMessage:
        def __init__(self):
            self.frames = [MockFrame()]
            self.data = bytearray([0x41, 0x0C, 0x1A, 0xF8])
    
    messages = [MockMessage()]
    
    # Test decoder
    result = codebase.decoders.rpm(messages)
    
    # Assert expected behavior
    assert result is not None
```

### Testing Both Codebases Separately

```python
def test_legacy_specific():
    """Test something specific to legacy code"""
    from legacy.obd.utils import some_function
    result = some_function()
    assert result == expected

def test_new_specific():
    """Test something specific to new code"""
    from obd2.utils.hex_tools import some_function
    result = some_function()
    assert result == expected
```

### Using Mocks

```python
from unittest.mock import patch, Mock

@patch('serial.Serial')
def test_with_mock_serial(mock_serial):
    """Test using mocked serial port"""
    mock_serial_instance = Mock()
    mock_serial.return_value = mock_serial_instance
    
    # Your test code here
```

## Test Markers

Use markers to organize and filter tests:

- `@pytest.mark.decoders` - Decoder tests
- `@pytest.mark.protocols` - Protocol parsing tests
- `@pytest.mark.connection` - Connection tests
- `@pytest.mark.commands` - Command definition tests
- `@pytest.mark.utils` - Utility function tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (can be skipped)

## Continuous Integration

Run tests in CI/CD pipeline:

```bash
# Basic test run
pytest --tb=short

# With coverage
pytest --cov=. --cov-report=xml

# Fail if coverage drops below threshold
pytest --cov=. --cov-fail-under=80
```

## Troubleshooting

### ImportError: No module named 'pytest'

Install pytest:
```bash
pip install pytest
```

### Tests failing due to missing dependencies

Install all requirements:
```bash
pip install -r requirements.txt
```

### Serial port errors

All tests use mocks - no actual serial port needed. If you see serial errors, check that mocks are properly configured.

### Legacy code import errors

Ensure the project root is in your Python path. The `conftest.py` handles this automatically.

## Performance

Run tests in parallel for faster execution:

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

## Debugging Tests

Run tests with Python debugger:

```bash
pytest --pdb
```

Or add breakpoints in your test code:

```python
def test_something():
    import pdb; pdb.set_trace()
    # Your test code
```

## Coverage Reports

Generate HTML coverage report:

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## Contributing

When adding new functionality:
1. Add tests for the new feature
2. Ensure tests pass for both legacy and new code
3. Run full test suite before committing
4. Maintain test coverage above 80%

## Questions?

See pytest documentation: https://docs.pytest.org/
