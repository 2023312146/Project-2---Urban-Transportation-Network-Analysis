from project.data_structures.stop_entity import ZoneType

class TrafficConditionManager:
    """
    交通状况管理器，根据时段调整各区域的拥堵状态、等待时间和运行速度。
    """
    PEAK_MORNING = "Morning rush hour"
    NORMAL = "Ordinary hours" 
    PEAK_EVENING = "Evening rush hour"

    # 区域类型
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED = "mixed"

    # 高峰期等待时间预置
    PEAK_WAIT_TIMES = {
        PEAK_MORNING: {
            RESIDENTIAL: 4,  # 2+2
            COMMERCIAL: 4,
            INDUSTRIAL: 3,
            MIXED: 3,
        },
        PEAK_EVENING: {
            RESIDENTIAL: 2,
            COMMERCIAL: 6,  # 4+2
            INDUSTRIAL: 5,  # 3+2
            MIXED: 3,
        },
        NORMAL: {
            RESIDENTIAL: 2,
            COMMERCIAL: 4,
            INDUSTRIAL: 3,
            MIXED: 3,
        }
    }

    # 高峰期速度预置
    PEAK_SPEEDS = {
        PEAK_MORNING: {
            "congested": 15,
            "normal": 23
        },
        PEAK_EVENING: {
            "congested": 15,
            "normal": 23
        },
        NORMAL: {
            "congested": 23,
            "normal": 23
        }
    }

    def __init__(self):
        self.period = self.NORMAL
        self.base_speed = 23
        self.congestion_wait_time = 2 
        self.congestion_speed = 15   

    def set_period(self, period: str):
        """
        设置当前时段。
        """
        if period not in [self.PEAK_MORNING, self.NORMAL, self.PEAK_EVENING]:
            raise ValueError(f"无效的时段: {period}")
        self.period = period

    def get_area_congestion(self, area_type: str):
        """
        判断指定区域类型在当前时段是否拥堵。
        """
        if self.period == self.PEAK_MORNING:
            return area_type.lower() == self.RESIDENTIAL
        elif self.period == self.PEAK_EVENING:
            return area_type.lower() in [self.COMMERCIAL, self.INDUSTRIAL]
        return False

    def get_wait_time(self, area_type: str):
        """
        获取指定区域类型的当前等待时间。
        """
        area_type = area_type.lower()
        wait_times = self.PEAK_WAIT_TIMES.get(self.period, self.PEAK_WAIT_TIMES[self.NORMAL])
        return wait_times.get(area_type, wait_times[self.MIXED])

    def get_speed(self, area_type: str, is_entering_or_leaving_peak_area=False):
        if is_entering_or_leaving_peak_area and self.period in [self.PEAK_MORNING, self.PEAK_EVENING]:
            return self.PEAK_SPEEDS[self.period]["congested"]
        return self.PEAK_SPEEDS[self.period]["normal"]

    def get_current_period(self):
        return self.period 

    def get_edge_speed(self, from_area_type: str, to_area_type: str):
        if self.get_area_congestion(from_area_type) or self.get_area_congestion(to_area_type):
            return self.PEAK_SPEEDS[self.period]["congested"]
        return self.PEAK_SPEEDS[self.period]["normal"] 