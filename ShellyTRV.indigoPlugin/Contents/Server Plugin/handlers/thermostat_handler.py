#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Handler module for Shelly TRV thermostat devices.

import json
import indigo


def process_thermostat_message(topic_parts, payload, logger):
    """Parse MQTT message and extract thermostat state updates.

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

    state_updates = []

    # Handle info messages with thermostat data
    if topic_parts[-1] == "info":
        thermostats = payload.get("thermostats", [])
        if thermostats and isinstance(thermostats, list):
            thermostat = thermostats[0]  # Assuming single thermostat per device

            # Current temperature
            tmp = thermostat.get("tmp", {})
            if tmp.get("is_valid") and "value" in tmp:
                temp_c = tmp["value"]
                temp_f = temp_c * 9.0 / 5.0 + 32.0
                state_updates.append({
                    "key": "temperatureInput1",
                    "value": temp_f,
                    "uiValue": f"{temp_f:.1f} °F"
                })

            # Target temperature (setpoint)
            target_t = thermostat.get("target_t", {})
            if target_t.get("enabled") and "value" in target_t:
                setpoint_c = target_t["value"]
                setpoint_f = setpoint_c * 9.0 / 5.0 + 32.0
                state_updates.append({
                    "key": "setpointHeat",
                    "value": setpoint_f,
                    "uiValue": f"{setpoint_f:.1f} °F"
                })

            # HVAC mode based on enabled state
            if target_t.get("enabled"):
                state_updates.append({
                    "key": "hvacMode",
                    "value": indigo.kHvacMode.Heat
                })
            else:
                state_updates.append({
                    "key": "hvacMode",
                    "value": indigo.kHvacMode.Off
                })

            # Schedule state
            if "schedule" in thermostat:
                state_updates.append({
                    "key": "schedule",
                    "value": thermostat["schedule"]
                })

            # Window open detection
            if "window_open" in thermostat:
                state_updates.append({
                    "key": "windowOpen",
                    "value": thermostat["window_open"]
                })

            # Boost mode
            if "boost_minutes" in thermostat:
                boost_active = thermostat["boost_minutes"] > 0
                state_updates.append({
                    "key": "boostMode",
                    "value": boost_active
                })

    # Handle status messages
    elif topic_parts[-1] == "status":
        # Current temperature
        tmp = payload.get("tmp", {})
        if tmp.get("is_valid") and "value" in tmp:
            temp_c = tmp["value"]
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            state_updates.append({
                "key": "temperatureInput1",
                "value": temp_f,
                "uiValue": f"{temp_f:.1f} °F"
            })

        # Target temperature (setpoint)
        target_t = payload.get("target_t", {})
        if target_t.get("enabled") and "value" in target_t:
            setpoint_c = target_t["value"]
            setpoint_f = setpoint_c * 9.0 / 5.0 + 32.0
            state_updates.append({
                "key": "setpointHeat",
                "value": setpoint_f,
                "uiValue": f"{setpoint_f:.1f} °F"
            })

        # HVAC mode based on enabled state
        if target_t.get("enabled"):
            state_updates.append({
                "key": "hvacMode",
                "value": indigo.kHvacMode.Heat
            })
        else:
            state_updates.append({
                "key": "hvacMode",
                "value": indigo.kHvacMode.Off
            })

    if state_updates:
        updates.append((device_id, state_updates))

    return updates


def build_setpoint_payload(equipment_id, setpoint_f):
    """Build payload for setting thermostat setpoint."""
    setpoint_c = (setpoint_f - 32.0) * 5.0 / 9.0
    return {
        "target_t": {
            "enabled": True,
            "value": round(setpoint_c, 1)
        }
    }


def build_hvac_mode_payload(equipment_id, mode):
    """Build payload for setting HVAC mode."""
    enabled = mode != indigo.kHvacMode.Off
    return {
        "target_t": {
            "enabled": enabled
        }
    }