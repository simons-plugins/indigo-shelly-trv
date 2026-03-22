#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Handler module for Shelly TRV sensor devices (battery, WiFi signal).


def process_sensor_message(topic_parts, payload, logger):
    """Parse MQTT message and extract sensor state updates.

    Returns list of (equipment_id, state_updates) tuples where
    state_updates is a list of dicts for updateStatesOnServer.
    """
    updates = []

    if not isinstance(payload, dict):
        return updates

    # Extract device ID from topic parts
    device_id = None
    for part in topic_parts:
        if part.startswith("shellytrv-"):
            device_id = part
            break

    if not device_id:
        return updates

    # Handle info messages with sensor data
    if topic_parts[-1] == "info":
        # Battery sensor
        if "bat" in payload:
            bat_data = payload["bat"]
            if isinstance(bat_data, dict):
                battery_id = f"{device_id}_battery"
                state_updates = []

                if "value" in bat_data:
                    battery_level = bat_data["value"]
                    state_updates.append({
                        "key": "sensorValue",
                        "value": battery_level,
                        "uiValue": f"{battery_level}%"
                    })

                if "voltage" in bat_data:
                    voltage = bat_data["voltage"]
                    state_updates.append({
                        "key": "batteryVoltage",
                        "value": voltage,
                        "uiValue": f"{voltage:.3f}V"
                    })

                if state_updates:
                    updates.append((battery_id, state_updates))

        # WiFi signal sensor
        wifi_sta = payload.get("wifi_sta", {})
        if "rssi" in wifi_sta:
            wifi_id = f"{device_id}_wifi"
            rssi = wifi_sta["rssi"]
            state_updates = [{
                "key": "sensorValue",
                "value": rssi,
                "uiValue": f"{rssi} dBm"
            }]
            updates.append((wifi_id, state_updates))

    # Handle status messages with battery data
    elif topic_parts[-1] == "status":
        if "bat" in payload:
            battery_id = f"{device_id}_battery"
            battery_level = payload["bat"]
            state_updates = [{
                "key": "sensorValue",
                "value": battery_level,
                "uiValue": f"{battery_level}%"
            }]
            updates.append((battery_id, state_updates))

    return updates