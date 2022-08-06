[![PyPI version](https://badge.fury.io/py/vban-cmd.svg)](https://badge.fury.io/py/vban-cmd)
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
            f"strip 0 ({self.vban.strip[0].label}) mute has been set to {self.vban.strip[0].mute}"
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

### Strip

The following properties are available.

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
```

##### Gainlayers

-   `gain`: float, from -60.0 to 12.0

example:

```python
vm.strip[3].gainlayer[3].gain = 3.7
```

Gainlayers are defined for potato version only.

##### Levels

The following properties are available.

-   `prefader`

example:

```python
print(vm.strip[3].levels.prefader)
```

Level properties will return -200.0 if no audio detected.

### Bus

The following properties are available.

-   `mono`: boolean
-   `eq`: boolean
-   `eq_ab`: boolean
-   `mute`: boolean
-   `label`: string
-   `gain`: float, -60 to 12

example:

```python
vban.bus[4].eq = true
print(vm.bus[0].label)
```

##### Modes

The following properties are available.

-   `normal`: boolean
-   `amix`: boolean
-   `bmix`: boolean
-   `composite`: boolean
-   `tvmix`: boolean
-   `upmix21`: boolean
-   `upmix41`: boolean
-   `upmix61`: boolean
-   `centeronly`: boolean
-   `lfeonly`: boolean
-   `rearonly`: boolean

The following methods are available.

-   `get()`: Returns the current bus mode

example:

```python
vm.bus[4].mode.amix = True

print(vm.bus[2].mode.get())
```

##### Levels

The following properties are available.

-   `all`

example:

```python
print(vm.bus[0].levels.all)
```

`levels.all` will return -200.0 if no audio detected.

### Command

Certain 'special' commands are defined by the API as performing actions rather than setting values. The following methods are available:

-   `show()` : Bring Voiceemeter GUI to the front
-   `shutdown()` : Shuts down the GUI
-   `restart()` : Restart the audio engine
-   `reset()`: Applies the `reset` config. (phys strip B1, virt strip A1, gains, comp, gate 0.0, mute, mono, solo, eq false)

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
Three example configs have been included with the package. Remember to save
current settings before loading a user config. To set one you may do:

```python
import vban_cmd
with vban_cmd.api('banana') as vban:
    vban.apply_config('example')
```

will load a config file at configs/banana/example.toml for Voicemeeter Banana.

## `Base Module`

### VbanCmd class

`vban_cmd.api(kind_id: str, **opts: dict)`

You may pass the following optional keyword arguments:

-   `ip`: str, ip or hostname of remote machine
-   `streamname`: str, name of the stream to connect to.
-   `port`: int=6980, vban udp port of remote machine.
-   `subs`: dict={"pdirty": True, "ldirty": False}, controls which updates to listen for.
    -   `pdirty`: parameter updates
    -   `ldirty`: level updates

#### Event updates

To receive event updates you should do the following:

-   register your app to receive updates using the `vban.subject.add(observer)` method, where observer is your app.
-   define an `on_update(subject)` callback function in your app. The value of subject may be checked for the type of update.

See `examples/observer` for a demonstration.

Level updates are considered high volume, by default they are NOT listened for.

Each of the update types may be enabled/disabled separately.

example:

```python
import vban_cmd
# Listen for level updates
opts = {
    "ip": "<ip address>",
    "streamname": "Command1",
    "port": 6980,
    "subs": {"ldirty": True},
}
with vban_cmd.api('banana', **opts) as vban:
    ...
```

#### `vban.event`

You may also add/remove event subscriptions as necessary with the Event class.

example:

```python
vban.event.add("ldirty")

vban.event.remove("pdirty")

# get a list of currently subscribed
print(vban.event.get())
```

#### `vban.pdirty`

True iff a parameter has been changed.

#### `vban.ldirty`

True iff a level value has been changed.

#### `vban.sendtext(script)`

Sends a script block as a string request, for example:

```python
vban.sendtext("Strip[0].Mute=1;Bus[0].Mono=1")
```

#### `vban.public_packet`

Returns a Voicemeeter rt data packet object. Designed to be used internally by the interface but available for parsing through this read only property object. States not guaranteed to be current (requires use of dirty parameters to confirm).

### `Errors`

-   `errors.VMCMDErrors`: Base VMCMD error class.

### `Tests`

First make sure you installed the [development dependencies](https://github.com/onyx-and-iris/vban-cmd-python#installation)

Then from tests directory:

`pytest -v`

## Resources

-   [Voicemeeter VBAN TEXT](https://vb-audio.com/Voicemeeter/VBANProtocol_Specifications.pdf#page=19)

-   [Voicemeeter RT Packet Service](https://vb-audio.com/Voicemeeter/VBANProtocol_Specifications.pdf#page=27)
