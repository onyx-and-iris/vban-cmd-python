# Simple Tkinter GUI
Since Tkinter is packaged with Python 3.9 for Windows you should be able to run this example with nothing more than
Python on your system.

This app demonstrates strips only across all three Voicemeeter versions with very limited control.

### Notes
Ensure VBAN is enabled and the TEXT incoming stream is configured and ON.
Since the vbancmd interface implements both the TEXT sub protocol and the RT Packet service it's possible that an incorrect configuration
may result in odd behaviour, such as getters working but setters not. For example, you may see the levels change but be unable to effect
the gain sliders when moving them.
