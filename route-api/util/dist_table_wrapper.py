# route-api/util/dist_table_wrapper.py

class DistTableWrapper:
    def __init__(self, table, number_of_nodes):
        """
        Initialize the distance table wrapper.

        :param table: A 2D list representing the distance matrix.
        :param number_of_nodes: The number of nodes (size of one dimension of the matrix).
        """
        self.table = table
        self.number_of_nodes = number_of_nodes

        # Ensure that the table has the correct dimensions
        assert len(table) == number_of_nodes
        for row in table:
            assert len(row) == number_of_nodes

    def get_number_of_nodes(self):
        """
        Get the number of nodes in the table.

        :return: The number of nodes.
        """
        return self.number_of_nodes

    def __call__(self, from_idx, to_idx):
        """
        Get the distance between two nodes.

        :param from_idx: The index of the source node.
        :param to_idx: The index of the destination node.
        :return: The distance between the nodes.
        """
        if from_idx >= self.number_of_nodes or to_idx >= self.number_of_nodes:
            raise IndexError("Node index out of bounds")
        return self.table[from_idx][to_idx]

    def set_value(self, from_idx, to_idx, value):
        """
        Set the distance between two nodes.

        :param from_idx: The index of the source node.
        :param to_idx: The index of the destination node.
        :param value: The distance to set.
        """
        if from_idx >= self.number_of_nodes or to_idx >= self.number_of_nodes:
            raise IndexError("Node index out of bounds")
        self.table[from_idx][to_idx] = value

    def get_max_value_index(self):
        """
        Get the index of the maximum value in the distance table.

        :return: A tuple (from_idx, to_idx) of the nodes with the maximum distance.
        """
        max_value = float('-inf')
        max_from_idx = -1
        max_to_idx = -1

        for from_idx in range(self.number_of_nodes):
            for to_idx in range(self.number_of_nodes):
                if self.table[from_idx][to_idx] > max_value:
                    max_value = self.table[from_idx][to_idx]
                    max_from_idx = from_idx
                    max_to_idx = to_idx

        return max_from_idx, max_to_idx

    def size(self):
        """
        Get the size of the distance table.

        :return: The number of elements in the table (rows * columns).
        """
        return len(self.table) * len(self.table[0])
