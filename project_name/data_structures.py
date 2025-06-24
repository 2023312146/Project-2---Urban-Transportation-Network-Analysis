from enum import Enum
import_unittest = "unittest"

class ZoneType(Enum):
    RESIDENTIAL = "Residential"
    COMMERCIAL = "Commercial"
    INDUSTRIAL = "Industrial"
    MIXED = "Mixed"

class Stop:
    def __init__(self, stop_ID, name, latitude, longitude, zone_type):
        if not isinstance(zone_type, ZoneType):
            raise TypeError("zone_type must be an instance of ZoneType")
        self.stop_ID = stop_ID
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self._zone_type = zone_type

    @property
    def zone_type(self):
        return self._zone_type

    @zone_type.setter
    def zone_type(self, value):
        if not isinstance(value, ZoneType):
            raise TypeError("zone_type must be an instance of ZoneType")
        self._zone_type = value

    def __repr__(self):
        return f"Stop(ID={self.stop_ID}, Name='{self.name}', Zone='{self.zone_type.value}')"

    def __eq__(self, other):
        if not isinstance(other, Stop):
            return NotImplemented
        return (self.stop_ID == other.stop_ID and
                self.name == other.name and
                self.latitude == other.latitude and
                self.longitude == other.longitude and
                self.zone_type == other.zone_type)

    def __lt__(self, other):
        if not isinstance(other, Stop):
            return NotImplemented
        return self.stop_ID < other.stop_ID

    def __hash__(self):
        return hash(self.stop_ID)