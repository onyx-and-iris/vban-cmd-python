## Requirements

-   [OBS Studio](https://obsproject.com/)
-   [OBS Python SDK for Websocket v5](https://github.com/aatikturk/obsws-python)

## About

Perhaps you have a streaming setup but you want to control OBS and Voicemeeter from a remote location with python installed.
With the vban-cmd and obsws-python packages you may sync a distant Voicemeeter with a distant OBS over LAN.

## Configure

This script assumes you have your OBS connection info saved in a config file named `config.toml`.

A valid `config.toml` file might look like this:

```toml
[connection]
host = "gamepc.local"
port = 4455
password = "mystrongpass"
```

It also assumes you have your VBAN connection info saved in a config file named `vban.toml`.

A valid `vban.toml` file might look like this:

```toml
[connection]
ip = "gamepc.local"
port = 6980
streamname = "Command1"
```

Both configs should be placed next to `__main__.py`.

The script also assumes four OBS scenes names "START", "BRB", "END" and "LIVE".

## Use

Make sure you have established a working connection to OBS and the remote Voicemeeter.

Run the script, change OBS scenes and watch Voicemeeter parameters change.

Pressing `<Enter>` will exit.

## Notes

This script can be run from a Linux host since the vban-cmd interface relies on UDP packets and obsws-python runs over websockets.

You could for example, set this up to run in the background on a home server such as a Raspberry Pi.

It requires Python 3.10+.
