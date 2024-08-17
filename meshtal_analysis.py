# -*- coding: utf-8 -*-
"""
mesh tally tools

"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import argparse
import logging as ntlogger
import pandas as pd
mpl.use('Agg')


class meshtally:
    """Mesh tally object data"""
    def __init__(self):
        self.idnum = None
        self.ptype = None
        self.x_bounds = []
        self.y_bounds = []
        self.z_bounds = []
        self.e_bounds = []
        self.t_bounds = []
        self.data = []
        self.x_mids = []
        self.y_mids = []
        self.z_mids = []
        self.ctype = None

    def __str__(self):
        info = ("\n Number of voxels: " + str(self.number_voxels()) +
                " \n Number of bins in: \n x-dimension- " +
                str(len(self.x_mids)) + " \n y-dimension- " +
                str(len(self.y_mids)) + "\n z-dimension- " +
                str(len(self.z_mids)) + "\n voxel volume: " +
                str(self.voxel_uniform_volume()) + " cm squared")
        return info

    def number_voxels(self):
        """
        Member function of meshtally. gets the number of midpoints to
        find number of voxels.
        Return: int
        """
        num_x = len(self.x_mids)
        num_y = len(self.y_mids)
        num_z = len(self.z_mids)
        return (num_x * num_y * num_z)

    def voxel_uniform_volume(self):
        """ Member Function of meshtally. check uniform and finds volume
        from distance to adjacent vertex.

        Returns:
            float: volume of voxel
        """
        if (check_uniform(self.x_bounds) and check_uniform(self.y_bounds) and check_uniform(self.z_bounds)):

            x = np.abs(float(self.x_bounds[1]) - float(self.x_bounds[0]))
            y = np.abs(float(self.y_bounds[1]) - float(self.y_bounds[0]))
            z = np.abs(float(self.z_bounds[1]) - float(self.z_bounds[0]))

            return x * y * z
        else:
            # non uniform volume so print such and calculate average volume
            ntlogger.info("Mesh non-uniform!")
            return self.voxel_average_volume()

    def voxel_average_volume(self):
        """
        finds the mesh average volume by finding overall volume of all meshes
        and dividing by the number of meshes
        Returns:
            float - average voxel volume
        """
        # find min x y z and max x y z respectively
        x = np.abs(np.diff(np.max(self.x_bounds), np.min(self.x_bounds)))
        y = np.abs(np.diff(np.max(self.y_bounds), np.min(self.y_bounds)))
        z = np.abs(np.diff(np.max(self.z_bounds), np.min(self.z_bounds)))
        return (x * y * z) / (self.number_voxels())


class slice_object:
    """Slice object containing data info"""
    def __init__(self):
        self.values = []
        self.errors = []
        self.axis_mids = None
        self.slice_i = None
        self.slice_j = None
        self.i_lab = None
        self.j_lab = None
        self.value = None


def check_uniform(bounds):
    """checks if elements in list are equally spaced
    Args:
        bounds (list): list of bounds
    Returns:
        bool: true if uniformly spaced
    """
    if not bounds:
        # check for empty list
        return False

    # calculate the difference    
    diff = np.diff(list(map(float, bounds)))
    # check if all differences are close
    return np.allclose(diff, diff[0])


def rel_err_hist(df, fname=None):
    """ Plots a histogram of the relative errors"""

    plot, = df.hist(column='rel_err', bins=15)
    plt.xlabel("Relative error")
    plt.ylabel("Number of voxels")
    if fname:
        plt.savefig(fname)
        ntlogger.info("produced figure: %s", fname)
    else:
        plt.show()

    return plot[0]


def filter_energy_time(data, erg=None, time=None):
    """ Filters columns by energy or time parameter"""
    if erg:
        data = data[np.isclose(data["Energy"], erg)]
    if time:
        data = data[np.isclose(data["Time"], time)]
    return data


# TODO: need to generalize to any axis
# plot slice calls extract slice
def extract_slice(mesh, value, plane, erg=None, time=None):
    """ from a given plane will find the slice of a mesh"""
    data = mesh.data
    slice_obj = slice_object()
    # filter by energy/time if needed
    data = filter_energy_time(data, erg, time)

    if plane == "XZ":
        slice_obj.slice_i = mesh.x_mids
        slice_obj.slice_j = mesh.z_mids
        slice_obj.axis_mids = mesh.y_mids
        i_ind = "x"
        j_ind = "z"
        v_ind = "y"
        slice_obj.i_lab = "X co-ord (cm)"
        slice_obj.j_lab = "Z co-ord (cm)"
    elif plane == "XY":
        slice_obj.slice_i = mesh.x_mids
        slice_obj.slice_j = mesh.y_mids
        slice_obj.axis_mids = mesh.z_mids
        i_ind = "x"
        j_ind = "y"
        v_ind = "z"
        slice_obj.i_lab = "X co-ord (cm)"
        slice_obj.j_lab = "Y co-ord (cm)"
    elif plane == "YZ":
        slice_obj.slice_i = mesh.y_mids
        slice_obj.slice_j = mesh.z_mids
        slice_obj.axis_mids = mesh.x_mids
        i_ind = "y"
        j_ind = "z"
        v_ind = "x"
        slice_obj.i_lab = "Y co-ord (cm)"
        slice_obj.j_lab = "Z co-ord (cm)"
    else:
        # Catch plane not recognised
        raise ValueError(f"Plane not recognised format : XZ, XY, YZ")

    # find closest mid point
    slice_obj.value = find_nearest_mid(value, slice_obj.axis_mids)

    # filter to just the values in the plane
    data = data[data[v_ind] == slice_obj.value]
    # create a 2d array of just values matching corresponding axis
    for i in slice_obj.slice_i:
        slice_obj.values.append((data.loc[data[i_ind] == i]['value']))
        slice_obj.errors.append((data.loc[data[j_ind] == i]['rel_err']))

    slice_obj.values = np.array(slice_obj.values).T
    slice_obj.errors = np.array(slice_obj.errors).T

    return slice_obj


def create_plot(slice_obj, values, title, ax, lmin, lmax):
    """using slice obj and values create a 2d colormesh
    """
    plot = ax.pcolormesh(slice_obj.slice_i, slice_obj.slice_j, values,
                         norm=colors.LogNorm(vmin=lmin, vmax=lmax))
    plt.colorbar(plot, ax=ax)
    ax.set_title(title)
    ax.set_xlabel(slice_obj.i_lab)
    ax.set_ylabel(slice_obj.j_lab)
    ax.set_xlim(xmin=min(slice_obj.slice_i), xmax=max(slice_obj.slice_i))
    ax.set_ylim(ymin=min(slice_obj.slice_j), ymax=max(slice_obj.slice_j))
    return ax


def plot_slice(mesh, value, plane, lmin, lmax, err=False, fname=None, erg=None,
               time=None):
    """ plots a slice through the mesh check if err applied"""
    plt.clf()
    slice_obj = extract_slice(mesh, value, plane, erg, time)
    fig = plt.figure()
    ax = fig.add_subplot(211)
    title = plane + " Slice at " + str(value) + " of mesh " + str(mesh.idnum)
    ax = create_plot(slice_obj, slice_obj.values, title, ax, lmin, lmax)

    if err:
        title = title + " rel err"
        ax1 = fig.add_subplot(212)
        ax1 = create_plot(slice_obj, slice_obj.errors, title,  ax1, lmin, lmax)

    if fname:
        fig.savefig(fname)
        ntlogger.info("produced figure: %s", fname)
    else:
        plt.show()
    return slice_obj


# TODO:
def output_as_vtk():
    """ """
    ntlogger.debug("not ready yet")


def find_nearest_mid(value, mids):
    """ finds midpoint with shortest absoloute distance to the value """
    return mids[min(range(len(mids)), key=lambda i: abs(mids[i] - value))]


def convert_to_df(mesh):
    """ converts mesh.data in raw format to a pandas dataframe """
    # Define column mappings for different mesh types
    col_mappings = {
        "6col_e": ("Energy", "x", "y", "z", "value", "rel_err"),
        "6col_t": ("Time", "x", "y", "z", "value", "rel_err"),
        "5col": ("x", "y", "z", "value", "rel_err")
    }
    
    # Check if the column type is valid for future proofing
    if mesh.ctype not in col_mappings:
        raise ValueError(f"Unknown mesh type: {mesh.ctype}")

    # Create the DataFrame with the appropriate columns
    cols = col_mappings[mesh.ctype]
    data = pd.DataFrame(mesh.data, columns=cols)
    
    # convert to float
    data["x"] = pd.to_numeric(data["x"], downcast="float")
    data["y"] = pd.to_numeric(data["y"], downcast="float")
    data["z"] = pd.to_numeric(data["z"], downcast="float")
    data["value"] = pd.to_numeric(data["value"], downcast="float")
    data["rel_err"] = pd.to_numeric(data["rel_err"], downcast="float")

    if mesh.ctype == "6col_e":
        data["Energy"] = pd.to_numeric(data["Energy"], downcast="float")
    if mesh.ctype == "6col_t":
        data.drop(data[data.Time == "Total"].index, inplace=True)
        data.drop(data[data.Time == "0.000E+00"].index, inplace=True)
        data["Time"] = pd.to_numeric(data["Time"], downcast="float")

    return data


def extract_line(mesh, p1, p2, erg=None, time=None):
    """ currently support lines varying along a single axis
        p1 and p2 are tuples of the form (x,y,z) and
        describe two points on the line
        currently only either x,y or z can vary between the two points
    """

    data = mesh.data
    # find and filter the constant axis
    if p1[0] == p2[0]:
        x = p1[0]
        x = find_nearest_mid(x, mesh.x_mids)
        data = data[data["x"] == x]
    if p1[1] == p2[1]:
        y = p1[1]
        y = find_nearest_mid(y, mesh.y_mids)
        data = data[data["y"] == y]
    if p1[2] == p2[2]:
        z = p1[2]
        z = find_nearest_mid(z, mesh.z_mids)
        data = data[data["z"] == z]

    # filter for energy/time selection
    data = filter_energy_time(data, erg, time)
    result = data["value"]

    return result


def pick_point(x, y, z, mesh, erg=None, time=None):
    """ find the mesh value for the voxel that  point x, y, z is in and also
    matches time/energy parameter"""
    x = find_nearest_mid(x, mesh.x_mids)
    y = find_nearest_mid(y, mesh.y_mids)
    z = find_nearest_mid(z, mesh.z_mids)

    data = mesh.data
    data = data[data["x"] == x]
    data = data[data["y"] == y]
    data = data[data["z"] == z]

    data = filter_energy_time(data, erg, time)

    result = data["value"]

    return result


def calculate_upper_mesh_vals(mesh1):
    """ adds the absoute max value based on the relative error """
    maxvals = mesh1.data["value"] + (
        mesh1.data["value"] * mesh1.data["rel_err"])
    mesh1.data["max_vals"] = maxvals

    return mesh1


def calculate_lower_mesh_vals(mesh1):
    """ adds the absoute min value based on the relative error """
    minvals = mesh1.data["value"] - (
        mesh1.data["value"] * mesh1.data["rel_err"])
    mesh1.data["min_vals"] = minvals

    return mesh1


def add_mesh(mesh1, mesh2):
    """ checks if boundaries of two meshes are equal
        and adds their values and errors
    """
    # needs refactoring for different column number
    if ((mesh1.x_bounds != mesh2.x_bounds) or
            (mesh1.y_bounds != mesh2.y_bounds) or
            (mesh1.z_bounds != mesh2.z_bounds)):
        raise ValueError(f' position bounds not equal')
    if mesh1.ctype == "6col_e":
        col = "Energy"
        if (mesh1.e_bounds != mesh2.e_bounds):
            raise ValueError(f' energy bounds not equal')
    if mesh1.ctype == "6col_t":
        col = "Time"
        if (mesh1.t_bounds != mesh2.t_bounds):
            raise ValueError(f'time bounds are not equal')
    if mesh1.ctype != mesh2.ctype:
        raise ValueError(f'column types are not equal')

    else:
        new_val = mesh1.data['value'] + mesh2.data['value']
        new_err = np.sqrt((mesh1.data['rel_err'])**2 +
                          (mesh2.data['rel_err'])**2)

        new_mesh = meshtally()
        cols = (col, "x", "y", "z", "value", "rel_err")
        new_mesh.data = pd.DataFrame(columns=cols)
        new_mesh.ctype = mesh1.ctype
        new_mesh.x_bounds = mesh1.x_bounds
        new_mesh.y_bounds = mesh1.y_bounds
        new_mesh.z_bounds = mesh1.z_bounds

        new_mesh.x_mids = calc_mid_points(mesh1.x_bounds)
        new_mesh.y_mids = calc_mid_points(mesh1.y_bounds)
        new_mesh.z_mids = calc_mid_points(mesh1.z_bounds)
        new_mesh.data['value'] = new_val
        new_mesh.data['rel_err'] = new_err

        if mesh1.ctype == "6col_e":
            new_mesh.data['Energy'] = mesh1.data['Energy']
            new_mesh.e_bounds = mesh1.e_bounds
        elif mesh1.ctype == "6col_t":
            new_mesh.data["Time"] = mesh1.data["Time"]
            new_mesh.t_bounds = mesh1.t_bounds

        new_mesh.data['x'] = mesh1.data['x']
        new_mesh.data['y'] = mesh1.data['y']
        new_mesh.data['z'] = mesh1.data['z']

        return new_mesh


# TODO: need to deal with energy bins
def convert_to_3d_array(mesh):
    """ converts the mesh into 3d numpy array
        one array for the values and another for the rel errs
    """
    data = mesh.data
    data = np.array(data).astype(float)

    midx = mesh.x_mids
    midy = mesh.y_mids
    midz = mesh.z_mids

    vals = np.zeros((len(midx), len(midy), len(midz)))
    err_vals = np.zeros((len(midx), len(midy), len(midz)))

    for r in data:
        i, = np.where(midx == r[1])
        j, = np.where(midy == r[2])
        k, = np.where(midz == r[3])

        vals[i, j, k] = r[4]
        err_vals[i, j, k] = r[5]

    return vals, err_vals


def calc_mid_points(bounds):
    """ finds the mid points given a set of bounds """
    bounds = np.array(bounds).astype(float)

    mids = np.round((bounds[1:] + bounds[:-1]) * 0.5, 5)
    return mids.tolist()


def count_zeros(mesh):
    """ counts number of voxels with a zero value"""
    count = mesh.data["value"].value_counts()[0.0]
    return count


def find_mesh_tally_numbers(data):
    """ find the different meshes in the file, the tally number
        and the line it starts on"""
    tdict = {}
    for i, l in enumerate(data):
        if "Mesh Tally Number" in l:
            talid = int(l.split(" ")[-1])
            tdict[talid] = i
    return tdict


def find_next_mesh(tnum, tdict):
    """ finds the start location of the next numerical mesh tally"""
    keylist = sorted(tdict.keys())
    if tnum == keylist[-1]:
        return -1
    else:
        for i, v in enumerate(keylist):
            if v == tnum:
                return tdict[keylist[i + 1]]


def read_meshtally_file(path, mesh_num=None):
    """reads in a mesh file line by line into a meshtally object
    Args:
        path (str): path to file

    Returns:
        meshes (list of objects)
    """
    in_data = False
    select_mesh = False
    mesh = meshtally()
    mesh.ctype = "6col_e"
    meshes = []
    with open(path) as f:
        for i, line in enumerate(f):
            if in_data and " Mesh Tally Number" in line:
                if select_mesh:
                    return mesh
                else:
                    meshes.append(mesh)
                    mesh = meshtally()
                    in_data = False

            if "Mesh Tally Number" in line:
                tnum = int(line.split(" ")[-1])
                mesh.idnum = tnum
                if mesh.idnum == mesh_num:
                    select_mesh = True
            if in_data:
                data = " ".join(line.split())
                mesh.data.append(data.split())
            elif "X direction:" in line:
                line = " ".join(line.split())
                mesh.x_bounds = line.split(" ")[2:]
                mesh.x_mids = calc_mid_points(mesh.x_bounds)
            elif "Y direction:" in line:
                line = " ".join(line.split())
                mesh.y_bounds = line.split(" ")[2:]
                mesh.y_mids = calc_mid_points(mesh.y_bounds)
            elif "Z direction:" in line:
                line = " ".join(line.split())
                mesh.z_bounds = line.split(" ")[2:]
                mesh.z_mids = calc_mid_points(mesh.z_bounds)
            elif "Energy bin boundaries:" in line:
                line = " ".join(line.split())
                mesh.e_bounds = line.split(" ")[3:]
            elif "Time bin boundaries:" in line:
                line = " ".join(line.split())
                mesh.t_bounds = line.split(" ")[3:]
            elif ("Energy         X         Y         Z     Result" in line):
                in_data = True
            elif ("Time         X         Y         Z     Result" in line):
                in_data = True
                mesh.ctype = "6col_t"
            elif "X         Y         Z     Result" in line:
                in_data = True
                mesh.ctype = "5col"
            elif "mesh tally." in line:
                line = " ".join(line.split())
                mesh.ptype = line.split(' ')[0]
    meshes.append(mesh)

    for mesh in meshes:
        mesh.data = convert_to_df(mesh)
    return meshes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Meshtally ploting")
    parser.add_argument("input", help="path to the Meshtal file")
    args = parser.parse_args()

    meshes = read_meshtally_file(args.input)
