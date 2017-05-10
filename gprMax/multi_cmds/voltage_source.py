from ..exceptions import CmdInputError
from ..sources import VoltageSource


cmdname = '#voltage_source'


def create_voltage_sources(multicmds, G):

    if cmdname in multicmds:
        for params in multicmds[cmdname]:
            create_voltage_source(params, G)


def create_voltage_source(params, G):

    if G.subgrids:
        grid = G.subgrids[0]
    else:
        grid = G

    tmp = params.split()

    # Check number of arguments
    if len(tmp) < 6:
        em = '{}: {} requires at least six parameters'.format(cmdname, ' '.join(tmp))
        raise CmdInputError(em)

    # Parse argument string
    polarisation = tmp[0].lower()
    xcoord = float(tmp[1])
    ycoord = float(tmp[2])
    zcoord = float(tmp[3])
    resistance = float(tmp[4])
    waveform_id = tmp[5]

    try:
        start = float(tmp[6])
        stop = float(tmp[7])
        if start < 0:
            em = '{}: {} delay of the initiation of the source should not be less than zero'.format(cmdname, ' '.join(tmp))
            raise CmdInputError(em)
        if stop < 0:
            em = '{}: {} time to remove the source should not be less than zero'.format(cmdname, ' '.join(tmp))
            raise CmdInputError(em)
        if stop - start <= 0:
            em = '{}: {} duration of the source should not be zero or less'.format(cmdname, ' '.join(tmp))
            raise CmdInputError(em)

        if stop > G.timewindow:
            stop = G.timewindow

        startstop = ' start time {:g} secs, finish time {:g} secs '.format(start, stop)

    except IndexError:
        start = 0
        stop = G.timewindow
        startstop = ' '

    # Check polarity & position parameters
    if polarisation.lower() not in ('x', 'y', 'z'):
        em = '{}: {} polarisation must be x, y, or z'.format(cmdname, ' '.join(tmp))
        raise CmdInputError(em)

    if resistance < 0:
        em = '{}: {} requires a source resistance of zero or greater'.format(cmdname, ' '.join(tmp))
        raise CmdInputError(em)

    # Check if there is a waveform_id in the waveforms list
    if not any(x.ID == tmp[5] for x in G.waveforms):
        em = '{}: {} there is no waveform with the identifier {}'.format(cmdname, ' '.join(tmp), waveform_id)
        raise CmdInputError(em)

    p1 = grid.calculate_disc_coord_3(xcoord, ycoord, zcoord)
    grid.are_coords_within_bounds(p1)

    nx, ny, nz = grid.calculate_coord_3(*p1)

    # Check that the source isn't within the pml region of the main grid
    if (xcoord < G.pmlthickness['x0']
        or xcoord > G.nx - G.pmlthickness['xmax']
        or ycoord < G.pmlthickness['y0']
        or ycoord > G.ny - G.pmlthickness['ymax']
        or zcoord < G.pmlthickness['z0']
        or zcoord > G.nz - G.pmlthickness['zmax']):

        print(Fore.RED + "WARNING: '" + cmdname + ': ' + ' '.join(tmp) + "'" + ' sources and receivers should not normally be positioned within the PML.' + Style.RESET_ALL)

    v = VoltageSource()
    v.polarisation = polarisation
    v.xcoord = nx
    v.ycoord = ny
    v.zcoord = nz
    v.ID = v.ID = v.__class__.__name__ + '(' + str(v.xcoord) + ',' + str(v.ycoord) + ',' + str(v.zcoord) + ')'
    v.resistance = resistance
    v.waveformID = waveform_id
    v.start = start
    v.stop = stop

    v.calculate_waveform_values(grid)

    if G.messages:
        print('Voltage source with polarity {} at {:g}m, {:g}m, {:g}m, resistance {:.1f} Ohms,'.format(v.polarisation, v.xcoord * G.dx, v.ycoord * G.dy, v.zcoord * G.dz, v.resistance) + startstop + 'using waveform {} created.'.format(v.waveformID))

    grid.voltagesources.append(v)