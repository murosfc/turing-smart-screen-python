# Alternative temperature sources for CPU temperature display
# Allows using different hardware temperature sensors when CPU temp is not available

import math
import sys
import os

def get_alternative_temperature(source="GPU_CORE") -> float:
    """
    Get temperature from alternative sources.
    
    Available sources:
    - GPU_CORE: GPU Core temperature
    - GPU_MEMORY: GPU Memory temperature  
    - GPU_HOTSPOT: GPU Hot Spot temperature
    - MOTHERBOARD: Motherboard temperature (if available)
    - SYSTEM: Average of available temperatures
    
    Returns temperature in Celsius or math.nan if not available.
    """
    
    try:
        import clr
        lib_path = os.path.join(os.getcwd(), "external", "LibreHardwareMonitor")
        if lib_path not in sys.path:
            sys.path.append(lib_path)
        clr.AddReference(os.path.join(lib_path, "LibreHardwareMonitorLib.dll"))
        import LibreHardwareMonitor.Hardware as Hardware
        
        # Use existing handle if available, otherwise create one
        try:
            from library.sensors.sensors_librehardwaremonitor import handle
        except:
            # Create temporary handle for testing
            handle = Hardware.Computer()
            handle.IsCpuEnabled = True
            handle.IsGpuEnabled = True
            handle.IsMotherboardEnabled = True
            handle.Open()
        
        if source == "GPU_CORE":
            # Get GPU Core temperature
            for hardware in handle.Hardware:
                if hardware.HardwareType == Hardware.HardwareType.GpuAmd or \
                   hardware.HardwareType == Hardware.HardwareType.GpuNvidia or \
                   hardware.HardwareType == Hardware.HardwareType.GpuIntel:
                    hardware.Update()
                    for sensor in hardware.Sensors:
                        if sensor.SensorType == Hardware.SensorType.Temperature:
                            if "GPU Core" in str(sensor.Name) or "GPU Temperature" in str(sensor.Name):
                                if sensor.Value is not None:
                                    return float(sensor.Value)
        
        elif source == "GPU_MEMORY":
            # Get GPU Memory temperature
            for hardware in handle.Hardware:
                if hardware.HardwareType == Hardware.HardwareType.GpuAmd or \
                   hardware.HardwareType == Hardware.HardwareType.GpuNvidia:
                    hardware.Update()
                    for sensor in hardware.Sensors:
                        if sensor.SensorType == Hardware.SensorType.Temperature:
                            if "Memory" in str(sensor.Name):
                                if sensor.Value is not None:
                                    return float(sensor.Value)
        
        elif source == "GPU_HOTSPOT":
            # Get GPU Hot Spot temperature
            for hardware in handle.Hardware:
                if hardware.HardwareType == Hardware.HardwareType.GpuAmd or \
                   hardware.HardwareType == Hardware.HardwareType.GpuNvidia:
                    hardware.Update()
                    for sensor in hardware.Sensors:
                        if sensor.SensorType == Hardware.SensorType.Temperature:
                            if "Hot Spot" in str(sensor.Name):
                                if sensor.Value is not None:
                                    return float(sensor.Value)
        
        elif source == "MOTHERBOARD":
            # Get Motherboard temperature
            for hardware in handle.Hardware:
                if hardware.HardwareType == Hardware.HardwareType.Motherboard:
                    hardware.Update()
                    for subhardware in hardware.SubHardware:
                        subhardware.Update()
                        for sensor in subhardware.Sensors:
                            if sensor.SensorType == Hardware.SensorType.Temperature:
                                if sensor.Value is not None:
                                    return float(sensor.Value)
        
        elif source == "SYSTEM":
            # Get average of all available temperatures
            temps = []
            for hardware in handle.Hardware:
                hardware.Update()
                for sensor in hardware.Sensors:
                    if sensor.SensorType == Hardware.SensorType.Temperature and sensor.Value is not None:
                        temps.append(float(sensor.Value))
            
            if temps:
                return sum(temps) / len(temps)
    
    except Exception as e:
        pass
    
    return math.nan


if __name__ == "__main__":
    print("=== Testando Fontes Alternativas de Temperatura ===\n")
    
    sources = ["GPU_CORE", "GPU_MEMORY", "GPU_HOTSPOT", "MOTHERBOARD", "SYSTEM"]
    
    for source in sources:
        temp = get_alternative_temperature(source)
        if not math.isnan(temp):
            print(f"{source:20} -> {temp:.1f}°C")
        else:
            print(f"{source:20} -> Não disponível")

