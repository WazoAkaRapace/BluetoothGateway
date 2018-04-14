# BluetoothGateway

This is a homemade Bluetooth to MQTT Gateway, I use it to control BLE Lights and monitor a thermometer for my Homeassistant installation.
It's going to grow with the devices I'm gonna buy.


## Usage

``python BluetoothGateway.py`` and that's all.

## Requirements
- Awoxpy
- Bluepy
- paho-mqtt

## Configuration

### config.json : 
```
{
	"user": "Your_MQTT_Username",
	"password": "Your_MQTT_password",
	"host": "Your_MQTT_host",
	"devices": [
		{
			"mac": "BTLE Mac",
			"type": "xiaomiht",
            "refresh" : 300
		},
		{
			"mac": "BTLE Mac",
			"type": "awoxaroma"
		}
	]
}
```

### Working components : 
- xiaomiht : http://bit.ly/XMF_XMST
    - Battery level, temperature, humidity in json format are reported every `refresh` seconds on topic `sensor/{device_MAC}`
- awoxaroma : http://www.awox.com/awox_product/aromalight/
    - turn ON/OFF with payload `ON` or `OFF` on topic `light/{device_MAC}/state/set`
    - Change brightness level with payload `1 to 127` on topic `light/{device_MAC}/brightness/set`
    - Change white temperature with payload `153 to 500` on topic `light/{device_MAC}/white/set`
    - Change the color with payload `(0 to 255),(0 to 255),(0 to 255)` (Red,Green,Blue) on topic `light/{device_MAC}/color/set`
    - After each change, it report it state on the topic without the `/set` part.  

# TODO
- Clean component loading.
- Improve refresh time algorithm.
- Make Awox Aroma fan working. 


# Thanks

Home assistant : https://www.home-assistant.io/  
BLEA : https://www.jeedom.com/forum/viewforum.php?f=157