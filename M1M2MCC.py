from numpy import *
from pylab import *
from math import factorial

from EventVariant import EventVariant
from EventHandlerVariant import EventHandlerVariant
from MMCC import MMCC
from Servers import Servers


class M1M2MCC(MMCC):
    """
    Class to simulate M1/M2/M/C/C system
    """

    def run(self, total_servers: int, arrival_total: int, threshold: int):
        """
        Modified run function that adds threshold value
        :param total_servers: Number of servers
        :param arrival_total: Number of events
        :param threshold: Servers reserved for handover calls
        """

        # Setup servers, event handler and add first events
        self.servers = Servers(total_servers)
        self.events = EventHandlerVariant()
        self.events.start()

        # Start counter and iteration
        self.arrival_number = 0
        self.arrival = {"handover": 0, "newcall": 0}

        while(sum(self.arrival_number) < arrival_total):

            # Iterate to next event with handler and update sim time
            current_event = self.events.next()
            self.simulation_time = current_event.time()

            # If arrival, update counter and add to appropriate list
            if current_event.event_type == "arrival":
                priority = current_event.path
                self.arrival_number += 1
                self.arrival[priority] += 1

                self.events.add(EventVariant(priority, "arrival", current_event.time()))

                # Check server availability by priority and threshold
                if (len(self.servers) > threshold) or (priority == "handover" and self.servers.is_free()):
                    # Assign server to event
                    current_event.served_by(self.servers.allocate())
                    self.events.add(current_event)
                    continue

                # Arrival has been blocked
                self.events.block(current_event)

            # If departure, free server and depart event
            else:
                self.servers.deallocate(current_event.served_by())
                self.events.depart(current_event)

    def blocking_probability(self):
        """
        Obtain aggregated blocking probability of previous run
        :return: Blocking probability
        """

        HFP = len(self.events.blocked_handover) / self.arrival["handover"] \
            if self.arrival["handover"] else 0

        CBP = len(self.events.blocked_newcall) / self.arrival["newcall"] \
            if self.arrival["newcall"] else 0

        return CBP + (10 * HFP)


