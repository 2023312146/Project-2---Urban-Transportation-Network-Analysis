import unittest
from project.data_structures.stop_entity import Stop, ZoneType

class TestStopEntity(unittest.TestCase):
    def test_stop_creation_and_properties(self):
        stop = Stop(1, 'A', 10.0, 20.0, ZoneType.RESIDENTIAL)
        self.assertEqual(stop.stop_ID, 1)
        self.assertEqual(stop.name, 'A')
        self.assertEqual(stop.latitude, 10.0)
        self.assertEqual(stop.longitude, 20.0)
        self.assertEqual(stop.zone_type, ZoneType.RESIDENTIAL)

    def test_zone_type_setter_and_type_error(self):
        stop = Stop(1, 'A', 0, 0, ZoneType.RESIDENTIAL)
        stop.zone_type = ZoneType.COMMERCIAL
        self.assertEqual(stop.zone_type, ZoneType.COMMERCIAL)
        with self.assertRaises(TypeError):
            stop.zone_type = 'NotAZoneType'

    def test_stop_eq_and_lt_and_hash(self):
        s1 = Stop(1, 'A', 0, 0, ZoneType.RESIDENTIAL)
        s2 = Stop(1, 'A', 0, 0, ZoneType.RESIDENTIAL)
        s3 = Stop(2, 'B', 0, 0, ZoneType.COMMERCIAL)
        self.assertEqual(s1, s2)
        self.assertNotEqual(s1, s3)
        self.assertTrue(s1 < s3)
        self.assertEqual(hash(s1), hash(s2))
        self.assertNotEqual(hash(s1), hash(s3))

    def test_stop_repr(self):
        stop = Stop(1, 'A', 0, 0, ZoneType.RESIDENTIAL)
        self.assertIn("Stop(ID=1, Name='A', Zone='Residential')", repr(stop))

    def test_stop_from_dict_normal(self):
        d = {'stop_id': '1', 'name': 'A', 'latitude': '10', 'longitude': '20', 'zone_type': 'Residential'}
        stop = Stop.from_dict(d)
        self.assertEqual(stop.stop_ID, 1)
        self.assertEqual(stop.zone_type, ZoneType.RESIDENTIAL)

    def test_stop_from_dict_case_and_unknown(self):
        d = {'stop_id': '2', 'name': 'B', 'latitude': '0', 'longitude': '0', 'zone_type': 'urban'}
        stop = Stop.from_dict(d)
        self.assertEqual(stop.zone_type, ZoneType.URBAN)
        d2 = {'stop_id': '3', 'name': 'C', 'latitude': '0', 'longitude': '0', 'zone_type': 'suburban'}
        stop2 = Stop.from_dict(d2)
        self.assertEqual(stop2.zone_type, ZoneType.RESIDENTIAL)
        d3 = {'stop_id': '4', 'name': 'D', 'latitude': '0', 'longitude': '0', 'zone_type': 'unknown'}
        stop3 = Stop.from_dict(d3)
        self.assertEqual(stop3.zone_type, ZoneType.MIXED)

    def test_stop_from_dict_missing_fields(self):
        d = {'stop_id': '5', 'name': 'E', 'latitude': '0', 'longitude': '0'}
        with self.assertRaises(KeyError):
            Stop.from_dict(d)

    def test_stop_zone_type_type_error(self):
        with self.assertRaises(TypeError):
            Stop(1, 'A', 0, 0, 'NotAZoneType')

    def test_zone_type_enum(self):
        self.assertEqual(ZoneType.RESIDENTIAL.value, 'Residential')
        self.assertEqual(ZoneType.COMMERCIAL.value, 'Commercial')
        self.assertEqual(ZoneType.INDUSTRIAL.value, 'Industrial')
        self.assertEqual(ZoneType.MIXED.value, 'Mixed')
        self.assertEqual(ZoneType.URBAN.value, 'Urban')

if __name__ == '__main__':
    unittest.main() 