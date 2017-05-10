from ..subgrid_3d import SubGrid3d
from ..subgrid import SubGrid2dTE
from ..subgrid import SubGrid2dTM
from ..exceptions import CmdInputError
from copy import copy

cmdname = '#subgrid'


def create_subgrids(multicmds, G):

    if cmdname in multicmds:
        for params in multicmds[cmdname]:
            create_subgrid(params, G)


def create_subgrid(params, G):

    """Function to create subgrid instances.

        Args:
            params (string): parameter string specified in the input
            file.
            G (class): Grid class instance - holds essential parameters
            describing the model.

    """

    args = params.split()

    # Check for the correct number of arguments
    if len(args) != 9:
        raise CmdInputError(
            'Subgrid command requires 8 parameters. Only {} provided'
            .format(len(args)))

    x1 = float(args[0])
    y1 = float(args[1])
    z1 = float(args[2])
    x2 = float(args[3])
    y2 = float(args[4])
    z2 = float(args[5])
    ratio = int(args[6])
    name = args[7]
    background_material = args[8]

    # 2d subgrid 2 cells high only
    if G.nz == 2:
        sg = SubGrid2dTE(ratio)
    elif G.nz == 1:
        sg = SubGrid2dTM(ratio)
    else:
        sg = SubGrid3d(ratio)

    G.subgrids.append(sg)
    sg.name = name
    sg.background_material = background_material

    # Set the discretisation
    sg.dx = G.dx / ratio
    sg.dy = G.dy / ratio
    sg.dz = G.dz / ratio

    sg.calculate_dt()
    sg.calculate_pml_thickness()

    # Define coordinates of the user defined grid at main grid nodes
    sg.x1, sg.y1, sg.z1 = G.calculate_disc_coord_3(x1, y1, z1)
    sg.x2, sg.y2, sg.z2 = G.calculate_disc_coord_3(x2, y2, z2)

    # 2D grid is not aligned with main grid in z direction.
    if sg.gridtype == '2DTE' or sg.gridtype == '2DTM':
        sg.z1 = sg.calculate_disc_coord('z', z1)
        sg.z2 = sg.calculate_disc_coord('z', z2)

    # Number of cells in each dimension for the working region
    sg.nwx = sg.calculate_coord('x', x2 - x1)
    sg.nwy = sg.calculate_coord('y', y2 - y1)
    sg.nwz = sg.calculate_coord('z', z2 - z1)

    # Calculate the position of the sub grid in terms of main grid node indices
    sg.i0, sg.j0, sg.k0 = G.calculate_coord_3(x1, y1, z1)
    sg.i1, sg.j1, sg.k1 = G.calculate_coord_3(x2, y2, z2)

    # Number of cells in each dimension for the whole region
    sg.nx = 2 * sg.n_boundary_cells_x + sg.nwx
    sg.ny = 2 * sg.n_boundary_cells_y + sg.nwy
    sg.nz = 2 * sg.n_boundary_cells_z + sg.nwz

    if ratio % 2 == 0:
        raise CmdInputError('Subgrid Error: Odd ratios only')
    else:
        sg.ratio = ratio

    # Check the sub grid is specified within the bounds of the main grid
    try:
        G.within_bounds(x=x1, y=y1, z=z1)
    except ValueError as e:
        raise CmdInputError('Subgrid Error: Lower left corner is out of bounds')

    try:
        G.within_bounds(x=x2, y=y2, z=z2)
    except ValueError as e:
        raise CmdInputError('Subgrid Error: Upper right corner is out of bounds')

    sg.iterations = G.iterations * ratio

    # Copy over built in materials
    sg.materials = [copy(m) for m in G.materials if m.numID in range(0, G.n_built_in_materials + 1)]
    return sg
