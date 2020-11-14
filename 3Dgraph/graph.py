from collections import namedtuple
from typing import Any, Dict, Optional, Union, TypeVar, List, Type, NamedTuple, Iterable


class AnchoredGraph:
    __slots__ = ["nodes"]

    def __init__(self):
        self.nodes = set()

    def build_graph(self, objects_: Union[Dict[str, List[Union[str, dict, int]]], NamedTuple],
                    root_name: str, *branch_names: str) -> list:
        """
        Build an anchored bipartite, with the node of rootname acting as the anchor which all other
        nodes connect.
        """

        all_nodes = []
        for key, value in objects_.items():
            for index, items in enumerate(value):
                if isinstance(items, dict):
                    vertices = self.initialize_vertices(objects_=items,
                                                        root_name=root_name,
                                                        independent=False,
                                                        group=index)
                    all_nodes.extend(vertices)
                continue

        root = set()

        for vertex in all_nodes:
            if vertex[root_name]:
                root.add(vertex[root_name])

        for branch in branch_names:
            if not isinstance(branch, str):
                raise TypeError(f"Expected a string, got {type(branch)}")

            try:
                if vertex[branch]:
                    branches = self.locate_graph_link(vertex_list=all_nodes,
                                                      branch_name=branch)
            except KeyError:
                continue

            share = self.initialize_connection(branch_iterable=branches, root_iterable=root)

        return self.find_nodes_subtype(root_name)

    def find_nodes_subtype(self, name: str) -> list:
        """
        get the nodes with a given subtype name.
        """
        if len(self.nodes) > 0:
            return (node for node in self.nodes if node.subtype_name == name)

        return None

    def _add_node(self, node):
        if isinstance(node, Graph_Node) and node not in self.nodes:
            self.nodes.add(node)
            return

    def _add_graph_edges(self, node_1, node_2):
        if node_1 in self.nodes and node_2 in self.nodes:
            for value in self.nodes:
                if value == node_1:
                    value.add_neighbors(node_2)
                if value == node_2:
                    value.add_neighbors(node_1)
            return True
        return

    def initialize_vertices(self, objects_: Union[Dict[str, List[Union[str, int]]], NamedTuple],
                            root_name: str, independent: bool, group: int,
                            vertices_list: list = None) -> list:
        """
        Creates nodes from the dictionary and groups the values into various node subtypes based on the
        key name of the dictionary.
                    *
                   / \
                  *   *
                   \ /
                    *

        The expected entry structure example:
       {
            "root_name": 3,
            "branch_name1": [1,2,3,4]
            "branch_name2": [1,2]
        },
        {
            "root_name": 2,
            "branch_name1": [1,2]
        }
        Each item in the group can possess more than one branch name.

        root_id is the beginning point of a graph structure, The value of root_id expects
        a single value(int or str) unlike subsequent branches which can be tuple, list, strings or ints
        """
        if vertices_list is None:
            vertices_list = []
        if not isinstance(vertices_list, list):
            raise TypeError(f"Expected List, got {type(vertices_list)}")

        group_store = {}
        for key, values in objects_.items():
            if key == root_name:
                if type(values) == int or type(values) == str:
                    node = Graph_Node(subtype_name=key, value=values,
                                      independent=True, level="root")
                    node.group.add(group)
                    group_store[key] = node

                    # add root nodes to the class node list
                    self._add_node(node)
                else:
                    raise TypeError("Expected value of 'root_name' key to be a str or int")
            else:
                node = Graph_Node(subtype_name=key, value=values,
                                  independent=independent)
                node.group.add(group)
                group_store[key] = node
                vertices_list.append(group_store)

        return vertices_list

    def locate_graph_link(self, vertex_list: list,
                          branch_name: str) -> set:
        """
        locate branch nodes that share connection to root node(s) based on the sutype name of the
        node, with the branch name matching the value of the node's subtype name attribute.
        This function accepts a list containing graph nodes, selecting all graph nodes with
        similar values and creating a match case for them to their various root nodes
        """
        shared = set()

        for index, vertext_group in enumerate(vertex_list):
            index

            for key, vertex in vertext_group.items():
                if not isinstance(vertex, Graph_Node):
                    continue

                if key == branch_name:
                    if vertex.independent is True and vertex not in shared:
                        vertex.group.add(index)
                        shared.add(vertex)

                    elif vertex.independent is True and vertex in shared:
                        vertex.group.add(index)

                    elif vertex.independent is False:
                        for values in vertex.value:
                            independent = vertex.create_independent(values)

                            if independent not in shared:
                                independent.group.add(index)
                                shared.add(independent)

                            elif independent in shared:
                                for items in shared:
                                    if items == independent:
                                        items.group.add(index)

                        # delete parent to free up memory
                        del vertex

        # add branch nodes to class node list
        for nodes in shared:
            self._add_node(nodes)
        return shared

    def initialize_connection(self, branch_iterable: Iterable, root_iterable: Iterable) -> None:
        """
        creating edges between graph nodes
        """
        for root in root_iterable:
            for branch in branch_iterable:
                if root.group.intersection(branch.group):
                    self._add_graph_edges(root, branch)
        return

