import unittest
from src.datastructure.dependency_tree import DependencyTreeNode


class TestDependencyTree(unittest.TestCase):
    @staticmethod
    def _gen_nodes(num_nodes: int):
        return list(DependencyTreeNode(i) for i in range(num_nodes))

    def test_empty_children(self):
        tree = DependencyTreeNode("abc")
        self.assertEqual(0, len(tree))

    def test_find_non_exist_children(self):
        num_nodes = 5  # 0 to 4
        nodes = self._gen_nodes(num_nodes)
        root = nodes[0]
        for i in range(1, num_nodes):
            root.add_child(nodes[i])
        self.assertIsNone(root.find_immediate_child(num_nodes))
        self.assertIsNone(root.find_child(num_nodes))

    def test_find_exist_children(self):
        num_nodes = 5  # 0 to 4
        nodes = self._gen_nodes(num_nodes)
        root = nodes[0]
        for i in range(1, num_nodes):
            root.add_child(nodes[i])
        self.assertEqual(nodes[num_nodes - 1], root.find_immediate_child(num_nodes - 1))
        self.assertEqual(nodes[num_nodes - 1], root.find_child(num_nodes - 1))

    def test_multi_level_tree(self):
        """
           0
         1   2
        3 4
        """
        num_nodes = 5
        nodes = self._gen_nodes(num_nodes)
        root = nodes[0]
        node_1 = nodes[1]
        node_2 = nodes[2]
        root.add_child(node_1)
        root.add_child(node_2)
        node_1_1 = nodes[3]
        node_1_2 = nodes[4]
        node_1.add_child(node_1_1)
        node_1.add_child(node_1_2)
        self.assertEqual(num_nodes - 1, len(root))
        self.assertIn(node_1, root.get_dependencies())
        self.assertIn(node_2, root.get_dependencies())
        self.assertIn(node_1_1, root.get_dependencies())
        self.assertIn(node_1_2, root.get_dependencies())

        self.assertIn(node_1_1, node_1.get_dependencies())
        self.assertIn(node_1_2, node_1.get_dependencies())
        self.assertNotIn(node_2, node_1.get_dependencies())
        self.assertNotIn(root, node_1.get_dependencies())

        self.assertNotIn(root, node_2.get_dependencies())
        self.assertNotIn(node_1, node_2.get_dependencies())
        self.assertNotIn(node_1_1, node_2.get_dependencies())
        self.assertNotIn(node_1_2, node_2.get_dependencies())

    def test_remove_child(self):
        """
           0
         1   2
        3 4
        """
        num_nodes = 5
        nodes = self._gen_nodes(num_nodes)
        root = nodes[0]
        node_1 = nodes[1]
        node_2 = nodes[2]
        root.add_child(node_1)
        root.add_child(node_2)
        node_1_1 = nodes[3]
        node_1_2 = nodes[4]
        node_1.add_child(node_1_1)
        node_1.add_child(node_1_2)
        self.assertIs(node_1, root.remove_child_from_tree(1))
        self.assertIsNone(root.find_child(1))
        self.assertIs(node_2, root.find_child(2))
        self.assertIsNone(root.find_child(3))
        self.assertEqual(1, len(root))

    def test_remove_deep_child(self):
        """
           0
         1   2
        3 4
        """
        num_nodes = 5
        nodes = self._gen_nodes(num_nodes)
        root = nodes[0]
        node_1 = nodes[1]
        node_2 = nodes[2]
        root.add_child(node_1)
        root.add_child(node_2)
        node_1_1 = nodes[3]
        node_1_2 = nodes[4]
        node_1.add_child(node_1_1)
        node_1.add_child(node_1_2)
        self.assertIs(node_1_2, root.remove_child_from_tree(4))
        self.assertIsNone(root.find_child(4))
        self.assertEqual(num_nodes - 2, len(root))

    def test_remove_invalid_child(self):
        """
           0
         1   2
        3 4
        """
        num_nodes = 5
        nodes = self._gen_nodes(num_nodes)
        root = nodes[0]
        node_1 = nodes[1]
        node_2 = nodes[2]
        root.add_child(node_1)
        root.add_child(node_2)
        node_1_1 = nodes[3]
        node_1_2 = nodes[4]
        node_1.add_child(node_1_1)
        node_1.add_child(node_1_2)
        self.assertIsNone(root.remove_child_from_tree(999))
        self.assertEqual(num_nodes - 1, len(root))
        self.assertIn(node_1, root.get_dependencies())
        self.assertIn(node_2, root.get_dependencies())
        self.assertIn(node_1_1, root.get_dependencies())
        self.assertIn(node_1_2, root.get_dependencies())
