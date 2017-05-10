import numpy as np

from ..constants import floattype
from ..receivers import Rx
from ..exceptions import CmdInputError
from .common import check_point
from. common import assign_item_coords


def create_receivers(multicmds, G):
    # Receiver
    cmdname = '#rx'
    if cmdname in multicmds:
        for params in multicmds[cmdname]:
            create_receiver(params, G)


def create_receiver(params, G):
    cmdname = '#rx'
    tmp = params.split()
    if len(tmp) != 3 and len(tmp) < 5:
        raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' has an incorrect number of parameters')

    r = Rx()
    p = (float(tmp[0]), float(tmp[1]), float(tmp[2]))
    coords, grid = check_point(p, G)
    assign_item_coords(r, coords)

    # If no ID or outputs are specified, use default i.e Ex, Ey, Ez, Hx, Hy,
    # Hz, Ix, Iy, Iz
    if len(tmp) == 3:
        r.ID = r.__class__.__name__
        r.ID += '(' + str(r.xcoord) + ',' + str(r.ycoord) + ',' + str(r.zcoord) + ')'
        for key in Rx.defaultoutputs:
            r.outputs[key] = np.zeros(G.iterations, dtype=floattype)

    else:
        r.ID = tmp[3]
        # Check and add field output names
        for field in tmp[4::]:
            if field in Rx.availableoutputs:
                r.outputs[field] = np.zeros(G.iterations, dtype=floattype)
            else:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' contains an output type that is not available')

    if G.messages:
        print('Receiver at {:g}m, {:g}m, {:g}m with output component(s) {} created.'.format(r.xcoord * G.dx, r.ycoord * G.dy, r.zcoord * G.dz, ', '.join(r.outputs)))

    grid.rxs.append(r)
