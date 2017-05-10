from ..exceptions import CmdInputError
from ..materials import PeplinskiSoil


def create_soil_peplinski(multicmds, G):
    cmdname = '#soil_peplinski'
    if multicmds[cmdname] is not None:
        for cmdinstance in multicmds[cmdname]:
            tmp = cmdinstance.split()
            if len(tmp) != 7:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires at exactly seven parameters')
            if float(tmp[0]) < 0:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires a positive value for the sand fraction')
            if float(tmp[1]) < 0:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires a positive value for the clay fraction')
            if float(tmp[2]) < 0:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires a positive value for the bulk density')
            if float(tmp[3]) < 0:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires a positive value for the sand particle density')
            if float(tmp[4]) < 0:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires a positive value for the lower limit of the water volumetric fraction')
            if float(tmp[5]) < 0:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires a positive value for the upper limit of the water volumetric fraction')
            if any(x.ID == tmp[6] for x in G.mixingmodels):
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' with ID {} already exists'.format(tmp[6]))

            # Create a new instance of the Material class material (start index after pec & free_space)
            s = PeplinskiSoil(tmp[6], float(tmp[0]), float(tmp[1]), float(tmp[2]), float(tmp[3]), (float(tmp[4]), float(tmp[5])))

            if G.messages:
                print('Mixing model (Peplinski) used to create {} with sand fraction {:g}, clay fraction {:g}, bulk density {:g}g/cm3, sand particle density {:g}g/cm3, and water volumetric fraction {:g} to {:g} created.'.format(s.ID, s.S, s.C, s.rb, s.rs, s.mu[0], s.mu[1]))

            # Append the new material object to the materials list
            G.mixingmodels.append(s)
