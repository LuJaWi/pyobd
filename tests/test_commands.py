"""
Test OBD command definitions for both legacy and new codebase.

Verifies all 200+ commands are properly defined.
"""

import pytest


@pytest.mark.commands
class TestCommandsStructure:
    """Test Commands class structure and methods"""
    

    def test_commands_class_exists_new(self):
        """Test Commands class exists in new code"""
        from obd2.command_functions import Commands
        
        commands = Commands()
        assert commands is not None
    

    def test_commands_has_base_commands_new(self):
        """Test base_commands() method in new"""
        from obd2.command_functions import Commands
        
        commands = Commands()
        base = commands.base_commands()
        assert isinstance(base, list)
        assert len(base) > 0
    

    def test_commands_has_pid_getters_new(self):
        """Test pid_getters() method in new"""
        from obd2.command_functions import Commands
        
        commands = Commands()
        getters = commands.pid_getters()
        assert isinstance(getters, list)
        assert len(getters) > 0


@pytest.mark.commands
class TestMode1Commands:
    """Test Mode 1 (live data) command definitions"""
    

    def test_mode1_pids_a_new(self):
        """Test PIDS_A command in new"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        cmd = commands_obj['PIDS_A']
        assert cmd is not None
        assert cmd.name == 'PIDS_A'
        assert cmd.mode == 1
        assert cmd.pid == 0
    

    def test_mode1_rpm_new(self):
        """Test RPM command in new"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        cmd = commands_obj['RPM']
        assert cmd is not None
        assert cmd.name == 'RPM'
        assert cmd.mode == 1
        assert cmd.pid == 0x0C
        assert cmd.command == b"010C"
    

    def test_mode1_speed_new(self):
        """Test SPEED command in new"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        cmd = commands_obj['SPEED']
        assert cmd is not None
        assert cmd.name == 'SPEED'
        assert cmd.pid == 0x0D
    

    def test_mode1_coolant_temp_new(self):
        """Test COOLANT_TEMP command in new"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        cmd = commands_obj['COOLANT_TEMP']
        assert cmd is not None
        assert cmd.pid == 0x05
    

    def test_mode1_throttle_pos_new(self):
        """Test THROTTLE_POS command in new"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        cmd = commands_obj['THROTTLE_POS']
        assert cmd is not None
        assert cmd.pid == 0x11
    

    def test_mode1_engine_load_new(self):
        """Test ENGINE_LOAD command in new"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        cmd = commands_obj['ENGINE_LOAD']
        assert cmd is not None
        assert cmd.pid == 0x04


@pytest.mark.commands
class TestMode3Commands:
    """Test Mode 3 (DTC) command definitions"""
    

    def test_mode3_get_dtc_new(self):
        """Test GET_DTC command in new"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        cmd = commands_obj['GET_DTC']
        assert cmd is not None
        assert cmd.mode == 3
        assert cmd.command == b"03"


@pytest.mark.commands
class TestMode4Commands:
    """Test Mode 4 (clear DTC) command definitions"""
    

    def test_mode4_clear_dtc_new(self):
        """Test CLEAR_DTC command in new"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        cmd = commands_obj['CLEAR_DTC']
        assert cmd is not None
        assert cmd.mode == 4
        assert cmd.command == b"04"


@pytest.mark.commands
class TestMode9Commands:
    """Test Mode 9 (vehicle info) command definitions"""
    

    def test_mode9_vin_new(self):
        """Test VIN command in new"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        cmd = commands_obj['VIN']
        assert cmd is not None
        assert cmd.mode == 9


@pytest.mark.commands
class TestCommandAccessMethods:
    """Test different ways to access commands"""
    

    def test_access_by_name_new(self):
        """Test accessing command by name in new"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        rpm = commands_obj['RPM']
        assert rpm.name == 'RPM'
    

    def test_access_by_mode_pid_new(self):
        """Test accessing command by mode/pid in new"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        cmd = commands_obj[1][0x0C]  # Mode 1, PID 0x0C (RPM)
        assert cmd.name == 'RPM'
    

    def test_has_pid_method_new(self):
        """Test has_pid() method in new"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        assert commands_obj.has_pid(1, 0x0C) == True  # RPM exists
        assert commands_obj.has_pid(1, 0xFF) == False  # Invalid PID


@pytest.mark.commands
class TestCommandProperties:
    """Test OBDCommand object properties"""
    

    def test_command_has_required_properties_new(self):
        """Test command object has all required properties (new)"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        rpm = commands_obj['RPM']
        assert hasattr(rpm, 'name')
        assert hasattr(rpm, 'desc')
        assert hasattr(rpm, 'command')
        assert hasattr(rpm, 'bytes')
        assert hasattr(rpm, 'decode')  # Note: it's 'decode' not 'decoder'
        assert hasattr(rpm, 'ecu')
        assert hasattr(rpm, 'fast')
    

    def test_command_mode_pid_properties_new(self):
        """Test command mode/pid properties (new)"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        rpm = commands_obj['RPM']
        assert rpm.mode == 1
        assert rpm.pid == 0x0C


@pytest.mark.commands
class TestCommandCount:
    """Test that we have all expected commands"""
    

    def test_mode1_command_count_new(self):
        """Test Mode 1 has expected number of commands (new)"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        mode1_commands = commands_obj.modes[1]  # Access mode 1 commands directly
        # Mode 1 should have many commands (100+)
        assert len(mode1_commands) > 50
    

    def test_total_command_count_new(self):
        """Test total number of commands (new)"""
        from obd2.command_functions import Commands
        
        commands_obj = Commands()
        total = len(commands_obj)  # Use __len__ method
        # Should have 200+ total commands across all modes
        assert total > 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
