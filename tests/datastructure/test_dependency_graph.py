import unittest
from datastructure.dependency_graph import DependencyGraphNode


class TestDependencyGraph(unittest.TestCase):
    @staticmethod
    def _gen_nodes(num_nodes: int):
        return list(DependencyGraphNode(i) for i in range(num_nodes))
