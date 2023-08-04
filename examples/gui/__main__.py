import logging

import vban_cmd

logging.basicConfig(level=logging.DEBUG)
import tkinter as tk
from tkinter import ttk


class App(tk.Tk):
    INDEX = 3

    def __init__(self, vban):
        super().__init__()
        self.vban = vban
        self.title(f"{vban} - version {vban.version}")
        self.vban.observer.add(self.on_ldirty)

        # create widget variables
        self.button_var = tk.BooleanVar(value=vban.strip[self.INDEX].mute)
        self.slider_var = tk.DoubleVar(value=vban.strip[self.INDEX].gain)
        self.meter_var = tk.DoubleVar(value=self._get_level())
        self.gainlabel_var = tk.StringVar(value=self.slider_var.get())

        # initialize style table
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Mute.TButton",
            foreground="#cd5c5c" if vban.strip[self.INDEX].mute else "#5a5a5a",
        )

        # create labelframe and grid it onto the mainframe
        self.labelframe = tk.LabelFrame(text=self.vban.strip[self.INDEX].label)
        self.labelframe.grid(padx=1)

        # create slider and grid it onto the labelframe
        slider = ttk.Scale(
            self.labelframe,
            from_=12,
            to_=-60,
            orient="vertical",
            variable=self.slider_var,
            command=lambda arg: self.on_slider_move(arg),
        )
        slider.grid(
            column=0,
            row=0,
        )
        slider.bind("<Double-Button-1>", self.on_button_double_click)

        # create level meter and grid it onto the labelframe
        level_meter = ttk.Progressbar(
            self.labelframe,
            orient="vertical",
            variable=self.meter_var,
            maximum=72,
            mode="determinate",
        )
        level_meter.grid(column=1, row=0)

        # create gainlabel and grid it onto the labelframe
        gainlabel = ttk.Label(self.labelframe, textvariable=self.gainlabel_var)
        gainlabel.grid(column=0, row=1, columnspan=2)

        # create button and grid it onto the labelframe
        button = ttk.Button(
            self.labelframe,
            text="Mute",
            style="Mute.TButton",
            command=lambda: self.on_button_press(),
        )
        button.grid(column=0, row=2, columnspan=2, padx=1, pady=2)

    # define callbacks

    def on_slider_move(self, *args):
        val = round(self.slider_var.get(), 1)
        self.vban.strip[self.INDEX].gain = val
        self.gainlabel_var.set(val)

    def on_button_press(self):
        self.button_var.set(not self.button_var.get())
        self.vban.strip[self.INDEX].mute = self.button_var.get()
        self.style.configure(
            "Mute.TButton", foreground="#cd5c5c" if self.button_var.get() else "#5a5a5a"
        )

    def on_button_double_click(self, e):
        self.slider_var.set(0)
        self.gainlabel_var.set(0)
        self.vban.strip[self.INDEX].gain = 0

    def _get_level(self):
        val = max(self.vban.strip[self.INDEX].levels.prefader)
        return 0 if self.button_var.get() else 72 + val - 12 + self.slider_var.get()

    def on_ldirty(self):
        self.meter_var.set(self._get_level())


def main():
    with vban_cmd.api("banana", ldirty=True) as vban:
        app = App(vban)
        app.mainloop()


if __name__ == "__main__":
    main()
