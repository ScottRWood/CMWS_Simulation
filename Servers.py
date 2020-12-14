class Servers:
    """
    Manager for Servers
    """

    def __init__(self, server_number: int):
        """
        Initialise servers
        :param server_number: Number of servers
        """
        self.free = list(range(1, server_number+1))
        self.busy = []

    def __len__(self) -> int:
        """
        :return: Number of free servers
        """
        return len(self.free)

    def is_free(self) -> bool:
        """
        Check if any servers are free
        :return: True if a server is free, else false
        """
        return len(self) > 0

    def allocate(self) -> int:
        """
        Allocate server
        :return: Server ID
        """
        server, self.free = self.free[0], self.free[1:]
        self.busy.append(server)
        return server

    def deallocate(self, server: int):
        """
        Free server
        :param server: Server to deallocate
        """
        self.busy.remove(server)
        self.free.append(server)
