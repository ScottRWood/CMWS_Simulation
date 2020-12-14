from Event import Event


class EventVariant(Event):
    """
    Variation of Event that adds a path to differentiate between new call and handover
    """
    # Arrival rates for different paths
    PRIORITIES = {"handover": 0.1, "newcall": 0.1}
    # Departure rate of events
    DEPARTURE_RATE = 0.01

    def __init__(self, path: str, event_type: str, time: float):
        """
        Initialisation
        :param path: handover or newcall
        :param event_type: type of event
        :param time: time of creation
        """
        self.path = path
        self.event_type = event_type
        self.arrival_time = time + Event.exponential(EventVariant.PRIORITIES[path])
        self.departure_time = self.arrival_time + Event.exponential(EventVariant.DEPARTURE_RATE)
