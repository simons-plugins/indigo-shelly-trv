# CLAUDE.md — Shelly TRV Plugin

Indigo home automation plugin for Shelly TRV (Thermostatic Radiator Valve) devices.

## Overview

This plugin automatically discovers and manages Shelly TRV devices via MQTT. It provides thermostat control and sensor monitoring for battery level and WiFi signal strength.

## Generated Device Types

| Device Type | Purpose | Auto-Created |
|-------------|---------|--------------|
| **Coordinator** | Manages MQTT connection to broker | Yes (single instance) |
| **Thermostat** | TRV temperature control and monitoring | Yes (per TRV device) |
| **Sensor** | Battery level and WiFi signal monitoring | Yes (per sensor type) |

## MQTT Topic Mapping

The plugin listens to these MQTT topic patterns:

- `shellies/shellytrv-{DEVICE_ID}/info` — Complete device information including thermostat data, battery, WiFi status
- `shellies/shellytrv-{DEVICE_ID}/status` — Temperature and setpoint updates

## Device Discovery

Equipment is automatically discovered from MQTT messages:
- **TRV Thermostat**: Detected from `thermostats[]` array in info messages or `tmp`/`target_t` fields in status messages
- **Battery Sensor**: Created when battery data (`bat`) is detected
- **WiFi Signal Sensor**: Created when WiFi RSSI data (`wifi_sta.rssi`) is detected

## Thermostat Features

- **Temperature Monitoring**: Current room temperature from TRV sensor
- **Setpoint Control**: Set target temperature (°F, converted to °C for device)
- **HVAC Mode**: Heat/Off based on thermostat enabled state
- **Schedule Status**: Shows if schedule mode is active
- **Window Detection**: Reports if open window is detected
- **Boost Mode**: Shows if boost heating is active

## Actions Available

### Thermostat Actions
- **Set Heat Setpoint**: Change target temperature
- **Set HVAC Mode**: Enable/disable heating (Heat/Off)

## Configuration

Configure MQTT broker connection in Plugin Configuration:
- **Broker Host**: MQTT broker IP/hostname (default: localhost)
- **Broker Port**: MQTT broker port (default: 1883)
- **Username/Password**: Optional MQTT authentication
- **Root Topic**: MQTT root topic (default: shellies)
- **Device Folder**: Indigo folder for auto-created devices
- **Debug Logging**: Enable verbose logging
- **Log MQTT**: Log all MQTT message traffic

## Installation Notes

1. Ensure paho-mqtt is installed in the plugin's Packages/ directory
2. Configure MQTT broker settings to match your Shelly device configuration
3. Devices will be auto-discovered and created when MQTT messages are received
4. Use "Discover Equipment" menu item to see discovered devices

## Technical Details

- **Bundle ID**: `com.simons-plugins.indigo-shelly-trv`
- **Version**: 2026.0.0
- **Coordinator Pattern**: Single coordinator manages all MQTT communication
- **Auto-Discovery**: Child devices created automatically on message receipt
- **Temperature Units**: Converts between Celsius (device) and Fahrenheit (Indigo)
- **Message Routing**: Handlers process messages by device category

## Troubleshooting

- Check MQTT broker connectivity in coordinator device status
- Enable "Log MQTT" to see message flow
- Use "Discover Equipment" menu to verify device discovery
- Check that Shelly TRV devices are publishing to expected MQTT topics
- Verify MQTT topic structure matches expected patterns

## Generated Files Structure

```
ShellyTRV.indigoPlugin/
├── Contents/
│   ├── Info.plist                    # Plugin metadata
│   └── Server Plugin/
│       ├── plugin.py                 # Main coordinator and routing
│       ├── mqtt_handler.py           # Generic MQTT thread handler
│       ├── discovery.py              # Equipment discovery from MQTT
│       ├── handlers/                 # Message processing handlers
│       │   ├── __init__.py
│       │   ├── thermostat_handler.py # TRV thermostat processing
│       │   └── sensor_handler.py     # Battery/WiFi sensor processing
│       ├── Devices.xml               # Device type definitions
│       ├── Actions.xml               # Available actions
│       ├── PluginConfig.xml          # Plugin configuration UI
│       └── MenuItems.xml             # Plugin menu items
└── .github/workflows/                # CI/CD automation
    ├── version-check.yml             # Version conflict checking
    └── create-release.yml            # Release automation
```