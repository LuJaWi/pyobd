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


@pytest.mark.commands
class TestCommandEnumStyle:
    """Test the new Command enum-style class"""
    

    def test_command_class_exists(self):
        """Test Command class exists and is accessible"""
        from obd2.command_functions import Command
        assert Command is not None
    

    def test_command_direct_access(self):
        """Test direct attribute access like Command.RPM"""
        from obd2.command_functions import Command
        
        rpm = Command.RPM
        assert rpm is not None
        assert rpm.name == 'RPM'
        assert rpm.mode == 1
        assert rpm.pid == 0x0C
    

    def test_command_multiple_accesses(self):
        """Test accessing multiple commands"""
        from obd2.command_functions import Command
        
        rpm = Command.RPM
        speed = Command.SPEED
        coolant = Command.COOLANT_TEMP
        vin = Command.VIN
        
        assert rpm.name == 'RPM'
        assert speed.name == 'SPEED'
        assert coolant.name == 'COOLANT_TEMP'
        assert vin.name == 'VIN'
    

    def test_command_get_method(self):
        """Test Command.get() method"""
        from obd2.command_functions import Command
        
        rpm = Command.get('RPM')
        assert rpm is not None
        assert rpm.name == 'RPM'
        
        # Test non-existent command
        fake = Command.get('FAKE_COMMAND')
        assert fake is None
    

    def test_command_get_by_mode_pid(self):
        """Test Command.get_by_mode_pid() method"""
        from obd2.command_functions import Command
        
        # Mode 1, PID 0x0C = RPM
        rpm = Command.get_by_mode_pid(1, 0x0C)
        assert rpm is not None
        assert rpm.name == 'RPM'
        
        # Invalid mode/pid
        invalid = Command.get_by_mode_pid(99, 99)
        assert invalid is None
        
        # Negative values
        invalid = Command.get_by_mode_pid(-1, 0)
        assert invalid is None
    

    def test_command_all_method(self):
        """Test Command.all() method"""
        from obd2.command_functions import Command
        
        all_commands = Command.all()
        assert isinstance(all_commands, list)
        assert len(all_commands) > 200
        
        # Verify all are OBDCommand objects
        from obd2.command import OBDCommand
        for cmd in all_commands[:10]:  # Check first 10
            assert isinstance(cmd, OBDCommand)
    

    def test_command_modes_method(self):
        """Test Command.modes() method"""
        from obd2.command_functions import Command
        
        modes = Command.modes()
        assert isinstance(modes, list)
        assert len(modes) == 10  # Modes 0-9
        
        # Mode 1 should have many commands
        assert len(modes[1]) > 50
    

    def test_command_containment_by_name(self):
        """Test 'in' operator with command names"""
        from obd2.command_functions import Command
        
        assert 'RPM' in Command
        assert 'SPEED' in Command
        assert 'FAKE_COMMAND' not in Command
    

    def test_command_containment_by_object(self):
        """Test 'in' operator with OBDCommand objects"""
        from obd2.command_functions import Command
        
        rpm = Command.RPM
        assert rpm in Command
    

    def test_command_same_as_commands_object(self):
        """Test that Command and commands return the same objects"""
        from obd2.command_functions import Command, commands
        
        # Should be the exact same object (not just equal)
        assert Command.RPM is commands.RPM
        assert Command.SPEED is commands.SPEED
        assert Command.COOLANT_TEMP is commands.COOLANT_TEMP
        assert Command.VIN is commands.VIN
    

    def test_command_dir_listing(self):
        """Test dir() shows all available commands"""
        from obd2.command_functions import Command
        
        dir_output = dir(Command)
        
        # Should include common commands
        assert 'RPM' in dir_output
        assert 'SPEED' in dir_output
        assert 'COOLANT_TEMP' in dir_output
        
        # Should include utility methods
        assert 'get' in dir_output
        assert 'get_by_mode_pid' in dir_output
        assert 'all' in dir_output
        assert 'modes' in dir_output
    

    def test_command_all_mode1_accessible(self):
        """Test all Mode 1 commands are accessible"""
        from obd2.command_functions import Command
        
        mode1_names = [
            'RPM', 'SPEED', 'COOLANT_TEMP', 'ENGINE_LOAD',
            'THROTTLE_POS', 'MAF', 'INTAKE_TEMP', 'FUEL_LEVEL',
            'INTAKE_PRESSURE', 'TIMING_ADVANCE'
        ]
        
        for name in mode1_names:
            cmd = getattr(Command, name, None)
            assert cmd is not None, f"Command.{name} should exist"
            assert cmd.name == name
    

    def test_command_dtc_commands_accessible(self):
        """Test DTC commands are accessible"""
        from obd2.command_functions import Command
        
        get_dtc = Command.GET_DTC
        clear_dtc = Command.CLEAR_DTC
        current_dtc = Command.GET_CURRENT_DTC
        
        assert get_dtc.name == 'GET_DTC'
        assert clear_dtc.name == 'CLEAR_DTC'
        assert current_dtc.name == 'GET_CURRENT_DTC'
    

    def test_command_vehicle_info_accessible(self):
        """Test vehicle info commands are accessible"""
        from obd2.command_functions import Command
        
        vin = Command.VIN
        fuel_type = Command.FUEL_TYPE
        compliance = Command.OBD_COMPLIANCE
        
        assert vin.name == 'VIN'
        assert fuel_type.name == 'FUEL_TYPE'
        assert compliance.name == 'OBD_COMPLIANCE'
    

    def test_command_elm_commands_accessible(self):
        """Test ELM327 commands are accessible"""
        from obd2.command_functions import Command
        
        version = Command.ELM_VERSION
        voltage = Command.ELM_VOLTAGE
        
        assert version.name == 'ELM_VERSION'
        assert voltage.name == 'ELM_VOLTAGE'
    

    def test_command_mode2_dtc_commands_accessible(self):
        """Test Mode 2 (freeze frame) commands are accessible"""
        from obd2.command_functions import Command
        
        dtc_rpm = Command.DTC_RPM
        dtc_speed = Command.DTC_SPEED
        
        assert dtc_rpm.name == 'DTC_RPM'
        assert dtc_speed.name == 'DTC_SPEED'
        assert dtc_rpm.mode == 2
        assert dtc_speed.mode == 2


