from Event import Event


class EventHandler:
    """
    Class to manage events of the simulation
    """

    def __init__(self):
        """
        Initialisation
        """
        self.upcoming = []
        self.departed = []
        self.blocked = []

    def add(self, event: Event):
        """
        Add event to handler
        :param event: Event to add
        """
        for i, e in enumerate(self.upcoming):
            if e.time() > event.time():
                self.upcoming.insert(i, event)
                return
        self.upcoming.append(event)

    def depart(self, event: Event):
        """
        Place departed event
        :param event: Event departing
        """
        self.departed.append(event)

    def block(self, event: Event):
        """
        Place blocked event
        :param event: Event being blocked
        """
        self.blocked.append(event)

    def next(self) -> Event:
        """
        Get next event to be handled and remove from list
        :return: Next event to be handled
        """
        e = self.upcoming[0]
        self.upcoming = self.upcoming[1:]
        return e
