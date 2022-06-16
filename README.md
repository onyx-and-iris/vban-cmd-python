[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/onyx-and-iris/vban-cmd-python/blob/dev/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
![Tests Status](./tests/basic.svg?dummy=8484744)
![Tests Status](./tests/banana.svg?dummy=8484744)
![Tests Status](./tests/potato.svg?dummy=8484744)

# VBAN CMD

This package offers a Python interface for the Voicemeeter RT Packet Service as well as Voicemeeter VBAN-TEXT.

This allows a user to get (rt packets) and set (vban-text) parameters over a local network. Consider the Streamer View app over VBAN, for example.

It may be used standalone or to extend the [Voicemeeter Remote Python API](https://github.com/onyx-and-iris/voicemeeter-api-python)

For sending audio across a network with VBAN you will need to look elsewhere.

For an outline of past/future changes refer to: [CHANGELOG](CHANGELOG.md)

## Tested against

-   Basic 1.0.8.2
-   Banana 2.0.6.2
-   Potato 3.0.2.2

## Requirements

-   [Voicemeeter](https://voicemeeter.com/)
-   Python 3.11 or greater

## Installation

### `Pip`

Install vban-cmd package from your console

`pip install vban-cmd`

## `Use`

Simplest use case, use a context manager to request a VbanCmd class of a kind.

Login and logout are handled for you in this scenario.

#### `__main__.py`

```python
import vban_cmd


class ManyThings:
    def __init__(self, vban):
        self.vban = vban

    def things(self):
        self.vban.strip[0].label = "podmic"
        self.vban.strip[0].mute = True
        print(
            f"strip 0 ({self.vban.strip[0].label}) has been set to {self.vban.strip[0].mute}"
        )

    def other_things(self):
        info = (
            f"bus 3 gain has been set to {self.vban.bus[3].gain}",
            f"bus 4 eq has been set to {self.vban.bus[4].eq}",
        )
        self.vban.bus[3].gain = -6.3
        self.vban.bus[4].eq = True
        print("\n".join(info))


def main():
    with vban_cmd.api(kind_id, **opts) as vban:
        do = ManyThings(vban)
        do.things()
        do.other_things()

        # set many parameters at once
        vban.apply(
            {
                "strip-2": {"A1": True, "B1": True, "gain": -6.0},
                "bus-2": {"mute": True},
            }
        )


if __name__ == "__main__":
    kind_id = "banana"
    opts = {
        "ip": "<ip address>",
        "streamname": "Command1",
        "port": 6980,
    }

    main()
```

Otherwise you must remember to call `vban.login()`, `vban.logout()` at the start/end of your code.

## `kind_id`

Pass the kind of Voicemeeter as an argument. kind_id may be:

-   `basic`
-   `banana`
-   `potato`

## `Available commands`

### Channels (strip/bus)

The following properties exist for audio channels.

-   `mono`: boolean
-   `solo`: boolean
-   `mute`: boolean
-   `label`: string
-   `gain`: float, -60 to 12
-   `A1 - A5`, `B1 - B3`: boolean
-   `comp`: float, from 0.0 to 10.0
-   `gate`: float, from 0.0 to 10.0
-   `limit`: int, from -40 to 12

example:

```python
vban.strip[3].gain = 3.7
print(strip[0].label)

vban.bus[4].mono = true
```

### Command

Certain 'special' commands are defined by the API as performing actions rather than setting values. The following methods are available:

-   `show()` : Bring Voiceemeter GUI to the front
-   `shutdown()` : Shuts down the GUI
-   `restart()` : Restart the audio engine

The following properties are write only and accept boolean values.

-   `showvbanchat`: boolean
-   `lock`: boolean

example:

```python
vban.command.restart()
vban.command.showvbanchat = true
```

### Multiple parameters

-   `apply`
    Set many strip/bus parameters at once, for example:

```python
vban.apply(
    {
        "strip-2": {"A1": True, "B1": True, "gain": -6.0},
        "bus-2": {"mute": True},
    }
)
```

Or for each class you may do:

```python
vban.strip[0].apply(mute: true, gain: 3.2, A1: true)
vban.vban.outstream[0].apply(on: true, name: 'streamname', bit: 24)
```

## Config Files

`vban.apply_config(<configname>)`

You may load config files in TOML format.
Three example profiles have been included with the package. Remember to save
current settings before loading a profile. To set one you may do:

```python
import vban_cmd
with vban_cmd.api('banana') as vban:
    vban.apply_config('example')
```

will load a config file at configs/banana/example.toml for Voicemeeter Banana.

## `Base Module`

### VbanCmd class

#### `vban.pdirty`

True iff a parameter has been changed. Typically this is checked periodically to update states.

#### `vban.set_rt(id_, param, val)`

Sends a string request RT Packet where the command would take the form:

```python
f'{id_}.{param}={val}'
```

#### `vban.public_packet`

Returns a Voicemeeter rt data packet. Designed to be used internally by the interface but available for parsing through this read only property object. States may or may not be current, use the polling parameter pdirty to be sure.

### `Errors`

-   `errors.VMCMDErrors`: Base VMCMD error class.

### `Tests`

First make sure you installed the [development dependencies](https://github.com/onyx-and-iris/vban-cmd-python#installation)

Then from tests directory:

`pytest -v`

## Resources

-   [Voicemeeter VBAN TEXT](https://vb-audio.com/Voicemeeter/VBANProtocol_Specifications.pdf#page=19)

-   [Voicemeeter RT Packet Service](https://vb-audio.com/Voicemeeter/VBANProtocol_Specifications.pdf#page=27)