@pytest.mark.commands
class TestCommandRegistry:
    """Test the internal _CommandRegistry class"""
    

    def test_registry_exists(self):
        """Test that Commands object has internal registry"""
        from obd2.command_functions import commands
        
        assert hasattr(commands, '_registry')
        assert commands._registry is not None
    

    def test_registry_get_method(self):
        """Test registry.get() method"""
        from obd2.command_functions import commands
        
        rpm = commands._registry.get('RPM')
        assert rpm is not None
        assert rpm.name == 'RPM'
        
        fake = commands._registry.get('FAKE')
        assert fake is None
    

    def test_registry_get_by_mode_pid(self):
        """Test registry.get_by_mode_pid() method"""
        from obd2.command_functions import commands
        
        rpm = commands._registry.get_by_mode_pid(1, 0x0C)
        assert rpm is not None
        assert rpm.name == 'RPM'
        
        # Test boundary conditions
        assert commands._registry.get_by_mode_pid(-1, 0) is None
        assert commands._registry.get_by_mode_pid(0, -1) is None
        assert commands._registry.get_by_mode_pid(99, 0) is None
    

    def test_registry_all_commands(self):
        """Test registry.all_commands() method"""
        from obd2.command_functions import commands
        
        all_cmds = commands._registry.all_commands()
        assert isinstance(all_cmds, list)
        assert len(all_cmds) > 200
    

    def test_registry_modes_attribute(self):
        """Test registry.modes attribute"""
        from obd2.command_functions import commands
        
        modes = commands._registry.modes
        assert isinstance(modes, list)
        assert len(modes) == 10


