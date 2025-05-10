import sqlite3
import uuid

from test_base import DatabaseTestBase
from src.database import database

class TestDatabaseCategoryQueries(DatabaseTestBase):
    """Tests for category-based database queries."""

    def setUp(self):
        """Set up test database with various sensor categories."""
        super().setUp()
        
        # Add sensors of different categories
        self.light_sensor_id = database.db_add_sensor("light1", "Living Room Light", "light", self.test_db_path)
        self.temp_sensor_id = database.db_add_sensor("temp1", "Living Room Temp", "temp", self.test_db_path)
        self.switch_sensor_id = database.db_add_sensor("switch1", "Kitchen Switch", "switch", self.test_db_path)
        self.door_sensor_id = database.db_add_sensor("door1", "Front Door", "door", self.test_db_path)
        self.radar_sensor_id = database.db_add_sensor("radar1", "Motion Sensor", "radar", self.test_db_path)

    def test_db_get_available_all_modules_ctrl(self):
        """Test retrieving modules for control (light, switch, door)."""
        modules = database.db_get_available_all_modules_ctrl(self.test_db_path)
        
        # Should include light, switch, and door sensors
        self.assertEqual(len(modules), 3)
        
        # Check categories
        categories = [module['category'] for module in modules]
        self.assertIn('light', categories)
        self.assertIn('switch', categories)
        self.assertIn('door', categories)
        self.assertNotIn('temp', categories)
        self.assertNotIn('radar', categories)

    def test_db_get_module_current_power_data(self):
        """Test retrieving current power data for modules."""
        # Add last_val data for light and switch sensors
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE sensors SET last_val = ? WHERE id = ?", ("1", self.light_sensor_id))
            cursor.execute("UPDATE sensors SET last_val = ? WHERE id = ?", ("0", self.switch_sensor_id))
        
        # Get power data
        power_data = database.db_get_module_current_power_data(self.test_db_path)
        
        # Should include light and switch sensors
        self.assertEqual(len(power_data), 2)
        
        # Check power values
        for module in power_data:
            if module['name'] == 'Living Room Light':
                self.assertEqual(module['power'], "1")
            elif module['name'] == 'Kitchen Switch':
                self.assertEqual(module['power'], "0")

    def test_db_get_sensors_by_category(self):
        """Test retrieving sensors by category."""
        # Get light sensors
        light_sensors = database.db_get_sensors_by_category('light', self.test_db_path)
        self.assertEqual(len(light_sensors), 1)
        self.assertIn('Living Room Light', light_sensors)
        
        # Get temperature sensors
        temp_sensors = database.db_get_sensors_by_category('temp', self.test_db_path)
        self.assertEqual(len(temp_sensors), 1)
        self.assertIn('Living Room Temp', temp_sensors)
        
        # Get door sensors
        door_sensors = database.db_get_sensors_by_category('door', self.test_db_path)
        self.assertEqual(len(door_sensors), 1)
        self.assertIn('Front Door', door_sensors)

    def test_db_get_module_type(self):
        """Test retrieving module type by client ID."""
        # Get module types
        light_type = database.db_get_module_type('light1', self.test_db_path)
        temp_type = database.db_get_module_type('temp1', self.test_db_path)
        door_type = database.db_get_module_type('door1', self.test_db_path)
        
        self.assertEqual(light_type, 'light')
        self.assertEqual(temp_type, 'temp')
        self.assertEqual(door_type, 'door')
        
        # Test non-existent client ID
        nonexistent_type = database.db_get_module_type('nonexistent', self.test_db_path)
        self.assertIsNone(nonexistent_type)

if __name__ == '__main__':
    unittest.main()