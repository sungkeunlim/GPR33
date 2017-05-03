# Copyright (C) 2015-2017: The University of Edinburgh
#                 Authors: Craig Warren and Antonis Giannopoulos
#
# This file is part of gprMax.
#
# gprMax is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gprMax is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gprMax.  If not, see <http://www.gnu.org/licenses/>.
import copy


class Node:

    def __init__(self, name='noname'):
        self.children = []
        self.name = name
        self.marked = False

    def add(self, *args):
        for node in args:
            self.children.append(node)


class TreeWalker:

    def getBreadthFirstNodes(self, tree):

        visited = copy.copy(tree.children)
        q = copy.copy(tree.children)

        while q:
            v = q.pop(0)

            for w in v.children:

                if not w.marked:
                    w.marked = True
                    q.append(w)
                    visited.append(w)

        # Unmark the nodes so we can use again
        for node in visited:
            node.marked = False

        return visited

    def getDepthFirstNodes(self, tree):
        nodes = []
        for child in tree.children:
            nodes.append(child)
            nodes += self.getDepthFirstNodes(child)
        return nodes

    def getNode(self, tree, name):
        nodes = self.getDepthFirstNodes(tree)
        for node in nodes:
            if node.name == name:
                return node
