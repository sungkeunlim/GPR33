from ..snapshots import Snapshot
from ..exceptions import CmdInputError
from .common import check_coordinates

cmdname = '#snapshot'


def create_snapshot(params, G):
    tmp = params.split()
    if len(tmp) != 11:
        er = "'{}: {}' requires exactly eleven parameters"
        er = er.format(cmdname, ' '.join(tmp))
        raise CmdInputError(er)
    xs = G.calculate_coord('x', tmp[0])
    ys = G.calculate_coord('y', tmp[1])
    zs = G.calculate_coord('z', tmp[2])

    xf = G.calculate_coord('x', tmp[3])
    yf = G.calculate_coord('y', tmp[4])
    zf = G.calculate_coord('z', tmp[5])

    dx = G.calculate_coord('x', tmp[6])
    dy = G.calculate_coord('y', tmp[7])
    dz = G.calculate_coord('z', tmp[8])

    # If number of iterations given
    try:
        time = int(tmp[9])
    # If real floating point value given
    except:
        time = float(tmp[9])
        if time > 0:
            time = round_value((time / G.dt)) + 1
        else:
            raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' time value must be greater than zero')

    check_coordinates(xs, ys, zs, G, name='lower')
    check_coordinates(xf, yf, zf, G, name='upper')

    if xs >= xf or ys >= yf or zs >= zf:

        raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' the lower coordinates should be less than the upper coordinates')
        if dx < 0 or dy < 0 or dz < 0:
            raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' the step size should not be less than zero')
        if dx < G.dx or dy < G.dy or dz < G.dz:
            raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' the step size should not be less than the spatial discretisation')
        if time <= 0 or time > G.iterations:
            raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' time value is not valid')

    s = Snapshot(xs, ys, zs, xf, yf, zf, dx, dy, dz, time, tmp[10])

    if G.messages:
        print('Snapshot from {:g}m, {:g}m, {:g}m, to {:g}m, {:g}m, {:g}m, discretisation {:g}m, {:g}m, {:g}m, at {:g} secs with filename {} created.'.format(xs * G.dx, ys * G.dy, zs * G.dz, xf * G.dx, yf * G.dy, zf * G.dz, dx * G.dx, dx * G.dy, dx * G.dz, s.time * G.dt, s.basefilename))

    G.snapshots.append(s)


def create_snapshots(multicmds, G):
    # Snapshot
    if multicmds[cmdname] is not None:
        for params in multicmds[cmdname]:
            create_snapshot(params, G)
