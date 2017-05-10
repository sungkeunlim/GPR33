from ..exceptions import CmdInputError
from ..sources import TransmissionLine
from .common import check_coordinates


def create_transmission_lines(multicmds, G):
    # Transmission line
    cmdname = '#transmission_line'
    if multicmds[cmdname] is not None:
        for cmdinstance in multicmds[cmdname]:
            tmp = cmdinstance.split()
            if len(tmp) < 6:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires at least six parameters')

            # Check polarity & position parameters
            polarisation = tmp[0].lower()
            if polarisation not in ('x', 'y', 'z'):
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' polarisation must be x, y, or z')

            xcoord = G.calculate_coord('x', tmp[1])
            ycoord = G.calculate_coord('y', tmp[2])
            zcoord = G.calculate_coord('z', tmp[3])
            resistance = float(tmp[4])

            check_coordinates(xcoord, ycoord, zcoord)
            if xcoord < G.pmlthickness['x0'] or xcoord > G.nx - G.pmlthickness['xmax'] or ycoord < G.pmlthickness['y0'] or ycoord > G.ny - G.pmlthickness['ymax'] or zcoord < G.pmlthickness['z0'] or zcoord > G.nz - G.pmlthickness['zmax']:
                print(Fore.RED + "WARNING: '" + cmdname + ': ' + ' '.join(tmp) + "'" + ' sources and receivers should not normally be positioned within the PML.' + Style.RESET_ALL)
            if resistance <= 0 or resistance >= z0:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires a resistance greater than zero and less than the impedance of free space, i.e. 376.73 Ohms')

            # Check if there is a waveformID in the waveforms list
            if not any(x.ID == tmp[5] for x in G.waveforms):
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' there is no waveform with the identifier {}'.format(tmp[4]))

            t = TransmissionLine(G)
            t.polarisation = polarisation
            t.xcoord = xcoord
            t.ycoord = ycoord
            t.zcoord = zcoord
            t.ID = t.__class__.__name__ + '(' + str(t.xcoord) + ',' + str(t.ycoord) + ',' + str(t.zcoord) + ')'
            t.resistance = resistance
            t.waveformID = tmp[5]

            if len(tmp) > 6:
                # Check source start & source remove time parameters
                start = float(tmp[6])
                stop = float(tmp[7])
                if start < 0:
                    raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' delay of the initiation of the source should not be less than zero')
                if stop < 0:
                    raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' time to remove the source should not be less than zero')
                if stop - start <= 0:
                    raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' duration of the source should not be zero or less')
                t.start = start
                if stop > G.timewindow:
                    t.stop = G.timewindow
                else:
                    t.stop = stop
                startstop = ' start time {:g} secs, finish time {:g} secs '.format(t.start, t.stop)
            else:
                t.start = 0
                t.stop = G.timewindow
                startstop = ' '

            t.calculate_waveform_values(G)
            t.calculate_incident_V_I(G)

            if G.messages:
                print('Transmission line with polarity {} at {:g}m, {:g}m, {:g}m, resistance {:.1f} Ohms,'.format(t.polarisation, t.xcoord * G.dx, t.ycoord * G.dy, t.zcoord * G.dz, t.resistance) + startstop + 'using waveform {} created.'.format(t.waveformID))

            G.transmissionlines.append(t)
