from ..sources import MagneticDipole
from ..exceptions import CmdInputError


def create_magnetic_dipoles(multicmds, G):
    # Magnetic dipole
    cmdname = '#magnetic_dipole'
    if multicmds[cmdname] is not None:
        for cmdinstance in multicmds[cmdname]:
            tmp = cmdinstance.split()
            if len(tmp) < 5:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires at least five parameters')

            # Check polarity & position parameters
            polarisation = tmp[0].lower()
            if polarisation not in ('x', 'y', 'z'):
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' polarisation must be x, y, or z')

            xcoord = G.calculate_coord('x', tmp[1])
            ycoord = G.calculate_coord('y', tmp[2])
            zcoord = G.calculate_coord('z', tmp[3])
            check_coordinates(xcoord, ycoord, zcoord)
            if xcoord < G.pmlthickness['x0'] or xcoord > G.nx - G.pmlthickness['xmax'] or ycoord < G.pmlthickness['y0'] or ycoord > G.ny - G.pmlthickness['ymax'] or zcoord < G.pmlthickness['z0'] or zcoord > G.nz - G.pmlthickness['zmax']:
                print(Fore.RED + "WARNING: '" + cmdname + ': ' + ' '.join(tmp) + "'" + ' sources and receivers should not normally be positioned within the PML.' + Style.RESET_ALL)

            # Check if there is a waveformID in the waveforms list
            if not any(x.ID == tmp[4] for x in G.waveforms):
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' there is no waveform with the identifier {}'.format(tmp[4]))

            m = MagneticDipole()
            m.polarisation = polarisation
            m.xcoord = xcoord
            m.ycoord = ycoord
            m.zcoord = zcoord
            m.xcoordorigin = xcoord
            m.ycoordorigin = ycoord
            m.zcoordorigin = zcoord
            m.ID = m.__class__.__name__ + '(' + str(m.xcoord) + ',' + str(m.ycoord) + ',' + str(m.zcoord) + ')'
            m.waveformID = tmp[4]

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
                m.start = start
                if stop > G.timewindow:
                    m.stop = G.timewindow
                else:
                    m.stop = stop
                startstop = ' start time {:g} secs, finish time {:g} secs '.format(m.start, m.stop)
            else:
                m.start = 0
                m.stop = G.timewindow
                startstop = ' '

            m.calculate_waveform_values(G)

            if G.messages:
                print('Magnetic dipole with polarity {} at {:g}m, {:g}m, {:g}m,'.format(m.polarisation, m.xcoord * G.dx, m.ycoord * G.dy, m.zcoord * G.dz) + startstop + 'using waveform {} created.'.format(m.waveformID))

            G.magneticdipoles.append(m)
