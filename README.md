# VBAN CMD
This package offers a Python interface for the [Voicemeeter RT Packet Service](https://vb-audio.com/Voicemeeter/VBANProtocol_Specifications.pdf). It allows a client to connect to a Voicemeeter installation on a remote machine
so long as a valid connection can be established between both systems, and VBAN is configured correctly. 
In similar fashion to the Remote API you can set and get parameters for strips/buses.

Tested against
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

Just the wrapper:
```
pip install .
```

With development dependencies:
```
pip install -e .['development']
```

#### Connection:
For sending a text request (remote set) several configuration options are available:
- `ip`: remote address
- `streamname`: default 'Command1'
- `port`: default 6990
- `bps`: bitrate of stream, default 0 should be safe for most cases.

pass these values as arguments to vban_cmd.connect() as show in the example below.

Regarding fetching data (remote get), the code registers itself to the RT Packet Service every 10 seconds,
with a timeout of 15 seconds (same as streamer view app).

#### Use with a context manager:
Unlike the Remote API the VBAN RT Packet service has no login limitations since receiving data requires
a client to simply register to the service. It is therefore advised to use this code only with a context manager.
Parameter coverage is not as extensive for the RT Packet Service as with the Remote API so defined below are the
classes/methods available through this package.

### Example 1
```python
import vban_cmd

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
    with vban_cmd.connect(kind_id, ip=ip) as vban:
        do = ManyThings(vban)
        do.things()
        do.other_things()

if __name__ == '__main__':
    kind_id = 'potato'
    ip = '<ip address>'

    main()
```

## API
### Kinds
A *kind* specifies a major Voicemeeter version. Currently this encompasses
- `basic`
- `banana`
- `potato`

#### `vban_cmd.connect(kind_id, ip=ip) -> '(VbanCmd)'`
Factory function for remotes.
- `ip`: remote pc you wish to send requests to.


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
Shows Voicemeeter if it's hide. No effect otherwise.
#### `vban.hide()`
Hides Voicemeeter if it's shown. No effect otherwise.
#### `vban.shutdown()`
Closes Voicemeeter.
#### `vban.restart()`
Restarts Voicemeeter's audio engine.

### `Strip`
The following properties are gettable and settable:
- `mono`: boolean
- `solo`: boolean
- `mute`: boolean
- `label`: string
- `gainlayer`: float, -60 to 12
- Output mapping (e.g. `A1`, `B3`, etc.): boolean, depends on the Voicemeeter kind

The following properties are settable:
- `comp`: float, from 0.0 to 10.0
- `gate`: float, from 0.0 to 10.0
- `limit`: int, from -40 to 12

### `Bus`
The following properties are gettable and settable:
- `mute`: boolean
- `mono`: boolean
- `eq`: boolean
- `eq_ab`: boolean
- `label`: string
- `gain`: float, -60 to 12

### `VbanCmd` (lower level)
#### `vban.public_packet`
Fetches an RT Data Packet (some values will still be in byte form).

#### `vban.set_rt(id_, param, val)`
Sends a string request RT Packet where the command would take the form:
```python
f'{id_}.{param}={val}'
```

### `Errors`
- `errors.VMCMDErrors`: Base VMCMD error class.

### `Tests`
First make sure you installed the [development dependencies](https://github.com/onyx-and-iris/vban-cmd-python#installation)

To run the tests from tests directory:

`nosetests --r test -v`

## Resources
- [Voicemeeter RT Packet Service](https://vb-audio.com/Voicemeeter/VBANProtocol_Specifications.pdf)
