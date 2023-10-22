from typing import Any
import re
from datastructure.dependency_graph import DependencyGraph, DependencyGraphNode
from utils.types import VALID_BASE_TYPE_VAL
from utils.const import OPERATORS, KEY_WITH_EXPRESSION, KEY_WITH_EXPRESSION_PRODUCE_BYTES


class RefProcessor():
    """Do processing on references"""

    REFERENCE_KEYS = set(KEY_WITH_EXPRESSION).union(KEY_WITH_EXPRESSION_PRODUCE_BYTES)

    def __init__(self, source: dict[str, Any]):
        self.source = source

    def _construct_dependency_graph(self) -> None:
        dependency_graph = DependencyGraph()
        self.source["_dependency_graph"] = dependency_graph
        nodes = {}
        # Initialise a node for every local reference available
        for seq_entry in self.source["seq"]:
            seq_entry_id = seq_entry["id"]
            nodes[seq_entry_id] = DependencyGraphNode(seq_entry_id)
        dependency_graph.add_nodes(nodes.values())

        available_ref = nodes.keys()
        # Link dependencies
        for seq_entry in self.source["seq"]:
            seq_entry_id = seq_entry["id"]
            is_custom_type = seq_entry["type"] not in VALID_BASE_TYPE_VAL
            for regex_ref_key in self.REFERENCE_KEYS:
                ref_key = None
                for seq_entry_key in seq_entry:
                    ref_key = re.fullmatch(regex_ref_key, seq_entry_key)
                    if ref_key is not None:
                        ref_key = ref_key.string
                        break
                if ref_key is None or (is_custom_type and ref_key == "size"):
                    # Ignore size if is custom type, size determined by size of custom type
                    continue
                expression = seq_entry[ref_key]
                if not isinstance(expression, str):  # Only strings can be expression
                    continue
                # Replace all operators with whitespace
                for op in OPERATORS:
                    expression.replace(op, " ")
                expr_components = expression.split()
                # Split into components based on whitespace
                for component in expr_components:
                    if component in available_ref:
                        nodes[seq_entry_id].depends_on(nodes[component])

    def _construct_available_ref(self) -> None:
        self.source["_available_ref"] = []
        for seq_entry in self.source["seq"]:
            self.source["_available_ref"].append(seq_entry["id"])

    def pre_process(self):
        pass

    def post_process(self):
        self._construct_available_ref()
        self._construct_dependency_graph()

        custom_types = self.source.get("types")
        if custom_types is not None:
            for custom_type_src in custom_types.values():
                RefProcessor(custom_type_src).post_process()
