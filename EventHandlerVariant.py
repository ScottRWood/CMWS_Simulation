from EventHandler import EventHandler
from EventVariant import EventVariant


class EventHandlerVariant(EventHandler):
    """
    Variation of the EventHandler with modifications to accept two different paths.
    """

    def __init__(self):
        """
        Initialisation
        """
        self.upcoming = []
        self.departed = []
        self.blocked_handover = []
        self.blocked_newcall = []

    def start(self):
        """
        Add event of each type to event list
        """
        arrivals = [EventVariant("handover", "arrival", 0), EventVariant("newcall", "arrival", 0)]
        start_time = min([arrivals[0].time(), arrivals[1].time()])

        for e in arrivals:
            e.arrival_time = e.arrival_time - start_time
            e.departure_time = e.departure_time - start_time
            self.add(e)

    def block(self, event: EventVariant):
        """
        Block function to ensure event stored in correct list
        :param event: Event to be blocked
        """
        if event.path == "handover":
            self.blocked_handover.append(event)
        else:
            self.blocked_newcall.append(event)
