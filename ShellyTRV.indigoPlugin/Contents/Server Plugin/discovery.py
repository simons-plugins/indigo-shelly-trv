#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Equipment discovery for Shelly TRV devices from MQTT messages.

import logging


class EquipmentDiscovery:
    """Tracks discovered equipment from MQTT messages."""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("Plugin.Discovery")
        self.discovered = {}

    def process_message(self, coordinator_dev_id, topic_parts, payload):
        """Process an MQTT message and extract equipment discovery info.
        Returns list of newly discovered equipment dicts, or empty list.
        """
        if coordinator_dev_id not in self.discovered:
            self.discovered[coordinator_dev_id] = {
                "thermostats": {}
            }

        coord_equip = self.discovered[coordinator_dev_id]
        new_equipment = []

        if not isinstance(payload, (dict, list)):
            return new_equipment

        if len(topic_parts) < 2:
            return new_equipment

        # Extract device ID from topic parts (e.g., "shellytrv-8CF6811871C7")
        device_id = None
        for part in topic_parts:
            if part.startswith("shellytrv-"):
                device_id = part
                break

        if not device_id:
            return new_equipment

        # Check if this is an info message with thermostat data
        if topic_parts[-1] == "info" and isinstance(payload, dict):
            thermostats = payload.get("thermostats", [])
            if thermostats and isinstance(thermostats, list):
                if device_id not in coord_equip["thermostats"]:
                    coord_equip["thermostats"][device_id] = {
                        "name": f"Shelly TRV {device_id[-6:]}",
                        "id": device_id
                    }
                    new_equipment.append({
                        "type": "thermostat",
                        "id": device_id,
                        "name": f"Shelly TRV {device_id[-6:]}"
                    })

        # Check if this is a status message
        elif topic_parts[-1] == "status" and isinstance(payload, dict):
            if ("tmp" in payload and "target_t" in payload and
                device_id not in coord_equip["thermostats"]):
                coord_equip["thermostats"][device_id] = {
                    "name": f"Shelly TRV {device_id[-6:]}",
                    "id": device_id
                }
                new_equipment.append({
                    "type": "thermostat",
                    "id": device_id,
                    "name": f"Shelly TRV {device_id[-6:]}"
                })

        return new_equipment

    def get_summary(self, coordinator_dev_id):
        """Return a formatted summary of discovered equipment."""
        equip = self.discovered.get(coordinator_dev_id, {})
        lines = []
        for category, items in equip.items():
            if items:
                lines.append(f"  {category}:")
                for item_id, info in sorted(items.items()):
                    lines.append(f"    ID {item_id}: {info['name']}")
        return "\n".join(lines) if lines else "  No equipment discovered yet."
