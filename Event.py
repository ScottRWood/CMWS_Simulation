from numpy import log
import random


class Event:
    """
    Class representing an event in the simulation
    """

    # Arrival rate of events
    ARRIVAL_RATE = 0.1
    # Departure rate of events
    DEPARTURE_RATE = 0.01

    def exponential(mean: float) -> float:
        """
        Calc exponential distribution around given mean
        """
        return - (log(random.random()) / mean)

    def __init__(self, event_type: str, time: float):
        """
        Initialisation
        :param event_type: Type of event
        :param time: Time of creation
        """

        self.event_type = event_type
        self.arrival_time = time + Event.exponential(Event.ARRIVAL_RATE)
        self.departure_time = self.arrival_time + Event.exponential(Event.DEPARTURE_RATE)

    def __str__(self) -> str:
        """
        :return: String representation of event
        """
        return self.event_type + " event at time: " + str(self.time())

    def time(self) -> float:
        """
        :return: Time value
        """
        if self.event_type == "arrival":
            return self.arrival_time
        return self.departure_time

    def service_time(self) -> float:
        """
        Calculate service time
        :return: Service time
        """
        return self.departure_time - self.arrival_time

    def served_by(self, server_id=None):
        """
        Return ID of allocated server or assign the server
        :param server_id: Server to assign task to
        :return: Server ID or None
        """
        if server_id:
            self.event_type = "Departure"
            self.server_id = server_id
            return
        return self.server_id
