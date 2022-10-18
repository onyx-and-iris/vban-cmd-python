## About

Registers a class as an observer and defines a callback.

## Configure

The script assumes you have connection info saved in a config file named `vban.toml` placed next to `__main__.py`.

A valid `vban.toml` might look like this:

```toml
[connection]
ip = "gamepc.local"
port = 6980
streamname = "Command1"
```

It should be placed next to `__main__.py`.

## Use

Make sure you have established a working VBAN connection.

Run the script, then:

-   change GUI parameters to trigger pdirty
-   play audio through any bus to trigger ldirty

Pressing `<Enter>` will exit.
