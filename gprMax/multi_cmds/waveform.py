from ..waveforms import Waveform
from ..exceptions import CmdInputError


def create_waveforms(multicmds, G):
    # Waveform definitions
    cmdname = '#waveform'
    if multicmds[cmdname] is not None:
        for cmdinstance in multicmds[cmdname]:
            tmp = cmdinstance.split()
            if len(tmp) != 4:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires exactly four parameters')
            if tmp[0].lower() not in Waveform.types:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' must have one of the following types {}'.format(','.join(Waveform.types)))
            if float(tmp[2]) <= 0:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires an excitation frequency value of greater than zero')
            if any(x.ID == tmp[3] for x in G.waveforms):
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' with ID {} already exists'.format(tmp[3]))

            w = Waveform()
            w.ID = tmp[3]
            w.type = tmp[0].lower()
            w.amp = float(tmp[1])
            w.freq = float(tmp[2])

            if G.messages:
                print('Waveform {} of type {} with maximum amplitude scaling {:g}, frequency {:g}Hz created.'.format(w.ID, w.type, w.amp, w.freq))

            G.waveforms.append(w)
