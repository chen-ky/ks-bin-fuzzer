from typing import Any, List
import re
from datastructure.dependency_graph import DependencyGraph, DependencyGraphNode
from utils.types import VALID_BASE_TYPE_VAL
from utils.const import OPERATORS, KEY_WITH_EXPRESSION, KEY_WITH_EXPRESSION_PRODUCE_BYTES


class RefProcessor():
    """Do processing on references"""

    REFERENCE_KEYS = set(KEY_WITH_EXPRESSION).union(
        KEY_WITH_EXPRESSION_PRODUCE_BYTES)

    def __init__(self, source: dict[str, Any]):
        self.source = source

    def _breakdown_expression_to_components(self, expression: Any) -> List[str]:
        if not isinstance(expression, str):
            return []
        # Replace all operators with whitespace
        for op in OPERATORS:
            expression = expression.replace(op, " ")
        # Split into components based on whitespace
        expr_components = expression.split()
        return list(filter(lambda s: len(s) > 0, expr_components))

    def _get_valid_references(self, expression: Any, available_ref: List[str]) -> List[str]:
        components = self._breakdown_expression_to_components(expression)
        return list(filter(lambda component: component in available_ref, components))

    def _key_can_contain_expression(self, key: str) -> bool:
        for regex_ref_key in self.REFERENCE_KEYS:
            if re.fullmatch(regex_ref_key, key) is not None:
                return True
        return False

    def _construct_dependency_graph(self) -> None:
        dependency_graph = DependencyGraph()
        self.source["_dependency_graph"] = dependency_graph

        nodes = {}
        # Initialise a node for every local reference available
        for seq_entry in self.source["seq"]:
            seq_entry_id = seq_entry["id"]
            nodes[seq_entry_id] = DependencyGraphNode(seq_entry_id)
        for instance_entry_name in self.source["instances"]:
            nodes[instance_entry_name] = DependencyGraphNode(instance_entry_name)
        dependency_graph.add_nodes(nodes.values())

        available_ref = list(nodes.keys())
        # Link dependencies
        for seq_entry in self.source["seq"]:
            # print(f"{seq_entry}", file=sys.stderr)
            seq_entry_id = seq_entry["id"]
            is_custom_type = seq_entry["type"] not in VALID_BASE_TYPE_VAL
            is_switch_custom_type = isinstance(seq_entry["type"], dict)
            # If type is a `switch-on` statement
            if is_switch_custom_type:
                components = self._get_valid_references(
                    seq_entry["type"]["switch-on"], available_ref)
                for component in components:
                    # print(f"{seq_entry_id} ⭠ {component}", file=sys.stderr)
                    nodes[seq_entry_id].depends_on(nodes[component])
            # Go through each key in a sequence entry
            for seq_entry_key in seq_entry:
                # Ignore size if is custom type, size determined by size of custom type
                if (is_custom_type and seq_entry_key == "size") or not self._key_can_contain_expression(seq_entry_key):
                    continue
                seq_entry_value = seq_entry[seq_entry_key]
                components = self._get_valid_references(
                    seq_entry_value, available_ref)
                for component in components:
                    # print(f"{seq_entry_id} ⭠ {component}", file=sys.stderr)
                    nodes[seq_entry_id].depends_on(nodes[component])
        for instance_name, instance_entry in self.source["instances"].items():
            if instance_entry["-fz-static"]:
                # Static object should not depend on other fields
                continue
            # Go through each key in a instance entry
            for instance_entry_key in instance_entry:
                if not self._key_can_contain_expression(instance_entry_key):
                    continue
                instance_entry_value = instance_entry[instance_entry_key]
                components = self._get_valid_references(
                    instance_entry_value, available_ref)
                for component in components:
                    # print(f"{seq_entry_id} ⭠ {component}", file=sys.stderr)
                    nodes[instance_name].depends_on(nodes[component])

    def _construct_available_ref(self) -> None:
        self.source["_available_ref"] = []
        self.source["_static_ref"] = []
        for seq_entry in self.source["seq"]:
            is_static = seq_entry["-fz-static"]
            self.source["_available_ref"].append(seq_entry["id"])
            if is_static:
                self.source["_static_ref"].append(seq_entry["id"])
        for instance_name, instance_entry in self.source["instances"].items():
            is_static = instance_entry["-fz-static"]
            self.source["_available_ref"].append(instance_name)
            if is_static:
                self.source["_static_ref"].append(instance_name)

    def pre_process(self):
        pass

    def post_process(self):
        self._construct_available_ref()
        self._construct_dependency_graph()

        custom_types = self.source.get("types")
        if custom_types is not None:
            for custom_type_src in custom_types.values():
                RefProcessor(custom_type_src).post_process()
