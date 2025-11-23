# PyOBD Testing Quick Start Guide

## Installation

1. **Install test dependencies:**
```bash
pip install pytest pytest-cov pytest-mock
```

Or install everything from requirements.txt:
```bash
pip install -r requirements.txt
```

## Running Tests

### Option 1: Using the Test Runner (Recommended)

```bash
# Run all tests
python run_tests.py

# Run specific category
python run_tests.py decoders
python run_tests.py utils
python run_tests.py commands
python run_tests.py connection
python run_tests.py protocols

# Quick tests (decoders + utils)
python run_tests.py quick

# Generate coverage report
python run_tests.py coverage
```

### Option 2: Using pytest directly

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_decoders.py

# Run specific test class
pytest tests/test_decoders.py::TestTemperatureDecoders

# Run specific test function
pytest tests/test_decoders.py::TestTemperatureDecoders::test_temp_decoder_coolant

# Run tests by marker
pytest -m decoders
pytest -m utils
pytest -m commands

# Run with coverage
pytest --cov=. --cov-report=html

# Run in parallel (requires pytest-xdist)
pytest -n auto
```

## Understanding Test Results

### ✅ Passing Test
```
tests/test_decoders.py::TestTemperatureDecoders::test_temp_decoder_coolant PASSED
```

### ❌ Failing Test
```
tests/test_decoders.py::TestTemperatureDecoders::test_temp_decoder_coolant FAILED
```

### Test Summary
```
============================= test session starts ==============================
collected 150 items

tests/test_decoders.py ........................................    [ 25%]
tests/test_utils.py ........................................        [ 50%]
tests/test_commands.py ........................................     [ 75%]
tests/test_connection.py ........................................   [100%]

============================== 150 passed in 2.34s ==============================
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures (mock serial, OBD responses)
├── test_decoders.py        # 50+ decoder tests
├── test_utils.py           # 40+ utility tests
├── test_commands.py        # 30+ command tests
├── test_connection.py      # 20+ connection tests
└── test_protocols.py       # 25+ protocol tests
```

## Key Features

### 🔄 Parametrized Tests
Most tests automatically run against BOTH legacy and new codebases:
```python
def test_temp_decoder(codebase):
    # Runs twice: once with legacy, once with new
    result = codebase.decoders.temp(messages)
    assert result is not None
```

### 🎭 Mocked Hardware
No OBD adapter required! All tests use mocks:
```python
@patch('serial.Serial')
def test_connection(mock_serial):
    # Creates mock ELM327 adapter
    connection = OBDConnection(portstr='/dev/ttyUSB0')
```

### 🏷️ Test Markers
Organize and filter tests:
```bash
pytest -m decoders    # Only decoder tests
pytest -m utils       # Only utility tests
pytest -m commands    # Only command tests
```

## Common Tasks

### Run Quick Sanity Check
```bash
python run_tests.py quick
```
Runs ~90 core tests in under 10 seconds.

### Check Test Coverage
```bash
python run_tests.py coverage
open htmlcov/index.html
```
Generates HTML coverage report showing which code is tested.

### Debug Failing Test
```bash
pytest tests/test_decoders.py::test_failing_test -v --tb=long
```
Shows detailed failure information.

### Run Tests in Watch Mode
```bash
pip install pytest-watch
ptw tests/
```
Automatically re-runs tests when files change.

## Troubleshooting

### "No module named pytest"
```bash
pip install pytest
```

### "ImportError: cannot import name 'OBD'"
Make sure you're in the project root directory and all modules are installed:
```bash
cd /path/to/pyobd
pip install -r requirements.txt
```

### Tests pass but real hardware fails
Tests use mocks - they verify code structure, not actual OBD communication.
For hardware testing, you'll need an actual OBD adapter.

### Slow tests
Run tests in parallel:
```bash
pip install pytest-xdist
pytest -n auto
```

## Next Steps

1. **Run all tests to verify setup:**
   ```bash
   python run_tests.py
   ```

2. **Check coverage:**
   ```bash
   python run_tests.py coverage
   ```

3. **Add new tests** as you add new features

4. **Run tests before committing** to catch regressions early

## Test Categories Explained

- **Decoders** (50+ tests): Test all OBD response decoders (temp, pressure, RPM, etc.)
- **Utils** (40+ tests): Test utility functions (hex conversion, BitArray, etc.)
- **Commands** (30+ tests): Test all 200+ OBD command definitions
- **Connection** (20+ tests): Test OBD connection management
- **Protocols** (25+ tests): Test protocol parsing (CAN, legacy, etc.)

## Expected Results

With everything working correctly, you should see:
```
✅ Decoder Tests PASSED
✅ Utility Tests PASSED
✅ Command Tests PASSED
✅ Connection Tests PASSED
✅ Protocol Tests PASSED

Passed: 5/5

✅ ALL TESTS PASSED!
```

Total: ~165 tests
Time: ~5-15 seconds (depending on your hardware)
Coverage: ~80%+

## Getting Help

- See full documentation: `tests/README.md`
- pytest docs: https://docs.pytest.org/
- Create an issue if tests fail unexpectedly
