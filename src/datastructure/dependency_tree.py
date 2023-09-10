from __future__ import annotations
from typing import List, TypeVar


_T = TypeVar("_T")


class DependencyTreeNode():

    def __init__(self, data: _T):
        self.data = data
        self.children = set()

    def add_child(self, node: DependencyTreeNode):
        self.children.add(node)

    def remove_child_from_tree(self, data: _T) -> DependencyTreeNode | None:
        result = None
        for child in self.children:
            if child.data == data:
                result = child
                self.children.remove(child)
                break
            result = child.remove_child_from_tree(data)
            if result is not None:
                break
        return result

    def find_child(self, data: _T) -> DependencyTreeNode | None:
        """
        Recursively search all the children of this tree for data and return the
        subtree.
        """
        result = None
        for child in self.children:
            if child.data == data:
                result = child
                break
            result = child.find_child(data)
        return result

    def find_immediate_child(self, data: _T):
        """
        Search immediate children of this tree for data and return the subtree.
        """
        result = None
        for child in self.children:
            if child.data == data:
                result = child
                break
        return result

    def get_dependencies(self) -> List[DependencyTreeNode]:
        """
        Get all children as a list recursively.
        """
        result = list(self.children)
        for child in self.children:
            result.extend(child.get_dependencies())
        return result

    def __len__(self) -> int:
        return len(self.get_dependencies())
