from ..geometry_outputs import GeometryView
from ..exceptions import CmdInputError
from .common import check_coordinates

cmdname = '#geometry_view'


def create_geometry_views(multicmds, G):
    if multicmds[cmdname] is not None:
        for params in multicmds[cmdname]:
            create_geometry_view(params, G)


def create_geometry_view(params, G):

    tmp = params.split()
    print(len(tmp))
    if len(tmp) < 11:
        s = '{}: {} requires at least eleven parameters'
        raise CmdInputError(s.format(cmdname, ' '.join(tmp)))
    # If the grid isnt specified make it the main grid
    if len(tmp) == 11:
        tmp.append('G')
    if tmp[11] == 'G':
        grid = G
        xf = grid.calculate_coord('x', tmp[3])
        yf = grid.calculate_coord('y', tmp[4])
        zf = grid.calculate_coord('z', tmp[5])

        xs = grid.calculate_coord('x', tmp[0])
        ys = grid.calculate_coord('y', tmp[1])
        zs = grid.calculate_coord('z', tmp[2])

    else:
        grid = [sg for sg in G.subgrids if sg.name == tmp[11]][0]

        # Always record the whole domain for the sub grid
        xf = grid.nx
        yf = grid.ny
        zf = grid.nz

        xs = 0
        ys = 0
        zs = 0

    dx = grid.calculate_coord('x', tmp[6])
    dy = grid.calculate_coord('y', tmp[7])
    dz = grid.calculate_coord('z', tmp[8])

    check_coordinates(xs, ys, zs, grid, name='lower')
    check_coordinates(xf, yf, zf, grid, name='upper')

    if xs >= xf or ys >= yf or zs >= zf:
        raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' the lower coordinates should be less than the upper coordinates')
    if dx < 0 or dy < 0 or dz < 0:
        raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' the step size should not be less than zero')
    if dx > grid.nx or dy > grid.ny or dz > grid.nz:
        raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' the step size should be less than the domain size')
    if dx < grid.dx or dy < grid.dy or dz < grid.dz:
        raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' the step size should not be less than the spatial discretisation')
    if tmp[10].lower() != 'n' and tmp[10].lower() != 'f':
        raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires type to be either n (normal) or f (fine)')
    if tmp[10].lower() == 'f' and (dx * grid.dx != grid.dx or dy * grid.dy != grid.dy or dz * grid.dz != grid.dz):
        raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires the spatial discretisation for the grideometry view to be the same as the model for geometry view of type f (fine)')

    # Set type of geometry file
    if tmp[10].lower() == 'n':
        type = '.vti'
    else:
        type = '.vtp'

    g = GeometryView(xs, ys, zs, xf, yf, zf, dx, dy, dz, tmp[9],
                     type, grid=grid)

    if grid.messages:
        print('Geometry view from {:g}m, {:g}m, {:g}m, to {:g}m, {:g}m, {:g}m, discretisation {:g}m, {:g}m, {:g}m, filename {} created.'.format(xs * grid.dx, ys * grid.dy, zs * grid.dz, xf * grid.dx, yf * grid.dy, zf * grid.dz, dx * grid.dx, dy * grid.dy, dz * grid.dz, g.basefilename))

    # Append the new GeometryView object to the geometry views list
    G.geometryviews.append(g)
