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
