from __future__ import annotations
from typing import List, Set, Iterable, TypeVar


_T = TypeVar("_T")


class DependencyGraph():

    def __init__(self):
        self.nodes: Set[DependencyGraphNode[_T]] = set()
        self.num_nodes = 0

    def _copy(self) -> DependencyGraph:
        new_graph = DependencyGraph()
        new_nodes = dict()
        # Create new nodes, does not link them
        for old_node in self.nodes:
            new_node = DependencyGraphNode(old_node.data)
            new_nodes[old_node.data] = new_node
            new_graph.add_node(new_node)
        # Link nodes
        for old_node in self.nodes:
            new_node = new_nodes[old_node.data]
            for old_node_dep in old_node.dependents:
                new_node.depends_on(new_nodes[old_node_dep.data])
        return new_graph

    def add_node(self, node: DependencyGraphNode[_T]) -> None:
        self.nodes.add(node)
        self.num_nodes += 1

    def add_nodes(self, nodes: Iterable[DependencyGraphNode[_T]]) -> None:
        for node in nodes:
            self.add_node(node)

    def linearise_graph(self) -> List[DependencyGraphNode]:
        # Run Kahn's algorithm to linearise DAG
        result = []
        # We are modifying the tree when running the algorithm, so we copy the tree
        search_graph = self._copy()
        queue = []
        # Populate queue
        for node in search_graph.nodes:
            if not node.has_dependents():
                queue.append(node)

        while len(queue) > 0:
            curr_node = queue.pop(0)
            for dependee in list(curr_node.dependees):
                dependee.remove_dependent(curr_node)
                if not dependee.has_dependents():
                    queue.append(dependee)
            result.append(curr_node)

        assert len(
            result) == self.num_nodes, "Length of result does not match the number of dependencies. Do you have a circular reference?"
        return result

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.linearise_graph().__str__()


class DependencyGraphNode():

    def __init__(self, data: _T):
        self.data = data
        self.dependees = set()  # Nodes that are dependent on us (Outgoing edges)
        self.dependents = set()  # Nodes that we depend on (Incoming edges)

    def depends_on(self, node: DependencyGraphNode):
        self.dependents.add(node)
        node.dependees.add(self)

    def remove_dependent(self, node_to_remove: DependencyGraphNode[_T]) -> DependencyGraphNode | None:
        to_remove = None
        if node_to_remove in self.dependents:
            self.dependents.remove(node_to_remove)
            node_to_remove.dependees.remove(self)
            to_remove = node_to_remove
        return to_remove

    def num_dependents(self) -> int:
        return len(self.dependents)

    def has_dependents(self) -> bool:
        return len(self.dependents) > 0

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.data.__str__()
