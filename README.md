# Pigpio PWM Fan

Home Assistant custom `fan` platform that drives a PWM fan (e.g. a Noctua
5V PWM fan on a Raspberry Pi) through a [pigpio](https://abyz.me.uk/rpi/pigpio/)
daemon, typically running as a Home Assistant add-on.

## Requirements

- The [pigpio add-on](https://github.com/Poeschl-HomeAssistant-Addons/pigpio)
  (or any reachable `pigpiod`) installed and started.
- The fan's PWM control wire connected to the GPIO pin configured below
  (BCM numbering).

## Installation

Install via HACS as a custom repository, or copy
`custom_components/pigpio_fan` into your `config/custom_components`
directory, then restart Home Assistant.

## Configuration

Add to `configuration.yaml`:

```yaml
fan:
  - platform: pigpio_fan
    host: 68413af6-pigpio   # hostname of the pigpio add-on
    port: 8888
    fans:
      - name: "Fan Raspberry Pi"
        pin: 18              # BCM GPIO number, not the physical pin number
        unique_id: rpi_fan_noctua
        frequency: 25000     # Hz, 25kHz recommended by Noctua
```

`host` and `port` default to the values above (the standard hostname for
the `pigpio` add-on slug `68413af6_pigpio` and its default port), so they
can be omitted if unchanged.
