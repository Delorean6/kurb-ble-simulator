"""
schedule_engine.py
Parses schedule JSON and exposes helper functions.
Logic Simulator uses this internally.
"""

def parse_daily_limit(schedule_json):
    return schedule_json["daily_limit"]["max_unlocks"]


def parse_time_windows(schedule_json):
    return schedule_json["windows"]
