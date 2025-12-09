"""
battery_engine.py
Handles battery classification logic.
Used by BLE wrapper or logic simulator.
"""

def classify_battery(percent):
    if percent <= 3:
        return "emergency"
    elif percent <= 10:
        return "critical"
    elif percent <= 20:
        return "low"
    else:
        return "normal"
