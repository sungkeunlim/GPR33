import numpy as np
from tqdm import tqdm

from ..constants import floattype
from ..exceptions import CmdInputError
from ..fractals import FractalSurface
from ..fractals import FractalVolume
from ..fractals import Grass
from ..geometry_primitives import build_voxels_from_array
from ..geometry_primitives import build_voxels_from_array_mask
from ..materials import Material
from ..utilities import round_value


def create_fractal_box(tmp, G):
    if tmp[0] == '#fractal_box:':
        # Default is no dielectric smoothing for a fractal box
        averagefractalbox = False

        if len(tmp) < 14:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires at least thirteen parameters')
        elif len(tmp) == 14:
            seed = None
        elif len(tmp) == 15:
            seed = int(tmp[14])
        elif len(tmp) == 16:
            seed = int(tmp[14])
            if tmp[15].lower() == 'y':
                averagefractalbox = True
            elif tmp[15].lower() == 'n':
                averagefractalbox = False
            else:
                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires averaging to be either y or n')
        else:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' too many parameters have been given')

        xs = round_value(float(tmp[1]) / G.dx)
        xf = round_value(float(tmp[4]) / G.dx)
        ys = round_value(float(tmp[2]) / G.dy)
        yf = round_value(float(tmp[5]) / G.dy)
        zs = round_value(float(tmp[3]) / G.dz)
        zf = round_value(float(tmp[6]) / G.dz)

        if xs < 0 or xs > G.nx:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower x-coordinate {:g}m is not within the model domain'.format(xs * G.dx))
        if xf < 0 or xf > G.nx:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper x-coordinate {:g}m is not within the model domain'.format(xf * G.dx))
        if ys < 0 or ys > G.ny:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower y-coordinate {:g}m is not within the model domain'.format(ys * G.dy))
        if yf < 0 or yf > G.ny:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper y-coordinate {:g}m is not within the model domain'.format(yf * G.dy))
        if zs < 0 or zs > G.nz:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower z-coordinate {:g}m is not within the model domain'.format(zs * G.dz))
        if zf < 0 or zf > G.nz:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper z-coordinate {:g}m is not within the model domain'.format(zf * G.dz))
        if xs >= xf or ys >= yf or zs >= zf:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower coordinates should be less than the upper coordinates')
        if float(tmp[7]) < 0:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires a positive value for the fractal dimension')
        if float(tmp[8]) < 0:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires a positive value for the fractal weighting in the x direction')
        if float(tmp[9]) < 0:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires a positive value for the fractal weighting in the y direction')
        if float(tmp[10]) < 0:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires a positive value for the fractal weighting in the z direction')
        if round_value(tmp[11]) < 0:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires a positive value for the number of bins')

        # Find materials to use to build fractal volume, either from mixing models or normal materials
        mixingmodel = next((x for x in G.mixingmodels if x.ID == tmp[12]), None)
        material = next((x for x in G.materials if x.ID == tmp[12]), None)
        nbins = round_value(tmp[11])

        if mixingmodel:
            if nbins == 1:
                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' must be used with more than one material from the mixing model.')
            # Create materials from mixing model as number of bins now known from fractal_box command
            mixingmodel.calculate_debye_properties(nbins, G)
        elif not material:
            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' mixing model or material with ID {} does not exist'.format(tmp[12]))

        volume = FractalVolume(xs, xf, ys, yf, zs, zf, float(tmp[7]))
        volume.ID = tmp[13]
        volume.operatingonID = tmp[12]
        volume.nbins = nbins
        volume.seed = seed
        volume.weighting = (float(tmp[8]), float(tmp[9]), float(tmp[10]))
        try:
            volume.averaging = averagefractalbox
        except:
            pass

        if G.messages:
            if volume.averaging:
                dielectricsmoothing = 'on'
            else:
                dielectricsmoothing = 'off'
            tqdm.write('Fractal box {} from {:g}m, {:g}m, {:g}m, to {:g}m, {:g}m, {:g}m with {}, fractal dimension {:g}, fractal weightings {:g}, {:g}, {:g}, fractal seeding {}, with {} material(s) created, dielectric smoothing is {}.'.format(volume.ID, xs * G.dx, ys * G.dy, zs * G.dz, xf * G.dx, yf * G.dy, zf * G.dz, volume.operatingonID, volume.dimension, volume.weighting[0], volume.weighting[1], volume.weighting[2], volume.seed, volume.nbins, dielectricsmoothing))

        G.fractalvolumes.append(volume)

        # Search and process any modifiers for the fractal box
        for object in geometry:
            tmp = object.split()

            if tmp[0] == '#add_surface_roughness:':
                if len(tmp) < 13:
                    raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires at least twelve parameters')
                elif len(tmp) == 13:
                    seed = None
                elif len(tmp) == 14:
                    seed = int(tmp[13])
                else:
                    raise CmdInputError("'" + ' '.join(tmp) + "'" + ' too many parameters have been given')

                # Only process rough surfaces for this fractal volume
                if tmp[12] == volume.ID:
                    xs = round_value(float(tmp[1]) / G.dx)
                    xf = round_value(float(tmp[4]) / G.dx)
                    ys = round_value(float(tmp[2]) / G.dy)
                    yf = round_value(float(tmp[5]) / G.dy)
                    zs = round_value(float(tmp[3]) / G.dz)
                    zf = round_value(float(tmp[6]) / G.dz)

                    if xs < 0 or xs > G.nx:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower x-coordinate {:g}m is not within the model domain'.format(xs * G.dx))
                    if xf < 0 or xf > G.nx:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper x-coordinate {:g}m is not within the model domain'.format(xf * G.dx))
                    if ys < 0 or ys > G.ny:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower y-coordinate {:g}m is not within the model domain'.format(ys * G.dy))
                    if yf < 0 or yf > G.ny:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper y-coordinate {:g}m is not within the model domain'.format(yf * G.dy))
                    if zs < 0 or zs > G.nz:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower z-coordinate {:g}m is not within the model domain'.format(zs * G.dz))
                    if zf < 0 or zf > G.nz:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper z-coordinate {:g}m is not within the model domain'.format(zf * G.dz))
                    if xs > xf or ys > yf or zs > zf:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower coordinates should be less than the upper coordinates')
                    if float(tmp[7]) < 0:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires a positive value for the fractal dimension')
                    if float(tmp[8]) < 0:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires a positive value for the fractal weighting in the first direction of the surface')
                    if float(tmp[9]) < 0:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires a positive value for the fractal weighting in the second direction of the surface')

                    # Check for valid orientations
                    if xs == xf:
                        if ys == yf or zs == zf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' dimensions are not specified correctly')
                        if xs != volume.xs and xs != volume.xf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' can only be used on the external surfaces of a fractal box')
                        fractalrange = (round_value(float(tmp[10]) / G.dx), round_value(float(tmp[11]) / G.dx))
                        # xminus surface
                        if xs == volume.xs:
                            if fractalrange[0] < 0:
                                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' cannot apply fractal surface to fractal box as it would exceed the domain size in the x direction')
                            requestedsurface = 'xminus'
                        # xplus surface
                        elif xf == volume.xf:
                            if fractalrange[1] > G.nx:
                                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' cannot apply fractal surface to fractal box as it would exceed the domain size in the x direction')
                            requestedsurface = 'xplus'

                    elif ys == yf:
                        if xs == xf or zs == zf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' dimensions are not specified correctly')
                        if ys != volume.ys and ys != volume.yf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' can only be used on the external surfaces of a fractal box')
                        fractalrange = (round_value(float(tmp[10]) / G.dy), round_value(float(tmp[11]) / G.dy))
                        # yminus surface
                        if ys == volume.ys:
                            if fractalrange[0] < 0:
                                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' cannot apply fractal surface to fractal box as it would exceed the domain size in the y direction')
                            requestedsurface = 'yminus'
                        # yplus surface
                        elif yf == volume.yf:
                            if fractalrange[1] > G.ny:
                                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' cannot apply fractal surface to fractal box as it would exceed the domain size in the y direction')
                            requestedsurface = 'yplus'

                    elif zs == zf:
                        if xs == xf or ys == yf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' dimensions are not specified correctly')
                        if zs != volume.zs and zs != volume.zf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' can only be used on the external surfaces of a fractal box')
                        fractalrange = (round_value(float(tmp[10]) / G.dz), round_value(float(tmp[11]) / G.dz))
                        # zminus surface
                        if zs == volume.zs:
                            if fractalrange[0] < 0:
                                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' cannot apply fractal surface to fractal box as it would exceed the domain size in the z direction')
                            requestedsurface = 'zminus'
                        # zplus surface
                        elif zf == volume.zf:
                            if fractalrange[1] > G.nz:
                                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' cannot apply fractal surface to fractal box as it would exceed the domain size in the z direction')
                            requestedsurface = 'zplus'

                    else:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' dimensions are not specified correctly')

                    surface = FractalSurface(xs, xf, ys, yf, zs, zf, float(tmp[7]))
                    surface.surfaceID = requestedsurface
                    surface.fractalrange = fractalrange
                    surface.operatingonID = volume.ID
                    surface.seed = seed
                    surface.weighting = (float(tmp[8]), float(tmp[9]))

                    # List of existing surfaces IDs
                    existingsurfaceIDs = [x.surfaceID for x in volume.fractalsurfaces]
                    if surface.surfaceID in existingsurfaceIDs:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' has already been used on the {} surface'.format(surface.surfaceID))

                    surface.generate_fractal_surface()
                    volume.fractalsurfaces.append(surface)

                    if G.messages:
                        tqdm.write('Fractal surface from {:g}m, {:g}m, {:g}m, to {:g}m, {:g}m, {:g}m with fractal dimension {:g}, fractal weightings {:g}, {:g}, fractal seeding {}, and range {:g}m to {:g}m, added to {}.'.format(xs * G.dx, ys * G.dy, zs * G.dz, xf * G.dx, yf * G.dy, zf * G.dz, surface.dimension, surface.weighting[0], surface.weighting[1], surface.seed, float(tmp[10]), float(tmp[11]), surface.operatingonID))

            if tmp[0] == '#add_surface_water:':
                if len(tmp) != 9:
                    raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires exactly eight parameters')

                # Only process surfaces for this fractal volume
                if tmp[8] == volume.ID:
                    xs = round_value(float(tmp[1]) / G.dx)
                    xf = round_value(float(tmp[4]) / G.dx)
                    ys = round_value(float(tmp[2]) / G.dy)
                    yf = round_value(float(tmp[5]) / G.dy)
                    zs = round_value(float(tmp[3]) / G.dz)
                    zf = round_value(float(tmp[6]) / G.dz)
                    depth = float(tmp[7])

                    if xs < 0 or xs > G.nx:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower x-coordinate {:g}m is not within the model domain'.format(xs * G.dx))
                    if xf < 0 or xf > G.nx:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper x-coordinate {:g}m is not within the model domain'.format(xf * G.dx))
                    if ys < 0 or ys > G.ny:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower y-coordinate {:g}m is not within the model domain'.format(ys * G.dy))
                    if yf < 0 or yf > G.ny:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper y-coordinate {:g}m is not within the model domain'.format(yf * G.dy))
                    if zs < 0 or zs > G.nz:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower z-coordinate {:g}m is not within the model domain'.format(zs * G.dz))
                    if zf < 0 or zf > G.nz:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper z-coordinate {:g}m is not within the model domain'.format(zf * G.dz))
                    if xs > xf or ys > yf or zs > zf:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower coordinates should be less than the upper coordinates')
                    if depth <= 0:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires a positive value for the depth of water')

                    # Check for valid orientations
                    if xs == xf:
                        if ys == yf or zs == zf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' dimensions are not specified correctly')
                        if xs != volume.xs and xs != volume.xf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' can only be used on the external surfaces of a fractal box')
                        # xminus surface
                        if xs == volume.xs:
                            requestedsurface = 'xminus'
                        # xplus surface
                        elif xf == volume.xf:
                            requestedsurface = 'xplus'
                        filldepthcells = round_value(depth / G.dx)
                        filldepth = filldepthcells * G.dx

                    elif ys == yf:
                        if xs == xf or zs == zf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' dimensions are not specified correctly')
                        if ys != volume.ys and ys != volume.yf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' can only be used on the external surfaces of a fractal box')
                        # yminus surface
                        if ys == volume.ys:
                            requestedsurface = 'yminus'
                        # yplus surface
                        elif yf == volume.yf:
                            requestedsurface = 'yplus'
                        filldepthcells = round_value(depth / G.dy)
                        filldepth = filldepthcells * G.dy

                    elif zs == zf:
                        if xs == xf or ys == yf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' dimensions are not specified correctly')
                        if zs != volume.zs and zs != volume.zf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' can only be used on the external surfaces of a fractal box')
                        # zminus surface
                        if zs == volume.zs:
                            requestedsurface = 'zminus'
                        # zplus surface
                        elif zf == volume.zf:
                            requestedsurface = 'zplus'
                        filldepthcells = round_value(depth / G.dz)
                        filldepth = filldepthcells * G.dz

                    else:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' dimensions are not specified correctly')

                    surface = next((x for x in volume.fractalsurfaces if x.surfaceID == requestedsurface), None)
                    if not surface:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' specified surface {} does not have a rough surface applied'.format(requestedsurface))

                    surface.filldepth = filldepthcells

                    # Check that requested fill depth falls within range of surface roughness
                    if surface.filldepth < surface.fractalrange[0] or surface.filldepth > surface.fractalrange[1]:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires a value for the depth of water that lies with the range of the requested surface roughness')

                    # Check to see if water has been already defined as a material
                    if not any(x.ID == 'water' for x in G.materials):
                        m = Material(len(G.materials), 'water')
                        m.averagable = False
                        m.type = 'builtin, debye'
                        m.er = Material.watereri
                        m.deltaer.append(Material.waterdeltaer)
                        m.tau.append(Material.watertau)
                        G.materials.append(m)
                        if Material.maxpoles == 0:
                            Material.maxpoles = 1

                    # Check if time step for model is suitable for using water
                    water = next((x for x in G.materials if x.ID == 'water'))
                    testwater = next((x for x in water.tau if x < G.dt), None)
                    if testwater:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires the time step for the model to be less than the relaxation time required to model water.')

                    if G.messages:
                        tqdm.write('Water on surface from {:g}m, {:g}m, {:g}m, to {:g}m, {:g}m, {:g}m with depth {:g}m, added to {}.'.format(xs * G.dx, ys * G.dy, zs * G.dz, xf * G.dx, yf * G.dy, zf * G.dz, filldepth, surface.operatingonID))

            if tmp[0] == '#add_grass:':
                if len(tmp) < 12:
                    raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires at least eleven parameters')
                elif len(tmp) == 12:
                    seed = None
                elif len(tmp) == 13:
                    seed = int(tmp[12])
                else:
                    raise CmdInputError("'" + ' '.join(tmp) + "'" + ' too many parameters have been given')

                # Only process grass for this fractal volume
                if tmp[11] == volume.ID:
                    xs = round_value(float(tmp[1]) / G.dx)
                    xf = round_value(float(tmp[4]) / G.dx)
                    ys = round_value(float(tmp[2]) / G.dy)
                    yf = round_value(float(tmp[5]) / G.dy)
                    zs = round_value(float(tmp[3]) / G.dz)
                    zf = round_value(float(tmp[6]) / G.dz)
                    numblades = int(tmp[10])

                    if xs < 0 or xs > G.nx:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower x-coordinate {:g}m is not within the model domain'.format(xs * G.dx))
                    if xf < 0 or xf > G.nx:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper x-coordinate {:g}m is not within the model domain'.format(xf * G.dx))
                    if ys < 0 or ys > G.ny:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower y-coordinate {:g}m is not within the model domain'.format(ys * G.dy))
                    if yf < 0 or yf > G.ny:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper y-coordinate {:g}m is not within the model domain'.format(yf * G.dy))
                    if zs < 0 or zs > G.nz:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower z-coordinate {:g}m is not within the model domain'.format(zs * G.dz))
                    if zf < 0 or zf > G.nz:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the upper z-coordinate {:g}m is not within the model domain'.format(zf * G.dz))
                    if xs > xf or ys > yf or zs > zf:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the lower coordinates should be less than the upper coordinates')
                    if float(tmp[7]) < 0:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires a positive value for the fractal dimension')
                    if float(tmp[8]) < 0 or float(tmp[9]) < 0:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires a positive value for the minimum and maximum heights for grass blades')

                    # Check for valid orientations
                    if xs == xf:
                        if ys == yf or zs == zf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' dimensions are not specified correctly')
                        if xs != volume.xs and xs != volume.xf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' must specify external surfaces on a fractal box')
                        fractalrange = (round_value(float(tmp[8]) / G.dx), round_value(float(tmp[9]) / G.dx))
                        # xminus surface
                        if xs == volume.xs:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' grass can only be specified on surfaces in the positive axis direction')
                        # xplus surface
                        elif xf == volume.xf:
                            if fractalrange[1] > G.nx:
                                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' cannot apply grass to fractal box as it would exceed the domain size in the x direction')
                            requestedsurface = 'xplus'

                    elif ys == yf:
                        if xs == xf or zs == zf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' dimensions are not specified correctly')
                        if ys != volume.ys and ys != volume.yf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' must specify external surfaces on a fractal box')
                        fractalrange = (round_value(float(tmp[8]) / G.dy), round_value(float(tmp[9]) / G.dy))
                        # yminus surface
                        if ys == volume.ys:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' grass can only be specified on surfaces in the positive axis direction')
                        # yplus surface
                        elif yf == volume.yf:
                            if fractalrange[1] > G.ny:
                                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' cannot apply grass to fractal box as it would exceed the domain size in the y direction')
                            requestedsurface = 'yplus'

                    elif zs == zf:
                        if xs == xf or ys == yf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' dimensions are not specified correctly')
                        if zs != volume.zs and zs != volume.zf:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' must specify external surfaces on a fractal box')
                        fractalrange = (round_value(float(tmp[8]) / G.dz), round_value(float(tmp[9]) / G.dz))
                        # zminus surface
                        if zs == volume.zs:
                            raise CmdInputError("'" + ' '.join(tmp) + "'" + ' grass can only be specified on surfaces in the positive axis direction')
                        # zplus surface
                        elif zf == volume.zf:
                            if fractalrange[1] > G.nz:
                                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' cannot apply grass to fractal box as it would exceed the domain size in the z direction')
                            requestedsurface = 'zplus'

                    else:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' dimensions are not specified correctly')

                    surface = FractalSurface(xs, xf, ys, yf, zs, zf, float(tmp[7]))
                    surface.ID = 'grass'
                    surface.surfaceID = requestedsurface
                    surface.seed = seed

                    # Set the fractal range to scale the fractal distribution between zero and one
                    surface.fractalrange = (0, 1)
                    surface.operatingonID = volume.ID
                    surface.generate_fractal_surface()
                    if numblades > surface.fractalsurface.shape[0] * surface.fractalsurface.shape[1]:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' the specified surface is not large enough for the number of grass blades/roots specified')

                    # Scale the distribution so that the summation is equal to one, i.e. a probability distribution
                    surface.fractalsurface = surface.fractalsurface / np.sum(surface.fractalsurface)

                    # Set location of grass blades using probability distribution
                    # Create 1D vector of probability values from the 2D surface
                    probability1D = np.cumsum(np.ravel(surface.fractalsurface))

                    # Create random numbers between zero and one for the number of blades of grass
                    R = np.random.RandomState(surface.seed)
                    A = R.random_sample(numblades)

                    # Locate the random numbers in the bins created by the 1D vector of probability values, and convert the 1D index back into a x, y index for the original surface.
                    bladesindex = np.unravel_index(np.digitize(A, probability1D), (surface.fractalsurface.shape[0], surface.fractalsurface.shape[1]))

                    # Set the fractal range to minimum and maximum heights of the grass blades
                    surface.fractalrange = fractalrange

                    # Set the fractal surface using the pre-calculated spatial distribution and a random height
                    surface.fractalsurface = np.zeros((surface.fractalsurface.shape[0], surface.fractalsurface.shape[1]))
                    for i in range(len(bladesindex[0])):
                            surface.fractalsurface[bladesindex[0][i], bladesindex[1][i]] = R.randint(surface.fractalrange[0], surface.fractalrange[1], size=1)

                    # Create grass geometry parameters
                    g = Grass(numblades)
                    g.seed = surface.seed
                    surface.grass.append(g)

                    # Check to see if grass has been already defined as a material
                    if not any(x.ID == 'grass' for x in G.materials):
                        m = Material(len(G.materials), 'grass')
                        m.averagable = False
                        m.type = 'builtin, debye'
                        m.er = Material.grasseri
                        m.deltaer.append(Material.grassdeltaer)
                        m.tau.append(Material.grasstau)
                        G.materials.append(m)
                        if Material.maxpoles == 0:
                            Material.maxpoles = 1

                    # Check if time step for model is suitable for using grass
                    grass = next((x for x in G.materials if x.ID == 'grass'))
                    testgrass = next((x for x in grass.tau if x < G.dt), None)
                    if testgrass:
                        raise CmdInputError("'" + ' '.join(tmp) + "'" + ' requires the time step for the model to be less than the relaxation time required to model grass.')

                    volume.fractalsurfaces.append(surface)

                    if G.messages:
                        tqdm.write('{} blades of grass on surface from {:g}m, {:g}m, {:g}m, to {:g}m, {:g}m, {:g}m with fractal dimension {:g}, fractal seeding {}, and range {:g}m to {:g}m, added to {}.'.format(numblades, xs * G.dx, ys * G.dy, zs * G.dz, xf * G.dx, yf * G.dy, zf * G.dz, surface.dimension, surface.seed, float(tmp[8]), float(tmp[9]), surface.operatingonID))

        # Process any modifications to the original fractal box then generate it
        if volume.fractalsurfaces:
            volume.originalxs = volume.xs
            volume.originalxf = volume.xf
            volume.originalys = volume.ys
            volume.originalyf = volume.yf
            volume.originalzs = volume.zs
            volume.originalzf = volume.zf

            # Extend the volume to accomodate any rough surfaces, grass, or roots
            for surface in volume.fractalsurfaces:
                if surface.surfaceID == 'xminus':
                    if surface.fractalrange[0] < volume.xs:
                        volume.nx += volume.xs - surface.fractalrange[0]
                        volume.xs = surface.fractalrange[0]
                elif surface.surfaceID == 'xplus':
                    if surface.fractalrange[1] > volume.xf:
                        volume.nx += surface.fractalrange[1] - volume.xf
                        volume.xf = surface.fractalrange[1]
                elif surface.surfaceID == 'yminus':
                    if surface.fractalrange[0] < volume.ys:
                        volume.ny += volume.ys - surface.fractalrange[0]
                        volume.ys = surface.fractalrange[0]
                elif surface.surfaceID == 'yplus':
                    if surface.fractalrange[1] > volume.yf:
                        volume.ny += surface.fractalrange[1] - volume.yf
                        volume.yf = surface.fractalrange[1]
                elif surface.surfaceID == 'zminus':
                    if surface.fractalrange[0] < volume.zs:
                        volume.nz += volume.zs - surface.fractalrange[0]
                        volume.zs = surface.fractalrange[0]
                elif surface.surfaceID == 'zplus':
                    if surface.fractalrange[1] > volume.zf:
                        volume.nz += surface.fractalrange[1] - volume.zf
                        volume.zf = surface.fractalrange[1]

            # If there is only 1 bin then a normal material is being used, otherwise a mixing model
            if volume.nbins == 1:
                volume.fractalvolume = np.ones((volume.nx, volume.ny, volume.nz), dtype=floattype)
                materialnumID = next(x.numID for x in G.materials if x.ID == volume.operatingonID)
                volume.fractalvolume *= materialnumID
            else:
                volume.generate_fractal_volume()
                volume.fractalvolume += mixingmodel.startmaterialnum

            volume.generate_volume_mask()

            # Apply any rough surfaces and add any surface water to the 3D mask array
            for surface in volume.fractalsurfaces:
                if surface.surfaceID == 'xminus':
                    for i in range(surface.fractalrange[0], surface.fractalrange[1]):
                        for j in range(surface.ys, surface.yf):
                            for k in range(surface.zs, surface.zf):
                                if i > surface.fractalsurface[j - surface.ys, k - surface.zs]:
                                    volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 1
                                elif surface.filldepth > 0 and i > surface.filldepth:
                                    volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 2
                                else:
                                    volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 0

                elif surface.surfaceID == 'xplus':
                    if not surface.ID:
                        for i in range(surface.fractalrange[0], surface.fractalrange[1]):
                            for j in range(surface.ys, surface.yf):
                                for k in range(surface.zs, surface.zf):
                                    if i < surface.fractalsurface[j - surface.ys, k - surface.zs]:
                                        volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 1
                                    elif surface.filldepth > 0 and i < surface.filldepth:
                                        volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 2
                                    else:
                                        volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 0
                    elif surface.ID == 'grass':
                        g = surface.grass[0]
                        # Build the blades of the grass
                        blade = 0
                        for j in range(surface.ys, surface.yf):
                            for k in range(surface.zs, surface.zf):
                                if surface.fractalsurface[j - surface.ys, k - surface.zs] > 0:
                                    height = 0
                                    blade += 1
                                    for i in range(volume.xs, surface.fractalrange[1]):
                                        if i < surface.fractalsurface[j - surface.ys, k - surface.zs] and volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] != 1:
                                            y, z = g.calculate_blade_geometry(blade - 1, height)
                                            # Add y, z coordinates to existing location
                                            yy = j - volume.ys + y
                                            zz = k - volume.zs + z
                                            # If these coordinates are outwith fractal volume stop building the blade, otherwise set the mask for grass
                                            if yy < 0 or yy >= volume.mask.shape[1] or zz < 0 or zz >= volume.mask.shape[2]:
                                                break
                                            else:
                                                volume.mask[i - volume.xs, yy, zz] = 3
                                                height += 1
                        # Build the roots of the grass
                        blade = 0
                        for j in range(surface.ys, surface.yf):
                            for k in range(surface.zs, surface.zf):
                                if surface.fractalsurface[j - surface.ys, k - surface.zs] > 0:
                                    depth = 0
                                    blade += 1
                                    i = volume.xf
                                    while i > volume.xs:
                                        if i > volume.originalxf - (surface.fractalsurface[j - surface.ys, k - surface.zs] - volume.originalxf) and volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] == 1:
                                            y, z = g.calculate_root_geometry(blade - 1, depth)
                                            # Add y, z coordinates to existing location
                                            yy = j - volume.ys + y
                                            zz = k - volume.zs + z
                                            # If these coordinates are outwith the fractal volume stop building the root, otherwise set the mask for grass
                                            if yy < 0 or yy >= volume.mask.shape[1] or zz < 0 or zz >= volume.mask.shape[2]:
                                                break
                                            else:
                                                volume.mask[i - volume.xs, yy, zz] = 3
                                                depth += 1
                                        i -= 1

                elif surface.surfaceID == 'yminus':
                    for i in range(surface.xs, surface.xf):
                        for j in range(surface.fractalrange[0], surface.fractalrange[1]):
                            for k in range(surface.zs, surface.zf):
                                if j > surface.fractalsurface[i - surface.xs, k - surface.zs]:
                                    volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 1
                                elif surface.filldepth > 0 and j > surface.filldepth:
                                    volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 2
                                else:
                                    volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 0

                elif surface.surfaceID == 'yplus':
                    if not surface.ID:
                        for i in range(surface.xs, surface.xf):
                            for j in range(surface.fractalrange[0], surface.fractalrange[1]):
                                for k in range(surface.zs, surface.zf):
                                    if j < surface.fractalsurface[i - surface.xs, k - surface.zs]:
                                        volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 1
                                    elif surface.filldepth > 0 and j < surface.filldepth:
                                        volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 2
                                    else:
                                        volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 0
                    elif surface.ID == 'grass':
                        g = surface.grass[0]
                        # Build the blades of the grass
                        blade = 0
                        for i in range(surface.xs, surface.xf):
                            for k in range(surface.zs, surface.zf):
                                if surface.fractalsurface[i - surface.xs, k - surface.zs] > 0:
                                    height = 0
                                    blade += 1
                                    for j in range(volume.ys, surface.fractalrange[1]):
                                        if j < surface.fractalsurface[i - surface.xs, k - surface.zs] and volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] != 1:
                                            x, z = g.calculate_blade_geometry(blade - 1, height)
                                            # Add x, z coordinates to existing location
                                            xx = i - volume.xs + x
                                            zz = k - volume.zs + z
                                            # If these coordinates are outwith fractal volume stop building the blade, otherwise set the mask for grass
                                            if xx < 0 or xx >= volume.mask.shape[0] or zz < 0 or zz >= volume.mask.shape[2]:
                                                break
                                            else:
                                                volume.mask[xx, j - volume.ys, zz] = 3
                                                height += 1
                        # Build the roots of the grass
                        blade = 0
                        for i in range(surface.xs, surface.xf):
                            for k in range(surface.zs, surface.zf):
                                if surface.fractalsurface[i - surface.xs, k - surface.zs] > 0:
                                    depth = 0
                                    blade += 1
                                    j = volume.yf
                                    while j > volume.ys:
                                        if j > volume.originalyf - (surface.fractalsurface[i - surface.xs, k - surface.zs] - volume.originalyf) and volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] == 1:
                                            x, z = g.calculate_root_geometry(blade - 1, depth)
                                            # Add x, z coordinates to existing location
                                            xx = i - volume.xs + x
                                            zz = k - volume.zs + z
                                            # If these coordinates are outwith the fractal volume stop building the root, otherwise set the mask for grass
                                            if xx < 0 or xx >= volume.mask.shape[0] or zz < 0 or zz >= volume.mask.shape[2]:
                                                break
                                            else:
                                                volume.mask[xx, j - volume.ys, zz] = 3
                                                depth += 1
                                        j -= 1

                elif surface.surfaceID == 'zminus':
                    for i in range(surface.xs, surface.xf):
                        for j in range(surface.ys, surface.yf):
                            for k in range(surface.fractalrange[0], surface.fractalrange[1]):
                                if k > surface.fractalsurface[i - surface.xs, j - surface.ys]:
                                    volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 1
                                elif surface.filldepth > 0 and k > surface.filldepth:
                                    volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 2
                                else:
                                    volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 0

                elif surface.surfaceID == 'zplus':
                    if not surface.ID:
                        for i in range(surface.xs, surface.xf):
                            for j in range(surface.ys, surface.yf):
                                for k in range(surface.fractalrange[0], surface.fractalrange[1]):
                                    if k < surface.fractalsurface[i - surface.xs, j - surface.ys]:
                                        volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 1
                                    elif surface.filldepth > 0 and k < surface.filldepth:
                                        volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 2
                                    else:
                                        volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] = 0
                    elif surface.ID == 'grass':
                        g = surface.grass[0]
                        # Build the blades of the grass
                        blade = 0
                        for i in range(surface.xs, surface.xf):
                            for j in range(surface.ys, surface.yf):
                                if surface.fractalsurface[i - surface.xs, j - surface.ys] > 0:
                                    height = 0
                                    blade += 1
                                    for k in range(volume.zs, surface.fractalrange[1]):
                                        if k < surface.fractalsurface[i - surface.xs, j - surface.ys] and volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] != 1:
                                            x, y = g.calculate_blade_geometry(blade - 1, height)
                                            # Add x, y coordinates to existing location
                                            xx = i - volume.xs + x
                                            yy = j - volume.ys + y
                                            # If these coordinates are outwith the fractal volume stop building the blade, otherwise set the mask for grass
                                            if xx < 0 or xx >= volume.mask.shape[0] or yy < 0 or yy >= volume.mask.shape[1]:
                                                break
                                            else:
                                                volume.mask[xx, yy, k - volume.zs] = 3
                                                height += 1
                        # Build the roots of the grass
                        blade = 0
                        for i in range(surface.xs, surface.xf):
                            for j in range(surface.ys, surface.yf):
                                if surface.fractalsurface[i - surface.xs, j - surface.ys] > 0:
                                    depth = 0
                                    blade += 1
                                    k = volume.zf
                                    while k > volume.zs:
                                        if k > volume.originalzf - (surface.fractalsurface[i - surface.xs, j - surface.ys] - volume.originalzf) and volume.mask[i - volume.xs, j - volume.ys, k - volume.zs] == 1:
                                            x, y = g.calculate_root_geometry(blade - 1, depth)
                                            # Add x, y coordinates to existing location
                                            xx = i - volume.xs + x
                                            yy = j - volume.ys + y
                                            # If these coordinates are outwith the fractal volume stop building the root, otherwise set the mask for grass
                                            if xx < 0 or xx >= volume.mask.shape[0] or yy < 0 or yy >= volume.mask.shape[1]:
                                                break
                                            else:
                                                volume.mask[xx, yy, k - volume.zs] = 3
                                                depth += 1
                                        k -= 1

            # Build voxels from any true values of the 3D mask array
            waternumID = next((x.numID for x in G.materials if x.ID == 'water'), 0)
            grassnumID = next((x.numID for x in G.materials if x.ID == 'grass'), 0)
            data = volume.fractalvolume.astype('int16', order='C')
            mask = volume.mask.copy(order='C')
            build_voxels_from_array_mask(volume.xs, volume.ys, volume.zs, waternumID, grassnumID, volume.averaging, mask, data, G.solid, G.rigidE, G.rigidH, G.ID)

        else:
            if volume.nbins == 1:
                raise CmdInputError("'" + ' '.join(tmp) + "'" + ' is being used with a single material and no modifications, therefore please use a #box command instead.')
            else:
                volume.generate_fractal_volume()
                volume.fractalvolume += mixingmodel.startmaterialnum

            data = volume.fractalvolume.astype('int16', order='C')
            build_voxels_from_array(volume.xs, volume.ys, volume.zs, 0, volume.averaging, data, G.solid, G.rigidE, G.rigidH, G.ID)