if __name__ == "__main__":

    def expected_blocking_probability(server_number: int, threshold: int, handover_arrival_rate: float,  newcall_arrival_rate: float, departure_rate: float) -> float:
        """
        Calculate expected blocking probability via analytical methods
        :param server_number: Number of servers
        :param threshold: Servers reserved for handovers
        :param handover_arrival_rate: Arrival rate of handover events
        :param newcall_arrival_rate: Arrival rate of newcall events
        :param departure_rate: Departure rate of events
        :return: Expected blocking probability
        """

        combined_arrival_rate = handover_arrival_rate + newcall_arrival_rate
        common_server_number = server_number - threshold

        # Compute first sum of P_zero
        P_zero_first = sum([(1/factorial(k)) *
                            ((combined_arrival_rate/departure_rate)**k)
                            for k in range(0, common_server_number+1)])

        # Use a loop for second sum
        P_zero_second = 0

        for k in range(common_server_number + 1, server_number + 1):
            a = 1/factorial(server_number - threshold)
            b = (combined_arrival_rate/departure_rate)**(common_server_number)
            c = 1/factorial(k - common_server_number)
            d = (handover_arrival_rate/departure_rate)**(k-common_server_number)
            P_zero_second += a*b*c*d

        # Obtain P_zero
        P_zero = (P_zero_first + P_zero_second)**(-1)

        P_loss_newcall = sum([ computePk(k, server_number, threshold, P_zero, handover_arrival_rate, newcall_arrival_rate, departure_rate) for k in range(common_server_number, server_number+1)])

        # Compute P_loss_handover
        w = 1/factorial(server_number - threshold)
        x = (combined_arrival_rate/departure_rate)**(common_server_number)
        y = 1/factorial(threshold)
        z = (handover_arrival_rate/departure_rate)**threshold
        P_loss_handover = w*x*y*z*P_zero

        expected_ABP = P_loss_newcall + 10 * P_loss_handover

        return expected_ABP

    def computePk(k: int, server_number: int, threshold: int, P_zero: double, handover_arrival_rate: float,  newcall_arrival_rate: float, departure_rate: float) -> float:
        """
        Compute Pk
        :param k: k value
        :param server_number: Number of servers
        :param threshold: Servers reserved for handovers
        :param P_zero: P_zero value
        :param handover_arrival_rate:  Arrival rate of handover events
        :param newcall_arrival_rate: Arrival rate of newcall events
        :param departure_rate: Departure rate of events
        :return: Pk
        """

        common_server_number = server_number - threshold
        combined_arrival_rate = handover_arrival_rate + newcall_arrival_rate

        if k <= common_server_number:
            Pk = 1/factorial(k)*((combined_arrival_rate/departure_rate)**k)*P_zero
            return Pk

        a  = 1/factorial(server_number - threshold)
        b  = (combined_arrival_rate/departure_rate)**common_server_number
        c  = 1 / factorial(k - (common_server_number))
        d  = (handover_arrival_rate/departure_rate)**(k - common_server_number)
        Pk = a*b*c*d*P_zero
        return Pk

    matplotlib.pyplot.show()
    machine = M1M2MCC()

    # Initialise test parameters
    handover_range = geomspace(0.000001, 0.1, 100)
    EventVariant.PRIORITIES["newcall"] = 0.1
    EventVariant.DEPARTURE_RATE = 0.01

    # Outcome lists
    simulation_blocking = []
    simulation_utilisation = []

    expected_blocking = []

    simulation_arrival = []
    simulation_incomplete = []
    simulation_departed = []
    simulation_handover_blocked = []
    simulation_newcall_blocked = []
    simulation_arrival_handover = []
    simulation_arrival_newcall = []

    for p in handover_range:
        EventVariant.PRIORITIES["handover"] = p
        machine.run(16, 10000, 2)

        simulation_blocking.append(machine.blocking_probability())
        simulation_utilisation.append(machine.server_utilisation())
        expected_blocking.append(expected_blocking_probability(16, 2, p, 0.1, 0.01))

    # Figure for handover range experiment
    figure()
    plot(handover_range, simulation_blocking, "b.", label="ABP blocking probability")
    plot(handover_range, expected_blocking, "r--", label="Theoretical blocking percentage")
    plot([handover_range[0], handover_range[-1]], [0.02]*2, \
         'g--', label="Target probability of 0.02")
    ylabel("ABP blocking probability")
    xlabel("Handover arrival rate")
    legend()
    xlim(handover_range[0], handover_range[-1])
    ylim(-0.005, 0.2)
    xscale("log")
    show(block=True)

    call_range = linspace(0.01, 0.1, 100)
    EventVariant.PRIORITIES["handover"] = 0.03
    EventVariant.DEPARTURE_RATE = 0.01

    simulation_blocking = []
    expected_blocking2 = []
    index, best_prob = 0, 0

    for i, c in enumerate(call_range):
        EventVariant.PRIORITIES["newcall"] = c
        machine.run(16, 10000, 2)
        prob = machine.blocking_probability()

        if prob < 0.02: index, best_prob = i, prob

        simulation_blocking.append(prob)
        expected_blocking2.append(expected_blocking_probability(16, 2, 0.03, c, 0.01))

        # Lists to hold outcomes for each value in arrival range
        simulation_arrival.append(machine.arrival_number)
        simulation_incomplete.append(machine.arrival_number - (len(machine.events.departed) + len(machine.events.blocked_handover) + len(machine.events.blocked_newcall)))
        simulation_departed.append(len(machine.events.departed))
        simulation_handover_blocked.append(len(machine.events.blocked_handover))
        simulation_newcall_blocked.append(len(machine.events.blocked_newcall))
        simulation_arrival_newcall.append(machine.arrival["newcall"])
        simulation_arrival_handover.append(machine.arrival["handover"])

    # Best run
    print("Values from run on best proposed new call arrival rate:")
    print("\tEvents Handled ::")
    print("\t\tArrivals:", simulation_arrival[index])
    print("\t\t\tOf which handovers:", simulation_arrival_handover[index])
    print("\t\t\tOf which new calls:", simulation_arrival_newcall[index])
    print("\t\tIncomplete:", simulation_incomplete[index])
    print("\t\tDepartures:", simulation_departed[index])
    print("\t\tBlocked handovers:", simulation_handover_blocked[index])
    print("\t\tBlocked new calls:", simulation_newcall_blocked[index])

    print("\tBlocking rate:", simulation_blocking[index])
    print("\tServer Utilisation:", simulation_utilisation[index])
    print()

    print("For Aggregated blocking rate below 0.02:")
    print("\tCall arrival value:", call_range[index])
    print("\tBlocking value:", best_prob)

    # Figure for arrival rate experiment
    figure()
    plot(call_range, simulation_blocking, "b.", label="ABP blocking probability")
    plot(call_range, expected_blocking2, "r--", label="Theoretical blocking percentage")
    plot([0.01, call_range[index]], [simulation_blocking[index]]*2, "g--", \
         label="Setup with probability under 0.02")
    plot([call_range[index]]*2, [-0.005, simulation_blocking[index]], "g--")
    ylabel("ABP blocking probability")
    xlabel("New call arrival rate")
    xlim(0.01,0.1)
    ylim(-0.005, 0.2)
    legend()
    show(block=True)
