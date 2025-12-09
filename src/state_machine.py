"""
state_machine.py
Simple helpers for lock/unlock state changes.
"""

def is_locked(state):
    return state == 1

def is_unlocked(state):
    return state == 0
