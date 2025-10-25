# turing-smart-screen-python - a Python system monitor and library for USB-C displays like Turing Smart Screen or XuanFang
# https://github.com/mathoudebine/turing-smart-screen-python/

# Copyright (C) 2021-2023  Matthieu Houdebine (mathoudebine)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Hybrid sensor implementation for Windows:
# - Uses LibreHardwareMonitor for GPU (better AMD/Nvidia support)
# - Uses psutil (Python) for CPU frequency and temperature (works better on newer CPUs)
# - Uses LibreHardwareMonitor for other sensors when available

import library.sensors.sensors_librehardwaremonitor as sensors_lhm
import library.sensors.sensors_python as sensors_python
from library.sensors import sensors
from typing import Tuple
from library.log import logger

# Use LHM for GPU (better support for AMD/Nvidia)
Gpu = sensors_lhm.Gpu

# Use LHM for Memory
Memory = sensors_lhm.Memory

# Use LHM for Disk (but it uses psutil internally anyway)
Disk = sensors_lhm.Disk

# Use LHM for Network
Net = sensors_lhm.Net


# Hybrid CPU implementation
class Cpu(sensors.Cpu):
    """
    Hybrid CPU sensor:
    - Uses psutil for frequency (better support for newer Intel CPUs like 14th gen)
    - Uses LibreHardwareMonitor for temperature when available
    - Uses psutil as fallback for temperature
    - Uses LibreHardwareMonitor for other metrics
    """
    
    # Cache detection results to avoid repeated checks
    _lhm_freq_works = None
    _lhm_temp_works = None
    
    @staticmethod
    def _check_lhm_frequency():
        """Check once if LHM can read CPU frequency"""
        if Cpu._lhm_freq_works is None:
            import math
            freq = sensors_lhm.Cpu.frequency()
            Cpu._lhm_freq_works = not math.isnan(freq)
            if not Cpu._lhm_freq_works:
                logger.info("CPU Frequency: Using psutil (LHM not available for this CPU)")
        return Cpu._lhm_freq_works
    
    @staticmethod
    def _check_lhm_temperature():
        """Check once if LHM can read CPU temperature"""
        if Cpu._lhm_temp_works is None:
            import math
            temp = sensors_lhm.Cpu.temperature()
            Cpu._lhm_temp_works = not math.isnan(temp)
            if not Cpu._lhm_temp_works:
                logger.info("CPU Temperature: Using psutil (LHM not available for this CPU)")
        return Cpu._lhm_temp_works
    
    @staticmethod
    def percentage(interval: float) -> float:
        # Use LHM for CPU percentage (more accurate)
        return sensors_lhm.Cpu.percentage(interval)
    
    @staticmethod
    def frequency() -> float:
        # Use cached detection to avoid repeated checks
        if Cpu._check_lhm_frequency():
            return sensors_lhm.Cpu.frequency()
        else:
            return sensors_python.Cpu.frequency()
    
    @staticmethod
    def load() -> Tuple[float, float, float]:
        # Use psutil for load average
        return sensors_python.Cpu.load()
    
    @staticmethod
    def is_temperature_available() -> bool:
        # Check if LHM can read temperature
        if sensors_lhm.Cpu.is_temperature_available():
            return True
        # Otherwise check psutil
        return sensors_python.Cpu.is_temperature_available()
    
    @staticmethod
    def temperature() -> float:
        # Use cached detection to avoid repeated checks
        if Cpu._check_lhm_temperature():
            return sensors_lhm.Cpu.temperature()
        else:
            # Try psutil first
            temp_psutil = sensors_python.Cpu.temperature()
            import math
            if not math.isnan(temp_psutil):
                return temp_psutil
            
            # Fallback: Use alternative temperature source from config
            try:
                from library import config
                from library.sensors.alternative_temp import get_alternative_temperature
                
                alt_source = config.CONFIG_DATA["config"].get("CPU_TEMP_ALTERNATIVE", "GPU_CORE")
                return get_alternative_temperature(alt_source)
            except:
                return math.nan
    
    @staticmethod
    def fan_percent(fan_name: str = None) -> float:
        # Use LHM for fan speed
        return sensors_lhm.Cpu.fan_percent(fan_name)

