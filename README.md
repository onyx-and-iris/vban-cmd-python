[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/onyx-and-iris/vban-cmd-python/blob/dev/LICENSE)
# VBAN CMD
This package offers a Python interface for [Voicemeeter VBAN TEXT](https://vb-audio.com/Voicemeeter/VBANProtocol_Specifications.pdf#page=19) as well as the [Voicemeeter RT Packet Service](https://vb-audio.com/Voicemeeter/VBANProtocol_Specifications.pdf#page=27) which allows a client to send and receive parameter values over a local network.

It may be used standalone or to extend the [Voicemeeter Remote Python API](https://github.com/onyx-and-iris/voicemeeter-api-python)

For sending audio across a network with VBAN you will need to look elsewhere.

## Tested against
- Basic 1.0.8.1
- Banana 2.0.6.1
- Potato 3.0.2.1

## Prerequisites
- Voicemeeter 1 (Basic), 2 (Banana) or 3 (Potato)
- Python 3.9+

## Installation
```
git clone https://github.com/onyx-and-iris/vban-cmd-python
cd vban-cmd-python
```

Just the interface:
```
pip install .
```

With development dependencies:
```
pip install -e .['development']
```

#### Use with a context manager:
Parameter coverage is not as extensive for the RT Packet Service as with the Remote API.

### Example 1
```python
import vbancmd

class ManyThings:
    def __init__(self, vban):
        self.vban = vban

    def things(self):
        # Set the mapping of the second input strip
        self.vban.strip[1].A3 = True
        print(f'Output A3 of Strip {self.vban.strip[1].label}: {self.vban.strip[1].A3}')

    def other_things(self):
        # Toggle mute for the leftmost output bus
        self.vban.bus[0].mute = not self.vban.bus[0].mute


def main():
    with vbancmd.connect(kind_id, ip=ip) as vban:
        do = ManyThings(vban)
        do.things()
        do.other_things()

if __name__ == '__main__':
    kind_id = 'potato'
    ip = '<ip address>'

    main()
```

#### Or perform setup/teardown independently:
for example:

### Example 2
```python
import vbancmd

kind_id = 'potato'
ip = '<ip address>'

vban = vbancmd.connect(kind_id, ip=ip)

# call login() at the start of your code
vban.login()

# Toggle mute for leftmost input strip
vban.strip[0].mute = not vban.strip[0].mute

# Toggle eq for leftmost output bus
vban.bus[0].eq = not vban.bus[0].eq

# call logout() at the end of your code
vban.logout()
```

## API
### Kinds
A *kind* specifies a major Voicemeeter version. Currently this encompasses
- `basic`
- `banana`
- `potato`

#### `vbancmd.connect(kind_id, **kwargs) -> '(VbanCmd)'`
Factory function for remotes. Keyword arguments include:
- `ip`: remote pc you wish to send requests to.
- `streamname`: default 'Command1'
- `port`: default 6990
- `channel`: from 0 to 255
- `bps`: bitrate of stream, default 0 should be safe for most cases.


### `VbanCmd` (higher level)
#### `vban.type`
The kind of the Voicemeeter instance.
#### `vban.version`
A tuple of the form `(v1, v2, v3, v4)`.

#### `vban.strip`
An `InputStrip` tuple, containing both physical and virtual.
#### `vban.bus`
An `OutputBus` tuple, containing both physical and virtual.


#### `vban.show()`
Shows Voicemeeter if it's hidden. No effect otherwise.
#### `vban.hide()`
Hides Voicemeeter if it's shown. No effect otherwise.
#### `vban.shutdown()`
Closes Voicemeeter.
#### `vban.restart()`
Restarts Voicemeeter's audio engine.

#### `vban.apply(mapping)`
Updates values through a dict.  
Example:
```python
vban.apply({
    'strip-2': dict(A1=True, B1=True, gain=-6.0),
    'bus-2': dict(mute=True),
})
```


### `Strip`
The following properties are gettable and settable:
- `mono`: boolean
- `solo`: boolean
- `mute`: boolean
- `label`: string
- `gain`: float, -60 to 12
- Output mapping (e.g. `A1`, `B3`, etc.): boolean, depends on the Voicemeeter kind


The following properties are settable:
- `comp`: float, from 0.0 to 10.0
- `gate`: float, from 0.0 to 10.0
- `limit`: int, from -40 to 12

#### `gainlayer`
- `gainlayer[j].gain`: float, -60 to 12

for example:
```python
# set and get the value of the second input strip, fourth gainlayer
vban.strip[1].gainlayer[3].gain = -6.3
print(vban.strip[1].gainlayer[3].gain)
```
Gainlayers defined for Potato version only.

### `Bus`
The following properties are gettable and settable:
- `mute`: boolean
- `mono`: boolean
- `eq`: boolean
- `eq_ab`: boolean
- `label`: string
- `gain`: float, -60 to 12

#### `mode`
Bus modes are gettable and settable
- `normal`, `amix`, `bmix`, `repeat`, `composite`, `tvmix`, `upmix21`,
- `upmix41`, `upmix61`, `centeronly`, `lfeonly`, `rearonly`

for example:
```python
# set leftmost bus mode to tvmix
vban.bus[0].mode.tvmix = True
```

### `VbanCmd` (lower level)
#### `vban.set_rt(id_, param, val)`
Sends a string request RT Packet where the command would take the form:
```python
f'{id_}.{param}={val}'
```

#### `vban._get_rt()`
Used for updating the RT data packet, used internally by the Interface.
```python
vban.public_packet = vban._get_rt()
```

#### `vban.sendtext(cmd)`
Sends a multi parameter TEXT string command, for example:
```python
# Use ';' or ',' for delimiters.
vban.sendtext('Strip[0].Mute=1;Strip[3].A3=0;Bus[2].Mute=0;Bus[3].Eq.On=1')
```

### `Errors`
- `errors.VMCMDErrors`: Base VMCMD error class.

### `Tests`
First make sure you installed the [development dependencies](https://github.com/onyx-and-iris/vban-cmd-python#installation)

To run the tests from tests directory:

`nosetests --r test -v`

## Resources
- [Voicemeeter RT Packet Service](https://vb-audio.com/Voicemeeter/VBANProtocol_Specifications.pdf)
