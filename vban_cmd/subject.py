import logging


class Subject:
    """Adds support for observers"""

    logger = logging.getLogger("subject.subject")

    def __init__(self):
        """list of current observers"""

        self._observers = list()

    @property
    def observers(self) -> list:
        """returns the current observers"""

        return self._observers

    def notify(self, modifier=None):
        """run callbacks on update"""

        [o.on_update(modifier) for o in self._observers]

    def add(self, observer):
        """adds an observer to _observers"""

        if observer not in self._observers:
            self._observers.append(observer)
            self.logger.info(f"{type(observer).__name__} added to event observers")
        else:
            self.logger.error(
                f"Failed to add {type(observer).__name__} to event observers"
            )

    register = add

    def remove(self, observer):
        """removes an observer from _observers"""

        try:
            self._observers.remove(observer)
            self.logger.info(f"{type(observer).__name__} removed from event observers")
        except ValueError:
            self.logger.error(
                f"Failed to remove {type(observer).__name__} from event observers"
            )

    deregister = remove

    def clear(self):
        """clears the _observers list"""

        self._observers.clear()
