from typing import Any
from datastructure.dependency_graph import DependencyGraph, DependencyGraphNode
from utils.types import VALID_BASE_TYPE_VAL
from utils.const import OPERATORS


class RefProcessor():
    """Do processing on references"""

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

        REFERENCE_KEYS = ["-fz-attr-len", "size", "-fz-process-crc32", "-fz-process-md5", "-fz-process-sha1", "-fz-process-sha224", "-fz-process-sha256", "-fz-process-sha384", "-fz-process-sha512", "-fz-process-sha-3-224", "-fz-process-sha-3-256", "-fz-process-sha-3-384", "-fz-process-sha-3-512"]
        available_ref = nodes.keys()
        # Link dependencies
        for seq_entry in self.source["seq"]:
            seq_entry_id = seq_entry["id"]
            is_custom_type = seq_entry["type"] not in VALID_BASE_TYPE_VAL
            for ref_key in REFERENCE_KEYS:
                if is_custom_type and ref_key == "size":
                    # Ignore size if is custom type, size determined by size of custom type
                    continue
                if ref_key in seq_entry:
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
