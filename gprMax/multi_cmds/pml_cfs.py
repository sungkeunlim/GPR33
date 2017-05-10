from ..exceptions import CmdInputError
from ..pml import CFSParameter
from ..pml import CFS


def create_pml_cfs(multicmds, G):
    # Complex frequency shifted (CFS) PML parameter
    cmdname = '#pml_cfs'
    if multicmds[cmdname] is not None:
        if len(multicmds[cmdname]) > 2:
            raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' can only be used up to two times, for up to a 2nd order PML')
        for cmdinstance in multicmds[cmdname]:
            tmp = cmdinstance.split()
            if len(tmp) != 12:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' requires exactly twelve parameters')
            if tmp[0] not in CFSParameter.scalingprofiles.keys() or tmp[4] not in CFSParameter.scalingprofiles.keys() or tmp[8] not in CFSParameter.scalingprofiles.keys():
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' must have scaling type {}'.format(','.join(CFSParameter.scalingprofiles.keys())))
            if tmp[1] not in CFSParameter.scalingdirections or tmp[5] not in CFSParameter.scalingdirections or tmp[9] not in CFSParameter.scalingdirections:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' must have scaling type {}'.format(','.join(CFSParameter.scalingdirections)))
            if float(tmp[2]) < 0 or float(tmp[3]) < 0 or float(tmp[6]) < 0 or float(tmp[7]) < 0 or float(tmp[10]) < 0:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' minimum and maximum scaling values must be greater than zero')
            if float(tmp[6]) < 1:
                raise CmdInputError("'" + cmdname + ': ' + ' '.join(tmp) + "'" + ' minimum scaling value for kappa must be greater than or equal to one')

            cfsalpha = CFSParameter()
            cfsalpha.ID = 'alpha'
            cfsalpha.scalingprofile = tmp[0]
            cfsalpha.scalingdirection = tmp[1]
            cfsalpha.min = float(tmp[2])
            cfsalpha.max = float(tmp[3])
            cfskappa = CFSParameter()
            cfskappa.ID = 'kappa'
            cfskappa.scalingprofile = tmp[4]
            cfskappa.scalingdirection = tmp[5]
            cfskappa.min = float(tmp[6])
            cfskappa.max = float(tmp[7])
            cfssigma = CFSParameter()
            cfssigma.ID = 'sigma'
            cfssigma.scalingprofile = tmp[8]
            cfssigma.scalingdirection = tmp[9]
            cfssigma.min = float(tmp[10])
            if tmp[11] == 'None':
                cfssigma.max = None
            else:
                cfssigma.max = float(tmp[11])
            cfs = CFS()
            cfs.alpha = cfsalpha
            cfs.kappa = cfskappa
            cfs.sigma = cfssigma

            if G.messages:
                print('PML CFS parameters: alpha (scaling: {}, scaling direction: {}, min: {:g}, max: {:g}), kappa (scaling: {}, scaling direction: {}, min: {:g}, max: {:g}), sigma (scaling: {}, scaling direction: {}, min: {:g}, max: {}) created.'.format(cfsalpha.scalingprofile, cfsalpha.scalingdirection, cfsalpha.min, cfsalpha.max, cfskappa.scalingprofile, cfskappa.scalingdirection, cfskappa.min, cfskappa.max, cfssigma.scalingprofile, cfssigma.scalingdirection, cfssigma.min, cfssigma.max))

            G.cfs.append(cfs)