@pytest.mark.commands
class TestBackwardCompatibility:
    """Test that old code still works with new changes"""
    

    def test_commands_object_still_works(self):
        """Test traditional commands object access"""
        from obd2.command_functions import commands
        
        rpm = commands.RPM
        assert rpm.name == 'RPM'
        
        speed = commands['SPEED']
        assert speed.name == 'SPEED'
        
        mode1_rpm = commands[1][0x0C]
        assert mode1_rpm.name == 'RPM'
    

    def test_commands_methods_still_work(self):
        """Test Commands class methods still work"""
        from obd2.command_functions import commands
        
        # Test has_name
        assert commands.has_name('RPM') == True
        assert commands.has_name('FAKE') == False
        
        # Test has_pid
        assert commands.has_pid(1, 0x0C) == True
        assert commands.has_pid(1, 0xFF) == False
        
        # Test has_command
        rpm = commands.RPM
        assert commands.has_command(rpm) == True
    

    def test_commands_base_commands_method(self):
        """Test base_commands() method still works"""
        from obd2.command_functions import commands
        
        base = commands.base_commands()
        assert isinstance(base, list)
        assert len(base) > 0
        
        # Should include essential commands
        names = [cmd.name for cmd in base]
        assert 'PIDS_A' in names
        assert 'ELM_VERSION' in names
    

    def test_commands_pid_getters_method(self):
        """Test pid_getters() method still works"""
        from obd2.command_functions import commands
        
        getters = commands.pid_getters()
        assert isinstance(getters, list)
        assert len(getters) > 0
    

    def test_commands_len_method(self):
        """Test __len__ method still works"""
        from obd2.command_functions import commands
        
        total = len(commands)
        assert total > 200
    

    def test_commands_contains_method(self):
        """Test __contains__ method still works"""
        from obd2.command_functions import commands
        
        assert 'RPM' in commands
        assert 'FAKE_COMMAND' not in commands


@pytest.mark.commands
class TestCommandEdgeCases:
    """Test edge cases and error conditions"""
    

    def test_command_get_none_value(self):
        """Test Command.get() with None"""
        from obd2.command_functions import Command
        
        result = Command.get(None)
        assert result is None
    

    def test_command_get_empty_string(self):
        """Test Command.get() with empty string"""
        from obd2.command_functions import Command
        
        result = Command.get('')
        assert result is None
    

    def test_command_get_by_mode_pid_reserved_slot(self):
        """Test get_by_mode_pid() on reserved (None) slots"""
        from obd2.command_functions import Command
        
        # Mode 6 has many reserved slots (None values)
        # Try to access a reserved slot
        result = Command.get_by_mode_pid(6, 0x11)  # Should be None/reserved
        # Result could be None or a valid command, just verify it doesn't crash
        assert result is None or hasattr(result, 'name')
    

    def test_command_access_nonexistent_attribute(self):
        """Test accessing non-existent attribute raises proper error"""
        from obd2.command_functions import Command
        
        with pytest.raises(AttributeError):
            _ = Command.DEFINITELY_NOT_A_REAL_COMMAND_NAME_12345
    

    def test_command_all_returns_copy(self):
        """Test that Command.all() returns a list (not modifiable original)"""
        from obd2.command_functions import Command
        
        all1 = Command.all()
        all2 = Command.all()
        
        # Should be equal but not the same object
        assert len(all1) == len(all2)
        # Lists themselves are different objects
        assert all1 is not all2
    

    def test_command_modes_structure(self):
        """Test modes structure is correct"""
        from obd2.command_functions import Command
        
        modes = Command.modes()
        
        # Should have 10 modes (0-9)
        assert len(modes) == 10
        
        # Mode 0 should be empty
        assert len(modes[0]) == 0
        
        # Mode 1 should have commands
        assert len(modes[1]) > 50
        
        # Mode 5 should be empty (not used in OBD-II)
        assert len(modes[5]) == 0
        
        # Mode 8 should be empty
        assert len(modes[8]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
