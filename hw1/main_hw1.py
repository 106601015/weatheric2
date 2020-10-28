import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import math
import sys
print(sys.prefix) # show what virtual env I am in
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# read binary data, analyze to 49x*25y*5(1000 850 700 500 300)*4(H U V T) = 24500 np.array, return wanted plane data
def read_bindata_return_wanted(hw1_root_path, filename, pressure, parameter):
    all_data = np.fromfile(hw1_root_path+filename, dtype='<f4', count=-1, sep='')
    init_lndex = 5*x_num*y_num*parameter_list.index(parameter) + x_num*y_num*pressure_list.index(pressure)
    return all_data[init_lndex:init_lndex+x_num*y_num]

# Input x y and output the corresponding latitude and longitude coordinates
def xy_to_lonlat(x, y):
    return 90+x*delta, 15+y*delta
# Input y and output the corresponding latitude coordinates
def y_to_lat(y):
    return 15+y*delta

# Input pre, post, and d and output interpolation differential.
def median_interpolation(front, behind, d):
    return (behind-front)/(2*d)
# Input pre, here, and d and output the pre-interpolated differential.
def front_interpolation(front, here, d):
    return (here-front)/d
# Input here value and post value and output post-interpolation differential.
def behind_interpolation(here, behind, d):
    return (behind-here)/d

# Enter flat data, draw on a map and save it.
def plot_in_map(plane_data, title, pressure, var_name):
    # Create x, y grid points
    x = np.arange(lon_lower, lon_upper+delta, delta)
    y = np.arange(lat_lower, lat_upper+delta, delta)
    X, Y = np.meshgrid(x, y)

    # Set map parameters: projection, coastline resolution, grid, off right and above longitude and latitude, format latitude and longitude.
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines(resolution='50m', alpha=0.7)
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, color='gray', alpha=0.5)
    gl.xlocator = mticker.FixedLocator(np.arange(90, 180+10, 10))
    gl.ylocator = mticker.FixedLocator(np.arange(15, 60+5, 5))
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    # plot
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['figure.dpi'] = 300
    plt.title('{} Field'.format(title), fontsize='large')
    plt.contourf(X, Y, plane_data, cmap='jet') #rainbow gist_rainbow
    plt.colorbar()
    plt.savefig(hw1_root_path+title+'.png', dpi=600)
    plt.close()

# Input u, v, t field and pressure layer to create a horizontal temperature advection field and plot.
def plot_horizontal_temperature_advection(u, v, t, pressure):
    # HTA is what we want
    HTA = np.zeros([y_num, x_num])
    dy = 6378000*delta*math.pi/180

    for y in range(y_num):
        # renew dx per y
        dx=dy*math.cos(y_to_lat(y)*(2*math.pi/360))
        for x in range(x_num):
            # default try: median_interpolation
            try:
                dtdy = median_interpolation(t[y-1, x], t[y+1, x], dy)
                dtdx = median_interpolation(t[y, x-1], t[y, x+1], dx)
            except IndexError:
                pass
            # edge conditions
            if y == 0:dtdy = behind_interpolation(t[y, x], t[y+1, x], dy)
            if y == y_num-1:dtdy = front_interpolation(t[y-1, x], t[y, x], dy)
            if x == 0:dtdx = behind_interpolation(t[y, x], t[y, x+1], dx)
            if x == x_num-1:dtdx = front_interpolation(t[y, x-1], t[y, x], dx)

            HTA[y, x] = -(u[y, x]*dtdx)-(v[y, x]*dtdy)
    plot_in_map(HTA, '{}hPa Horizontal Temperature Advection'.format(pressure), pressure, 'HTA')

# Input u, v field and pressure layer to create a divergence field and plot.
def plot_divergence(u, v, pressure):
    divergence = np.zeros([y_num, x_num])
    dy = 6378000*delta*math.pi/180

    for y in range(y_num):
        dx=dy*math.cos(y_to_lat(y)*(2*math.pi/360))
        for x in range(x_num):
            # default try: median_interpolation
            try:
                dvdy = median_interpolation(v[y-1, x], v[y+1, x], dy)
                dudx = median_interpolation(u[y, x-1], u[y, x+1], dx)
            except IndexError:
                pass
            # edge conditions
            if y == 0:dvdy = behind_interpolation(v[y, x], v[y+1, x], dy)
            if y == y_num-1:dvdy = front_interpolation(v[y-1, x], v[y, x], dy)
            if x == 0:dudx = behind_interpolation(u[y, x], u[y, x+1], dx)
            if x == x_num-1:dudx = front_interpolation(u[y, x-1], u[y, x], dx)

            divergence[y, x] = dudx + dvdy
    plot_in_map(divergence, '{}hPa divergence'.format(pressure), pressure, 'divergence')

