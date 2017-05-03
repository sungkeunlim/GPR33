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
def rotate90_point(x, y, rotate90origin=()):
    """Rotates a point 90 degrees CCW in the x-y plane.

    Args:
        x, y (float): Coordinates.
        rotate90origin (tuple): x, y origin for 90 degree CCW rotation in x-y plane.

    Returns:
        xrot, yrot (float): Rotated coordinates.
    """

    # Translate point to origin
    x -= rotate90origin[0]
    y -= rotate90origin[1]

    # 90 degree CCW rotation and translate back
    xrot = -y + rotate90origin[0]
    yrot = x + rotate90origin[1]

    return xrot, yrot


def rotate90_edge(xs, ys, xf, yf, polarisation, rotate90origin):
    """Rotates an edge or edge-like object/source 90 degrees CCW in the x-y plane.

    Args:
        xs, ys, xf, yf (float): Start and finish coordinates.
        polarisation (str): is the polarisation and can be 'x', 'y', or 'z'.
        rotate90origin (tuple): x, y origin for 90 degree CCW rotation
        in x-y plane.

    Returns:
        xs, ys, xf, yf (float): Rotated start and finish coordinates.
    """

    xsnew, ysnew = rotate90_point(xs, ys, rotate90origin)
    xfnew, yfnew = rotate90_point(xf, yf, rotate90origin)

    # Swap coordinates for original y-directed edge, original x-directed
    # edge does not require this.
    if polarisation == 'y':
        xs = xfnew
        xf = xsnew
        ys = ysnew
        yf = yfnew
    else:
        xs = xsnew
        xf = xfnew
        ys = ysnew
        yf = yfnew

    return xs, ys, xf, yf


def rotate90_plate(xs, ys, xf, yf, rotate90origin):
    """Rotates an plate or plate-like object 90 degrees CCW in the x-y plane.

    Args:
        xs, ys, xf, yf (float): Start and finish coordinates.
        rotate90origin (tuple): x, y origin for 90 degree CCW
        rotation in x-y plane.

    Returns:
        xs, ys, xf, yf (float): Rotated start and finish coordinates.
    """

    xsnew, ysnew = rotate90_point(xs, ys, rotate90origin)
    xfnew, yfnew = rotate90_point(xf, yf, rotate90origin)

    # Swap x-coordinates to correctly specify plate
    xs = xfnew
    xf = xsnew
    ys = ysnew
    yf = yfnew

    return xs, ys, xf, yf
