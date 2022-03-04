import tkinter as tk
from tkinter import ttk
from functools import partial
from typing import NamedTuple

import vbancmd
from vbancmd import kinds

class ExampleAppErrors(Exception):
    pass

class App(tk.Tk):
    """ Topmost Level of App """
    @classmethod
    def make(cls, kind: NamedTuple):
        """
        Factory function for App

        Returns an App class of a kind
        """
        APP_cls =  type(f'App{kind.name}', (cls,), {
            'name': kind.name,
            'ins': kind.ins,
            'outs': kind.outs,
            }
        )
        return APP_cls

    def __init__(self):
        super().__init__()
        self.title(f'Voicemeeter{self.name} Example Program')
        self.phys_in, self.virt_in = self.ins
        self.col = self.phys_in + self.virt_in
        self.row = 3
        self.w = {'Basic': 300, 'Banana': 600, 'Potato': 800}
        self.h = 150
        self.defaultsizes = {
            'Basic': f'{self.w[self.name]}x{self.h}',
            'Banana': f'{self.w[self.name]}x{self.h}',
            'Potato': f'{self.w[self.name]}x{self.h}',
        }
        self.geometry(self.defaultsizes[self.name])

        """ create tkinter variables, generate widgets and configure rows/cols """
        self.gains = {
            'strip': [tk.DoubleVar() for i in range(self.phys_in + self.virt_in)],
        }
        self.levels = {
            'strip': [tk.DoubleVar() for i in range(self.phys_in + self.virt_in)],
        }
        [self._make_single_channel(i, j) for i, j in enumerate(i for i in range(0, self.col*2, 2))]
        scales = [widget for widget in self.winfo_children() if isinstance(widget, tk.Scale)]
        [scale.bind('<Double-Button-1>', partial(self.reset_gain, index=i)) for i, scale in enumerate(scales)]

        """ configure grid """
        self.col_row_configure()

        """ initiate watchers/updaters """
        self.refresh_public_packet()
        [self.watch_levels(i) for i in range(self.col)]

    @property
    def id_(self):
        return 'strip'

    def _make_single_channel(self, i, j):
        """
        Creates a label, progressbar, scale, and mute
        """
        ttk.Label(self, text=f'{vban.strip[i].label}').grid(column=j, row=0, columnspan=2)

        ttk.Progressbar(self, maximum=72, orient='vertical', mode='determinate', variable=self.levels[self.id_][i]).grid(column=j, row=1)
        ttk.Scale(self, from_=12.0, to=-60.0, orient='vertical', variable=self.gains[self.id_][i], 
                    command=partial(self.scale_callback, index=i)).grid(column=j+1, row=1)

        ttk.Button(self, text='MUTE', 
            command=partial(self.toggle, 'mute', i), style=f'Mute{i}.TButton').grid(column=j, row=2, columnspan=2, sticky=(tk.W, tk.E))

    def scale_callback(self, *args, index=None):
        """ callback function for scale widgets """
        vban.strip[index].gain = self.gains[self.id_][index].get()

    def reset_gain(self, *args, index=None):
        """ reset gain to 0 when double click mouse """
        vban.strip[index].gain = 0
        self.gains[self.id_][index].set(0)

    def toggle(self, param, index):
        """ toggles a strip parameter """
        setattr(vban.strip[index], param, not getattr(vban.strip[index], param))

    def col_row_configure(self):
        [self.columnconfigure(i, weight=1) for i in range(self.col*2)]
        [child.grid_configure(padx=1, pady=1)
            for child in self.winfo_children()]


    """ 
    The following functions perform background tasks. Importantly the public packet is constantly updated
    allowing the vban_cmd interface to fetch updated values.
    """
    def refresh_public_packet(self):
        self.after(1, self.refresh_public_packet_step)

    def refresh_public_packet_step(self):
        """ updates public packet in the background """
        vban.public_packet = vban._get_rt()
        self.after(25, self.refresh_public_packet_step)

    def watch_levels(self, i):
        self.after(1, self.watch_levels_step, i)

    def watch_levels_step(self, i):
        val = vban.strip[i].levels.prefader[0] + vban.strip[i].gain
        self.levels[self.id_][i].set((0 if vban.strip[i].mute else 100 + (val-30)))
        self.after(20, self.watch_levels_step, i)


_apps  = {kind.id: App.make(kind) for kind in kinds.all}

def connect(kind_id: str) -> App:
    """ return App of the kind requested """
    try:
        APP_cls = _apps[kind_id]
        return APP_cls()
    except KeyError:
        raise ExampleAppErrors(f'Invalid kind: {kind_id}')


if __name__ == "__main__":
    kind_id = 'potato'
    opts = {
        # make sure VBAN is configured on remote machine then set IP accordingly
        'ip': 'ws.local',
        'streamname': 'Command1',
        'port': 6990,
    }

    with vbancmd.connect(kind_id, **opts) as vban:
        app = connect(kind_id)
        app.mainloop()
