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
from .data_structures import Node
from .data_structures import TreeWalker
from slugify import slugify
import os


class GPRObject(Node):

    def __init__(self, name, *args):
        Node.__init__(self, name)
        self.args = args

    def to_command(self):
        s = self.fs.format(*self.args)
        return s

    def __str__(self):
        return self.to_command()


class GPRObjectCreator:

    def __init__(self):
        self.types = {
            'subgrid': '#subgrid: {} {} {} {} {} {} {} {} {}',
            'discretisation': '#dx_dy_dz: {} {} {}',
            'time_window': '#time_window: {}',
            'title': '#title: {}',
            'edge': '#edge: {} {} {} {} {} {} {}',
            'plate': '#plate: {} {} {} {} {} {} {}',
            'box': '#box: {} {} {} {} {} {} {}',
            'domain': '#domain: {} {} {}',
            'waveform': '#waveform: {} {} {} {}',
            'voltage_source': '#voltage_source: {} {} {} {} {} {}',
            'cylinder': '#cylinder: {} {} {} {} {} {} {} {}',
            'triangle': '#triangle: {} {} {} {} {} {} {} {} {} {} {} {}',
            'hertzian_dipole': '#hertzian_dipole: {} {} {} {} {}',
            'magnetic_dipole': '#magnetic_dipole: {} {} {} {} {}',
            'snapshot': '#snapshot: {} {} {} {} {} {} {} {} {} {} snapshot{}',
            'rx': '#rx: {} {} {}',
            'geometry_view': '#geometry_view: {} {} {} {} {} {} {} {} {} {} {}',
            'dx_dy_dz': '#dx_dy_dz: {} {} {}',
            'material': '#material: {} {} {} {} {}',
            'time_window': '#time_window: {}',
            'wrapper': 'wrapper',
            'waveform': '#waveform: {} {} {} {}',
            'transmission_line': '#transmission_line: {} {} {} {} {} {}',
            'sma_transmission_line': '#sma_transmission_line: {} {} {} {} {} {}',
            'monopole_coaxial': '#monopole_coaxial: {} {} {} {} {} {}',
            'pml_cells': '#pml_cells: {} {} {} {} {} {}'
        }

    def create(self, name, *args):
        fs = self.types.get(name, None)
        if fs is None:
            raise Exception('Unknown GPRObject Type: ', name)
        if fs.count('{}') != len(args):
            raise Exception('Incorrect number of arguments to create: ', name)
        e = GPRObject(name, *args)
        e.fs = fs
        return e


class Scene(Node):

    def __init__(self):
        Node.__init__(self, 'scene')

    def to_commands(self):
        s = ''
        tw = TreeWalker()
        nodes = tw.getBreadthFirstNodes(self)
        for node in nodes:
            if node.name != 'wrapper':
                s += node.to_command() + os.linesep
        return s

    def getLast(self):
        tw = TreeWalker()
        nodes = tw.getBreadthFirstNodes(self)
        for node in reversed(nodes):
            if node.name == 'wrapper':
                return node
        return None

    def getObj(self, name):
        tw = TreeWalker()
        t = tw.getNode(self, name)
        return t

    def getTitle(self):
        return self.getObj('title')

    def getDomain(self):
        return self.getObj('domain')

    def hasSubgrid(self):
        if self.getObj('subgrid'):
            return True
        return False


def write_scene(scene):
    commands = scene.to_commands()
    t = scene.getTitle().args[0]
    fp = slugify(t) + '.in'
    with open(fp, 'w') as f:
        f.write(commands)
    return fp
