import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import math
import sys
print(sys.prefix) # show what virtual env I am in

# read binary data, analyze to 49x*25y*5(1000 850 700 500 300)*4(H U V T) = 24500 np.array, return wanted plane data
def read_bindata_return_wanted(hw1_root_path, filename, pressure, parameter):
    all_data = np.fromfile(hw1_root_path+filename, dtype='<f4', count=-1, sep='')
    init_lndex = 5*x_num*y_num*parameter_list.index(parameter) + x_num*y_num*pressure_list.index(pressure)
    return all_data[init_lndex:init_lndex+x_num*y_num]
# Input y and output the corresponding latitude coordinates
def y_to_lat(y):
    return lat_lower+y*delta
def lon_to_x(lon):
    return int((lon-lon_lower)/delta)

# Input pre, post, and d and output interpolation differential.
def median_interpolation(front, behind, d):
    return (behind-front)/(2*d)
# Input pre, here, and d and output the pre-interpolated differential.
def front_interpolation(front, here, d):
    return (here-front)/d
# Input here value and post value and output post-interpolation differential.
def behind_interpolation(here, behind, d):
    return (behind-here)/d
# return 120E 15~60N divergence
def get_120E_divergence(u, v):
    divergence = np.zeros([y_num])
    dy = 6378000*delta*math.pi/180

    for y in range(y_num):
        dx=dy*math.cos(y_to_lat(y)*(2*math.pi/360))
        x = lon_to_x(120)
        dudx = median_interpolation(u[y, x-1], u[y, x+1], dx)
        print(u[y, x-1], u[y, x+1], dx, dy)
        # default try: median_interpolation
        try:
            dvdy = median_interpolation(v[y-1, x], v[y+1, x], dy)
        except IndexError:
            pass
        # y edge conditions
        if y == 0:dvdy = behind_interpolation(v[y, x], v[y+1, x], dy)
        if y == y_num-1:dvdy = front_interpolation(v[y-1, x], v[y, x], dy)

        divergence[y] = dudx + dvdy
    print(divergence)
    return divergence

# plot profile
def plot_profile(w):
    print('plot init')
    print(w_pressure_list)
    y = np.arange(lat_lower, lat_upper+delta, delta)
    z = np.array(w_pressure_list)
    Y, Z = np.meshgrid(y, z)

    # log y axit, set yticks
    gap = np.max(w)/10
    y_clabel_list = gap * np.arange(int(np.min(w)/gap), int(np.max(w)/gap)+1)
    print(y_clabel_list)
    cs = plt.contour(Y, Z, w, cmap='jet', levels=y_clabel_list)
    plt.clabel(cs)
    plt.yscale('log')
    plt.yticks(np.linspace(100, 1000, 10), np.linspace(100, 1000, 10).astype('int32'))
    xlabel = np.linspace(15, 60, 10)
    plt.xticks(xlabel, ['{}N'.format(str(int(x))) for x in xlabel])
    plt.ylim(w_pressure_list[0], w_pressure_list[5])
    gl = plt.grid(color='gray', alpha=0.3, linestyle='--')
    plt.title('Vertical velocity (120E)')
    plt.show()

if __name__ == "__main__":
    # Definition of basic parameters
    print('init!!')
    names = locals()
    hw2_root_path = os.path.join(os.path.abspath('.'), 'hw2')+'\\'
    pressure_list = ['1000', '850', '700', '500', '300']
    parameter_list = ['H', 'U', 'V', 'T']
    x_num, y_num = 49, 25
    lon_upper, lon_lower, lat_upper, lat_lower = 180, 90, 60, 15
    delta = 1.875

    # Load u, v data + definate parameters
    for parameter in parameter_list:
        if parameter == 'H' or parameter == 'T':continue
        for pressure in pressure_list:
            plane_data_name = parameter + pressure
            plane_data = np.reshape(read_bindata_return_wanted(hw2_root_path, filename='output.bin', pressure=pressure, parameter=parameter), (y_num, x_num))
            names[plane_data_name] = plane_data
            print(parameter+pressure, 'load ok')

    # init w0~5 as 0 array, and get every layers divergence
    w_pressure_list = [1010, 925, 775, 600, 400, 100]
    for i in range(len(w_pressure_list)):
        w_name = 'w{}'.format(str(i))
        names[w_name] = np.zeros(y_num)
    for pressure in pressure_list:
        names['D{}'.format(pressure)] = get_120E_divergence(names['U{}'.format(pressure)], names['V{}'.format(pressure)])

    # using old w to culculate every layers w
    for i in range(len(w_pressure_list)):
        if i == 0:w = np.copy(np.zeros(y_num))
        else:
            w += names['D{}'.format(pressure_list[i-1])] * (w_pressure_list[i-1]-w_pressure_list[i])
            names['w{}'.format(str(i))] = np.copy(w)

    # using not ok w to fix D
    eps = (w5-w0)/(w_pressure_list[0]-w_pressure_list[5])
    for pressure in pressure_list:
        names['D{}'.format(pressure)] = names['D{}'.format(pressure)] - eps

    # using fixed w to culculate every layers w
    for i in range(len(w_pressure_list)):
        if i == 0:w = np.copy(np.zeros(y_num))
        else:
            w += names['D{}'.format(pressure_list[i-1])] * (w_pressure_list[i-1]-w_pressure_list[i])
            names['w{}'.format(str(i))] = np.copy(w)

    w = np.vstack([w0, w1, w2, w3, w4, w5])
    print('w.shape', w.shape)

    plot_profile(w)