[![PyPI version](https://badge.fury.io/py/vban-cmd.svg)](https://badge.fury.io/py/vban-cmd)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/onyx-and-iris/vban-cmd-python/blob/dev/LICENSE)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
![Tests Status](./tests/basic.svg?dummy=8484744)
![Tests Status](./tests/banana.svg?dummy=8484744)
![Tests Status](./tests/potato.svg?dummy=8484744)

# VBAN CMD

This python interface allows you to transmit Voicemeeter parameters over a network.

It may be used standalone or to extend the [Voicemeeter Remote Python API](https://github.com/onyx-and-iris/voicemeeter-api-python)

There is no support for audio transfer in this package, only parameters.

For an outline of past/future changes refer to: [CHANGELOG](CHANGELOG.md)

## Tested against

-   Basic 1.0.8.8
-   Banana 2.0.6.8
-   Potato 3.0.2.8

## Requirements

-   [Voicemeeter](https://voicemeeter.com/)
-   Python 3.10 or greater

## Installation

`pip install vban-cmd`

## `Use`

#### Connection

Load VBAN connection info from toml config. A valid `vban.toml` might look like this:

```toml
[connection]
ip = "gamepc.local"
port = 6980
streamname = "Command1"
```

It should be placed in \<user home directory\> / "Documents" / "Voicemeeter" / "configs"

Alternatively you may pass `ip`, `port`, `streamname` as keyword arguments.

#### `__main__.py`

Simplest use case, use a context manager to request a VbanCmd class of a kind.

Login and logout are handled for you in this scenario.

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
        self.vban.bus[3].gain = -6.3
        self.vban.bus[4].eq.on = True
        info = (
            f"bus 3 gain has been set to {self.vban.bus[3].gain}",
            f"bus 4 eq has been set to {self.vban.bus[4].eq.on}",
        )
        print("\n".join(info))


def main():
    KIND_ID = "banana"

    with vban_cmd.api(
        KIND_ID, ip="gamepc.local", port=6980, streamname="Command1"
    ) as vban:
        do = ManyThings(vban)
        do.things()
        do.other_things()

        # set many parameters at once
        vban.apply(
            {
                "strip-2": {"A1": True, "B1": True, "gain": -6.0},
                "bus-2": {"mute": True, "eq": {"on": True}},
                "vban-in-0": {"on": True},
            }
        )


if __name__ == "__main__":
    main()
```

Otherwise you must remember to call `vban.login()`, `vban.logout()` at the start/end of your code.

## `KIND_ID`

Pass the kind of Voicemeeter as an argument. KIND_ID may be:

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
-   `limit`: int, from -40 to 12

example:

```python
vban.strip[3].gain = 3.7
print(vban.strip[0].label)
```

The following methods are available.

-   `appgain(name, value)`: string, float, from 0.0 to 1.0

Set the gain in db by value for the app matching name.

-   `appmute(name, value)`: string, bool

Set mute state as value for the app matching name.

example:

```python
vban.strip[5].appmute("Spotify", True)
vban.strip[5].appgain("Spotify", 0.5)
```

##### Strip.Comp

The following properties are available.

-   `knob`: float, from 0.0 to 10.0
-   `gainin`: float, from -24.0 to 24.0
-   `ratio`: float, from 1.0 to 8.0
-   `threshold`: float, from -40.0 to -3.0
-   `attack`: float, from 0.0 to 200.0
-   `release`: float, from 0.0 to 5000.0
-   `knee`: float, from 0.0 to 1.0
-   `gainout`: float, from -24.0 to 24.0
-   `makeup`: boolean

example:

```python
print(vban.strip[4].comp.knob)
```

Strip Comp properties are defined as write only.

`knob` defined for all versions, all other parameters potato only.

##### Strip.Gate

The following properties are available.

-   `knob`: float, from 0.0 to 10.0
-   `threshold`: float, from -60.0 to -10.0
-   `damping`: float, from -60.0 to -10.0
-   `bpsidechain`: int, from 100 to 4000
-   `attack`: float, from 0.0 to 1000.0
-   `hold`: float, from 0.0 to 5000.0
-   `release`: float, from 0.0 to 5000.0

example:

```python
vban.strip[2].gate.attack = 300.8
```

Strip Gate properties are defined as write only, potato version only.

`knob` defined for all versions, all other parameters potato only.

##### Strip.Denoiser

The following properties are available.

-   `knob`: float, from 0.0 to 10.0

strip.denoiser properties are defined as write only, potato version only.

##### Strip.EQ

The following properties are available.

-   `on`: boolean
-   `ab`: boolean

Strip EQ properties are defined as write only, potato version only.

##### Gainlayers

-   `gain`: float, from -60.0 to 12.0

example:

```python
vban.strip[3].gainlayer[3].gain = 3.7
```

Gainlayers are defined for potato version only.

##### Levels

The following properties are available.

-   `prefader`

example:

```python
print(vban.strip[3].levels.prefader)
```

Level properties will return -200.0 if no audio detected.

### Bus

The following properties are available.

-   `mono`: boolean
-   `mute`: boolean
-   `label`: string
-   `gain`: float, -60 to 12

example:

```python
print(vban.bus[0].label)
```

##### Bus.EQ

The following properties are available.

-   `on`: boolean
-   `ab`: boolean

```python
vban.bus[4].eq.on = true
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
vban.bus[4].mode.amix = True

print(vban.bus[2].mode.get())
```

##### Levels

The following properties are available.

-   `all`

example:

```python
print(vban.bus[0].levels.all)
```

`levels.all` will return -200.0 if no audio detected.

### Strip | Bus

The following methods are available.

-   `fadeto(amount, time)`: float, int
-   `fadeby(amount, time)`: float, int

Modify gain to or by the selected amount in db over a time interval in ms.

example:

```python
vban.strip[0].fadeto(-10.3, 1000)
vban.bus[3].fadeby(-5.6, 500)
```

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
        "strip-0": {"A1": True, "B1": True, "gain": -6.0},
        "bus-1": {"mute": True, "mode": "composite"},
        "bus-2": {"eq": {"on": True}},
        "vban-in-0": {"on": True},
    }
)
```

Or for each class you may do:

```python
vban.strip[0].apply({"mute": True, "gain": 3.2, "A1": True})
vban.vban.outstream[0].apply({"on": True, "name": "streamname", "bit": 24})
```

## Config Files

`vban.apply_config(<configname>)`

You may load config files in TOML format.
Three example configs have been included with the package. Remember to save
current settings before loading a user config. To load one you may do:

```python
import vban_cmd
with vban_cmd.api('banana') as vban:
    vban.apply_config('example')
```

will load a config file at configs/banana/example.toml for Voicemeeter Banana.

Your configs may be located in one of the following paths:
-   \<current working directory\> / "configs" / kind_id
-   \<user home directory\> / ".config" / "vban-cmd" / kind_id
-   \<user home directory\> / "Documents" / "Voicemeeter" / "configs" / kind_id

If a config with the same name is located in multiple locations, only the first one found is loaded into memory, in the above order.

#### `config extends`

You may also load a config that extends another config with overrides or additional parameters.

You just need to define a key `extends` in the config TOML, that names the config to be extended.

Three example 'extender' configs are included with the repo. You may load them with:

```python
import voicemeeterlib
with voicemeeterlib.api('banana') as vm:
    vm.apply_config('extender')
```

## Events

Level updates are considered high volume, by default they are NOT listened for. Use `subs` keyword arg to initialize event updates.

example:

```python
import vban_cmd
opts = {
    "ip": "<ip address>",
    "streamname": "Command1",
    "port": 6980,
}
with vban_cmd.api('banana', ldirty=True, **opts) as vban:
    ...
```

#### `vban.subject`

Use the Subject class to register an app as event observer.

The following methods are available:

-   `add`: registers an app as an event observer
-   `remove`: deregisters an app as an event observer

example:

```python
# register an app to receive updates
class App():
    def __init__(self, vban):
        vban.subject.add(self)
        ...
```

#### `vban.event`

Use the event class to toggle updates as necessary.

The following properties are available:

-   `pdirty`: boolean
-   `ldirty`: boolean

example:

```python
vban.event.ldirty = True

vban.event.pdirty = False
```

Or add, remove a list of events.

The following methods are available:

-   `add()`
-   `remove()`
-   `get()`

example:

```python
vban.event.remove(["pdirty", "ldirty"])

# get a list of currently subscribed
print(vban.event.get())
```

## VbanCmd class

`vban_cmd.api(kind_id: str, **opts)`

You may pass the following optional keyword arguments:

-   `ip`: str, ip or hostname of remote machine
-   `streamname`: str, name of the stream to connect to.
-   `port`: int=6980, vban udp port of remote machine.
-   `pdirty`: boolean=False, parameter updates
-   `ldirty`: boolean=False, level updates
-   `timeout`: int=5, amount of time (seconds) to wait for an incoming RT data packet (parameter states).
-   `outbound`: boolean=False, set `True` if you are only interested in sending commands. (no rt packets will be received)

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

Returns a `VbanRtPacket`. Designed to be used internally by the interface but available for parsing through this read only property object. 

States not guaranteed to be current (requires use of dirty parameters to confirm).

## Errors

-   `errors.VBANCMDError`: Base VBANCMD Exception class.
-   `errors.VBANCMDConnectionError`: Exception raised when connection/timeout errors occur.

## Logging

It's possible to see the messages sent by the interface's setters and getters, may be useful for debugging.

example:
```python
import vban_cmd

logging.basicConfig(level=logging.DEBUG)

opts = {"ip": "ip.local", "port": 6980, "streamname": "Command1"}
with vban_cmd.api('banana', **opts) as vban:
        ...
```

## Tests

First make sure you installed the [development dependencies](https://github.com/onyx-and-iris/vban-cmd-python#installation)

Then from tests directory:

`pytest -v`

## Resources

-   [Voicemeeter VBAN TEXT](https://vb-audio.com/Voicemeeter/VBANProtocol_Specifications.pdf#page=19)

-   [Voicemeeter RT Packet Service](https://vb-audio.com/Voicemeeter/VBANProtocol_Specifications.pdf#page=27)
