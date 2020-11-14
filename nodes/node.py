from typing import Any, Dict, Optional, Union, TypeVar, List, Type, NamedTuple, Iterable

class Graph_Node:
    """
    Create nodes which store metadata of the objects for easier futur references.
    Nodes are iterables.

    param subtype_name:
        Acts as an identifier for naming the various nodes created with this class.

    param color:
        For tracking when traversing through the graph via breadth first search or
        depth first search

    param group:
        For tracking the point in entry which each node stems from. It is also used to
        track how various branch nodes connect to entry root nodes

    param independent:
        Specify if a node created is independent: the value attribute of the class is a standalone if True,
        else the value attribute holds the value for multiple class instances and can be split to indicate
        but is kept in a single tuple for memory reasons.
        You may want to store multiple values of the different instances of a node object, by storing them as one and
        setting independent to False, hence each value represents a potential seperate node object
    """

    def __init__(self, subtype_name: str, value: Union[tuple, int, List[int], str, List[str]], independent: bool, **kwargs: Any):

        if any((isinstance(value, str), isinstance(value, int))):
            self.value = (value,)
        elif any((isinstance(value, list), isinstance(value, tuple))):
            for values in value:
                if any((type(values) == int, type(values) == str)):
                    self.value = tuple(value)
                    break
                else:
                    raise TypeError(f"expected either int or str inside the Iterable, got {type(self.value)}")
        else:
            raise TypeError(f"expected either list, tuple, int or str, got {type(self.value)}")

        self.subtype_name = subtype_name
        self.color = 'black'
        self.neighbors = []
        self._start = 0
        self.independent = independent
        self.group = set()
        self.__dict__.update(kwargs)

    @property
    def metadata(self):
        if any((isinstance(self.value, tuple), isinstance(self.value, list))):

            # make a copy of the class attributes instead of using it directly
            meta = dict(**self.__dict__)

            if all((type(self.value) != int, type(self.value) != str)):
                meta["object_length"] = len(self.value)
                return meta
            else:
                meta["object_length"] = 1
                return meta
        else:
            raise TypeError(f"expected either list, tuple, got {type(self.value)}")

    @property
    def _keys(self):
        return (self.subtype_name, self.value)

    # def __contains__(self, value):
    #     if value in self.metadata.values():
    #         return True
    #     return False

    def __hash__(self):
        return hash((self._keys))

    def __eq__(self, other):
        if isinstance(other, Graph_Node):
            return (self.subtype_name, self.value) == (other.subtype_name, other.value)
        return NotImplemented

    def __iter__(self):
        for elem in self.value:
            yield elem

    def __next__(self):
        if self._start <= self.metadata["object_length"]:
            self._start += 1
            return elem
        else:
            raise StopIteration

    def create_independent(self, value):
        if self.independent is False:
            return Graph_Node(self.subtype_name, value, True)

    def add_neighbors(self, node):
        """
        For use with graph datastructure
        """
        if isinstance(node, Graph_Node):
            if len(self.neighbors) > 0:
                for values in self.neighbors:
                    if node == values:
                        break
                else:
                    self.neighbors.append(node)
            else:
                self.neighbors.append(node)
            return
        raise ValueError('invalid entry')
