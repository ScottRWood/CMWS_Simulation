from numpy import *
from pylab import *
from math import factorial

from Event import Event
from EventHandler import EventHandler
from Servers import Servers


class MMCC:
    """
    Class to simulate M/M/C/C system
    """

    def run(self, server_number: int, arrival_total: int):
        """
        Run simulation with specified parameters
        :param server_number: Number of servers
        :param arrival_total: Number of events
        """

        # Initialise Servers and EventHandler
        self.servers = Servers(server_number)
        self.events = EventHandler()

        # Create and add initial event
        starting_event = Event("arrival", 0)
        starting_event.departure_time -= starting_event.arrival_time
        starting_event.arrival_time = 0
        self.events.add(starting_event)

        # Run simulation until number of events handled
        self.arrival_number = 0

        while(self.arrival_number < arrival_total):

            # Iterate to next event and update simulation time
            current_event = self.events.next()
            self.simulation_time = current_event.time()

            # If arrival, update counter and add to appropriate list
            if current_event.event_type == "arrival":
                self.arrival_number += 1
                self.events.add(Event("arrival", current_event.time()))

                # If no servers free, block event
                if not self.servers.is_free():
                    self.events.block(current_event)
                    continue

                # Assign server to event
                current_event.served_by(self.servers.allocate())
                self.events.add(current_event)

            # If departure, free server and depart
            else:
                self.servers.deallocate(current_event.served_by())
                self.events.depart(current_event)

    def blocking_probability(self) -> float:
        """
        Obtain blocking probability of previous run
        :return: Blocking probability
        """
        return len(self.events.blocked)/self.arrival_number

    def server_utilisation(self) -> float:
        """
        Obtain server utilisation of previous run
        :return: Server utilisation
        """
        return sum([e.service_time() for e in self.events.departed]) / self.simulation_time


if __name__ == "__main__":

    def expected_blocking_probability(server_number: int, arrival_rate: float, departure_rate: float) -> float:
        """
        Calculate expected blocking probability via analytical methods
        :param server_number: Number of servers
        :param arrival_rate: Rate of arrival of events
        :param departure_rate: Rate of departure of events
        :return: Expected blocking probability
        """

        numerator = double(((arrival_rate / departure_rate)**server_number)/double(factorial(server_number)))
        denominator = sum( [((arrival_rate/departure_rate)**k)/factorial(k) for k in range(1,server_number)])
        return numerator / denominator

    def expected_server_utilisation(arrival_rate: float, departure_rate: float) -> float:
        """
        Calculate expected server utilisation via analytical methods
        :param arrival_rate: Rate of arrival of events
        :param departure_rate: Rate of departure of events
        :return: Expected server utilisation
        """
        return arrival_rate / departure_rate

    matplotlib.pyplot.show()
    machine = MMCC()

    # Initialise test parameters
    servers = 16
    arrival_range = linspace(0.01, 0.1, 100)

    departure_rate = 0.01
    clients = 10000

    # Lists to hold blocking rates
    simulation_blocking = []
    expected_blocking = []

    # Lists to hold utilisation rates
    simulation_utilisation = []
    expected_utilisation = []

    # Lists to hold outcomes
    simulation_arrival = []
    simulation_incomplete = []
    simulation_departed = []
    simulation_blocked = []

    # Simulation runs
    index = 0

    for i, arrival_rate in enumerate(arrival_range):
        Event.ARRIVAL_RATE = arrival_rate

        machine.run(server_number=servers, arrival_total=clients)

        probability = machine.blocking_probability()

        if probability < 0.01: index = i

        # Add simulation info to lists
        simulation_blocking.append(probability)
        expected_blocking.append(expected_blocking_probability(servers, arrival_rate, departure_rate))

        simulation_utilisation.append(machine.server_utilisation())
        expected_utilisation.append(expected_server_utilisation(arrival_rate, departure_rate))

        simulation_arrival.append(machine.arrival_number)
        simulation_incomplete.append(machine.arrival_number - (len(machine.events.departed) + len(machine.events.blocked)))
        simulation_departed.append(len(machine.events.departed))
        simulation_blocked.append(len(machine.events.blocked))

    # Best simulation with under 0.01 blocking
    print("Values for run on best arrival rate:")

    print("\tEvents Handled :")
    print("\t\tArrivals:", simulation_arrival[index])
    print("\t\tIncomplete:", simulation_incomplete[index])
    print("\t\tDepartures:", simulation_departed[index])
    print("\t\tBlocked:", simulation_blocked[index])

    print("\tBlocking rate:", simulation_blocking[index])
    print("\tServer Utilisation:", simulation_utilisation[index])
    print()

    # Info about investigation progress
    difference = [i - j for i, j in zip(simulation_blocking, expected_blocking)]
    print("For blocking rate below 0.01")
    print("\tArrival rate:", arrival_range[index])
    print("\tBlocking probability:", simulation_blocking[index])
    print("\tVariance from predictions:", sum(difference) / len(difference))

    # Plot blocking probability findings
    figure()
    plot(arrival_range, simulation_blocking, "b.", label="Simulation blocking percentage")
    plot(arrival_range, expected_blocking, "r--", label="Theoretical blocking percentage")
    plot([0.01, arrival_range[index]], [simulation_blocking[index]]*2, "g--", label="Best with probability under 0.01")
    plot([arrival_range[index]]*2, [-0.0005, simulation_blocking[index]], "g--")
    legend()
    ylabel("Blocking Probability")
    xlabel("Arrival Rate")
    xlim(0.01, 0.1)
    ylim(-0.0005,0.025)
    show(block=True)

    # Plot server utilisation findings
    figure()
    plot(arrival_range, simulation_utilisation, "b.", label="Server utilisation")
    plot(arrival_range, expected_utilisation, "r--", label="Predicted server utilisation")
    ylabel("Server Utilisation")
    xlabel("Arrival Rate")
    legend()
    xlim(0.01, 0.1)
    show(block=True)