# Input u, v field and pressure layer to create a relative vorticity field and plot.
def plot_relative_vorticity(u, v, pressure):
    RV = np.zeros([y_num, x_num])
    dy = 6378000*delta*math.pi/180

    for y in range(y_num):
        dx=dy*math.cos(y_to_lat(y)*(2*math.pi/360))
        for x in range(x_num):
            # default try: median_interpolation
            try:
                dudy = median_interpolation(u[y-1, x], u[y+1, x], dy)
                dvdx = median_interpolation(v[y, x-1], v[y, x+1], dx)
            except IndexError:
                pass
            # edge conditions
            if y == 0:dudy = behind_interpolation(u[y, x], u[y+1, x], dy)
            if y == y_num-1:dudy = front_interpolation(u[y-1, x], u[y, x], dy)
            if x == 0:dvdx = behind_interpolation(v[y, x], v[y, x+1], dx)
            if x == x_num-1:dvdx = front_interpolation(v[y, x-1], v[y, x], dx)

            RV[y, x] = dvdx - dudy
    plot_in_map(RV, '{}hPa Relative Vorticity'.format(pressure), pressure, 'RV')

# Input u, v field and pressure layer to create a relative vorticity field and plot.
def plot_absolute_vorticity_advection(u, v, pressure):
    RV_f = np.zeros([y_num, x_num])
    AVA = np.zeros([y_num, x_num])
    dy = 6378000*delta*math.pi/180

    for y in range(y_num):
        dx=dy*math.cos(y_to_lat(y)*(2*math.pi/360))
        f = 2*(2*math.pi/(24*60*60))*math.sin(y_to_lat(y)*(2*math.pi/360))
        for x in range(x_num):
            # default try: median_interpolation
            try:
                dudy = median_interpolation(u[y-1, x], u[y+1, x], dy)
                dvdx = median_interpolation(v[y, x-1], v[y, x+1], dx)
            except IndexError:
                pass
            # edge conditions
            if y == 0:dudy = behind_interpolation(u[y, x], u[y+1, x], dy)
            if y == y_num-1:dudy = front_interpolation(u[y-1, x], u[y, x], dy)
            if x == 0:dvdx = behind_interpolation(v[y, x], v[y, x+1], dx)
            if x == x_num-1:dvdx = front_interpolation(v[y, x-1], v[y, x], dx)

            RV_f[y, x] = (dvdx - dudy) + f

    for y in range(y_num):
        dx=dy*math.cos(y_to_lat(y)*(2*math.pi/360))
        for x in range(x_num):
            # default try: median_interpolation
            try:
                dRV_fdy = median_interpolation(RV_f[y-1, x], RV_f[y+1, x], dy)
                dRV_fdx = median_interpolation(RV_f[y, x-1], RV_f[y, x+1], dx)
            except IndexError:
                pass
            # edge conditions
            if y == 0:dRV_fdy = behind_interpolation(RV_f[y, x], RV_f[y+1, x], dy)
            if y == y_num-1:dRV_fdy = front_interpolation(RV_f[y-1, x], RV_f[y, x], dy)
            if x == 0:dRV_fdx = behind_interpolation(RV_f[y, x], RV_f[y, x+1], dx)
            if x == x_num-1:dRV_fdx = front_interpolation(RV_f[y, x-1], RV_f[y, x], dx)

            AVA[y, x] = -u[y, x]*dRV_fdx - v[y, x]*dRV_fdy

    plot_in_map(AVA, '{}hPa Absolute Vorticity Advection'.format(pressure), pressure, 'AVA')


if __name__ == "__main__":
    # Definition of basic parameters
    print('init!!')
    names = locals()
    hw1_root_path = os.path.join(os.path.abspath('.'), 'hw1')+'\\'
    pressure_list = ['1000', '850', '700', '500', '300']
    parameter_list = ['H', 'U', 'V', 'T']
    x_num, y_num = 49, 25
    lon_upper, lon_lower, lat_upper, lat_lower = 180, 90, 60, 15
    delta = 1.875

    # Load data + definate parameters
    for parameter in parameter_list:
        for pressure in pressure_list:
            plane_data_name = parameter + pressure
            plane_data = np.reshape(read_bindata_return_wanted(hw1_root_path, filename='output.bin', pressure=pressure, parameter=parameter), (y_num, x_num))
            names[plane_data_name] = plane_data
            print(parameter+pressure, 'load ok')

    plot_horizontal_temperature_advection(U1000, V1000, T1000, '1000')
    plot_horizontal_temperature_advection(U850, V850, T850, '850')
    plot_horizontal_temperature_advection(U700, V700, T700, '700')
    plot_horizontal_temperature_advection(U500, V500, T500, '500')
    plot_horizontal_temperature_advection(U300, V300, T300, '300')

    plot_divergence(U1000, V1000, '1000')
    plot_divergence(U850, V850, '850')
    plot_divergence(U700, V700, '700')
    plot_divergence(U500, V500, '500')
    plot_divergence(U300, V300, '300')

    plot_relative_vorticity(U1000, V1000, '1000')
    plot_relative_vorticity(U850, V850, '850')
    plot_relative_vorticity(U700, V700, '700')
    plot_relative_vorticity(U500, V500, '500')
    plot_relative_vorticity(U300, V300, '300')

    plot_absolute_vorticity_advection(U1000, V1000, '1000')
    plot_absolute_vorticity_advection(U850, V850, '850')
    plot_absolute_vorticity_advection(U700, V700, '700')
    plot_absolute_vorticity_advection(U500, V500, '500')
    plot_absolute_vorticity_advection(U300, V300, '300')