from .iremote import IRemote


class MacroButton(IRemote):
    """A placeholder class in case this interface is being used interchangeably with the Remote API"""

    def __str__(self):
        return f"{type(self).__name__}{self._remote.kind}{self.index}"

    @property
    def identifier(self):
        return f"command.button[{self.index}]"

    @property
    def state(self) -> bool:
        self.logger.warning("button.state commands are not supported over VBAN")

    @state.setter
    def state(self, _):
        self.logger.warning("button.state commands are not supported over VBAN")

    @property
    def stateonly(self) -> bool:
        self.logger.warning("button.stateonly commands are not supported over VBAN")

    @stateonly.setter
    def stateonly(self, v):
        self.logger.warning("button.stateonly commands are not supported over VBAN")

    @property
    def trigger(self) -> bool:
        self.logger.warning("button.trigger commands are not supported over VBAN")

    @trigger.setter
    def trigger(self, _):
        self.logger.warning("button.trigger commands are not supported over VBAN")
