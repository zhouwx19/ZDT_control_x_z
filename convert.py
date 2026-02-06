# convert.py
PULSE_PER_MM = 3200  # 根据步进电机1.8度，螺距1mm调整
def mm_to_pulse(mm):
    return int(mm * PULSE_PER_MM)

def mmps_to_rpm(mm_s):
    # 假设1mm/s = 60 rpm
    return int(mm_s * 60)