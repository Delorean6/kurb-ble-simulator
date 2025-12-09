"""
BLE Peripheral Wrapper for Kurb Simulator
-----------------------------------------

This file defines the scaffolding for running the Kurb Logic Simulator
as a Bluetooth LE peripheral device.

IMPORTANT:
    • This is a template file.
    • Developers MUST fill in OS-specific BLE code for:
        - Advertising
        - GATT service creation
        - Characteristic read/write
        - Notifications

The logic simulator (kurb_logic.py) is already complete.
The job here is to bind BLE events ↔ logic functions.

Supported Operating Systems for BLE Peripheral Mode:
    ✔ Windows 10/11  → WinRT APIs
    ✔ Linux (Ubuntu, Debian, Raspberry Pi) → BlueZ + python-dbus
    ✖ macOS does NOT support BLE peripheral mode (OS limitation)

"""

import asyncio
import json
import time

from kurb_logic import KurbSimulator
from ble_constants import (
    SERVICE_UUID,
    CHAR_LOCK_STATE,
    CHAR_LOCK_COMMAND,
    CHAR_SCHEDULE,
    CHAR_TIMESYNC,
    CHAR_BATTERY,
    CHAR_NEXT_UNLOCK,
    CHAR_EVENT,
)

# -------------------------------------------------------------------
# Main BLE Wrapper Class
# -------------------------------------------------------------------

class KurbBLEPeripheral:
    """
    Wraps the KurbSimulator logic engine in a BLE peripheral interface.
    Developers must implement OS-specific BLE code in:
        - start_advertising()
        - stop_advertising()
        - send_notification()
        - set_characteristic_handlers()
    """

    def __init__(self):
        self.sim = KurbSimulator()

        # BLE characteristic value storage
        self.char_values = {
            CHAR_LOCK_STATE: bytes([self.sim.lock_state]),
            CHAR_BATTERY: bytes([self.sim.battery]),
            CHAR_NEXT_UNLOCK: bytes([0x00] * 4),  # placeholder
        }

        # These must be implemented by dev team
        self.ble_server = None
        self.device_connected = False

    # -------------------------------------------------------------------
    # BLE lifecycle
    # -------------------------------------------------------------------

    async def start(self):
        print("[BLE] Starting BLE peripheral wrapper...")
        await self.start_advertising()
        await self.set_characteristic_handlers()
        print("[BLE] Advertising as Kurb_V1_Sim")

        # Main loop for checking simulated battery drains or timers
        while True:
            await asyncio.sleep(1)

    async def stop(self):
        await self.stop_advertising()
        print("[BLE] Stopped BLE peripheral.")

    # -------------------------------------------------------------------
    # BLE API placeholders — devs MUST implement these
    # -------------------------------------------------------------------

    async def start_advertising(self):
        """
        OS-specific BLE code goes here.
        For Windows: use WinRT BluetoothLEAdvertisementPublisher.
        For Linux: use BlueZ D-Bus GattManager + LEAdvertisingManager.
        """
        raise NotImplementedError("BLE advertising not yet implemented.")

    async def stop_advertising(self):
        """ Stop BLE advertising. """
        raise NotImplementedError

    async def send_notification(self, uuid: str, data: bytes):
        """
        OS-specific notification logic.
        Called whenever the logic simulator triggers an event.
        """
        print(f"[BLE Notify] {uuid}: {data.hex()}")
        raise NotImplementedError

    async def set_characteristic_handlers(self):
        """
        Register read/write handlers with OS BLE library.
        For each characteristic UUID, define:
            - on_read(uuid)
            - on_write(uuid, data)
        """
        raise NotImplementedError

    # -------------------------------------------------------------------
    # BLE → Logic Write Handlers
    # -------------------------------------------------------------------

    async def on_write_lock_command(self, data: bytes):
        """
        Handles:
            0x02 → unlock request
            0x20 → unlink/reset
            0x10 → force unlock
        """
        cmd = data[0]
        print(f"[BLE] Received LockCommand: {cmd:#04x}")

        # Forward to logic
        await self.sim.on_write(CHAR_LOCK_COMMAND, data)

        # Push LockState update
        await self.send_notification(
            CHAR_LOCK_STATE, bytes([self.sim.lock_state])
        )

    async def on_write_schedule(self, data: bytes):
        print("[BLE] Received ScheduleConfig write")
        await self.sim.on_write(CHAR_SCHEDULE, data)

    async def on_write_timesync(self, data: bytes):
        print("[BLE] Received TimeSync write")
        await self.sim.on_write(CHAR_TIMESYNC, data)

    # -------------------------------------------------------------------
    # Logic → BLE Event Mapping
    # -------------------------------------------------------------------

    async def on_logic_event(self, event_code: bytes):
        """
        Whenever the logic simulator triggers an event (unlock, lock,
        fail-open, battery critical, etc.), we notify BLE clients.
        """
        print(f"[LOGIC EVENT] {event_code.hex()}")
        await self.send_notification(CHAR_EVENT, event_code)

        # Update LockState characteristic on lock/unlock events
        if event_code in [bytes([0x01]), bytes([0x02]), bytes([0x09])]:
            await self.send_notification(
                CHAR_LOCK_STATE, bytes([self.sim.lock_state])
            )

    # -------------------------------------------------------------------
    # GATT Read Handlers
    # -------------------------------------------------------------------

    async def on_read(self, uuid: str) -> bytes:
        """
        Developers attach this callback to OS BLE read handlers.
        """
        print(f"[BLE] read request for {uuid}")

        if uuid == CHAR_LOCK_STATE:
            return bytes([self.sim.lock_state])

        if uuid == CHAR_BATTERY:
            return bytes([self.sim.battery])

        if uuid == CHAR_NEXT_UNLOCK:
            # Placeholder until devs implement a real timestamp calculation
            return b"\x00\x00\x00\x00"

        if uuid == CHAR_SCHEDULE:
            if self.sim.schedule:
                raw = json.dumps(self.sim.schedule).encode()
                length = len(raw)
                return bytes([length]) + raw
            else:
                return bytes([0x00])

        return bytes([0x00])



# -------------------------------------------------------------------
# Main Entry Point
# -------------------------------------------------------------------

async def main():
    ble = KurbBLEPeripheral()

    try:
        await ble.start()
    except KeyboardInterrupt:
        print("\n[BLE] Keyboard interrupt received. Stopping...")
    finally:
        await ble.stop()


if __name__ == "__main__":
    asyncio.run(main())
