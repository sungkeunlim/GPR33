from ..exceptions import CmdInputError
from ..utilities import wrap_string_in_warning


def check_pml(coord, grid):
    """
        Function to check whether the item is contained with a grids pml
    """
    if (coord[0] < grid.pmlthickness['x0']
        or coord[0] > grid.nx - grid.pmlthickness['xmax']
        or coord[1] < grid.pmlthickness['y0']
        or coord[1] > grid.ny - grid.pmlthickness['ymax']
        or coord[2] < grid.pmlthickness['z0']
        or coord[2] > grid.nz - grid.pmlthickness['zmax']):

        s = "WARNING: '{}: {}'"
        s += "sources and receivers should not normally be"
        s += "positioned within the PML."
        s = wrap_string_in_warning(s)
        raise CmdInputError(s)
        print(s)


# Check if coordinates are within the bounds of the grid
def check_coordinates(x, y, z, grid, name=''):
    try:
        grid.within_bounds(x=x, y=y, z=z)
    except ValueError as err:
        s = "'{}: {} ' {} {}-coordinate is not within the model domain"
        s = s.format(cmdname, ' '.join(tmp), name, err.args[0])
        raise CmdInputError(s)


def check_point(point, grid):

    """
        Function checks whether a continuous point (x1, y1, z1) in within
        the grid specifed or any subgrid and return the array indices of the
        point and the relevent grid.
    """

    coords = grid.calculate_coord_3(*point)
    check_coordinates(*coords, grid)

    # Check the point is not within the grids pml region
    check_pml(coords, grid)

    return (coords, grid)


def assign_item_coords(item, coords):
    item.xcoord, item.ycoord, item.zcoord = coords
    item.xcoordorigin, item.ycoordorigin, item.zcoordorigin = coords
    return item
