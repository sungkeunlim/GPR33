import numpy as np

from ..sources import HertzianDipole
from ..exceptions import CmdInputError
from .common import check_point
from. common import assign_item_coords

cmdname = '#hertzian_dipole'


def create_hertzian_dipoles(multicmds, G):
    if cmdname in multicmds:
        for params in multicmds[cmdname]:
            create_hertzian_dipole(params, G)


def create_hertzian_dipole(params, G):
    tmp = params.split()
    if len(tmp) < 5:
        raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires at least five parameters')

    # Check polarity & position parameters
    if tmp[0].lower() not in ('x', 'y', 'z'):
        raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' polarisation must be x, y, or z')

    h = HertzianDipole()
    p = (float(tmp[1]), float(tmp[2]), float(tmp[3]))
    coords, grid = check_point(p, G)
    assign_item_coords(h, coords)

    if not any(x.ID == tmp[4] for x in G.waveforms):
        raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' there is no waveform with the identifier {}'.format(tmp[4]))

    h.polarisation = tmp[0]
    h.ID = 'HertzianDipole(' + str(h.xcoord) + ',' + str(h.ycoord) + ',' + str(h.zcoord) + ')'
    h.waveformID = tmp[4]

    # Set length of dipole to grid size in polarisation direction
    if h.polarisation == 'x':
        h.dl = grid.dx
    elif h.polarisation == 'y':
        h.dl = grid.dy
    elif h.polarisation == 'z':
        h.dl = grid.dz

    if len(tmp) > 5:
        # Check source start & source remove time parameters
        start = float(tmp[5])
        stop = float(tmp[6])
        if start < 0:
            raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' delay of the initiation of the source should not be less than zero')
        if stop < 0:
            raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' time to remove the source should not be less than zero')
        if stop - start <= 0:
            raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' duration of the source should not be zero or less')
        h.start = start
        if stop > G.timewindow:
            h.stop = G.timewindow
        else:
            h.stop = stop
        startstop = ' start time {:g} secs, finish time {:g} secs '.format(h.start, h.stop)
    else:
        h.start = 0
        h.stop = G.timewindow
        startstop = ' '

        if G.messages:
            if G.dimension == '2D':
                print('Hertzian dipole is a line source in 2D with polarity {} at {:g}m, {:g}m, {:g}m,'.format(h.polarisation, h.xcoord * G.dx, h.ycoord * G.dy, h.zcoord * G.dz) + startstop + 'using waveform {} created.'.format(h.waveformID))
            else:
                print('Hertzian dipole with polarity {} at {:g}m, {:g}m, {:g}m,'.format(h.polarisation, h.xcoord * G.dx, h.ycoord * G.dy, h.zcoord * G.dz) + startstop + 'using waveform {} created.'.format(h.waveformID))

    h.calculate_waveform_values(grid)
    grid.hertziandipoles.append(h)
