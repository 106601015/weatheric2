import numpy as np
import matplotlib.pyplot as plt
import os

# basic initialization
dt = 0.01/2
times = 5000*2

s = 10
r = 24.74
b = 2.6666667
f = 2.5

# return d(x/y/z)/dt
def get_dxdt(x, y, sita):
    return -1*s*x + s*y + f*np.cos(sita)
def get_dydt(x, y, z, sita):
    return -1*x*z + r*x - y + f*np.sin(sita)
def get_dzdt(x, y, z):
    return x*y - b*z

# return x_n+1
def forward_scheme(x_n, f_n, dt=0.01):
    return (x_n + f_n*dt)
def leap_frog_scheme(x_n_sub1, f_n, dt=0.01):
    return (x_n_sub1 + f_n*2*dt)
def backward_scheme(x_n, f_n_add1, dt=0.01):
    return (x_n + f_n_add1*dt)

# leap_frog_time_filter uses x_n+1 and xn and y_n-1 to derive y_n, then y_n replace x_n
def leap_frog_time_filter(x_n, x_n_add1, y_n_sub1):
    alpha = 0.06
    return x_n + alpha*(y_n_sub1 - 2*x_n + x_n_add1)

# plot
def plot_xyz_t(xyz, t, title):
    plt.plot(t, xyz, color='black', linewidth=1)
    plt.xlabel(title.split(' ')[3])
    plt.ylabel(title.split(' ')[1])
    plt.title(title)
    plt.savefig(os.path.join(os.getcwd(), 'output_image2', title))
    #plt.show()
    plt.close()
def plot_x_y_z(xyz1, xyz2, title):
    plt.plot(xyz1, xyz2, color='black', linewidth=1)
    plt.xlabel(title.split(' ')[3])
    plt.ylabel(title.split(' ')[1])
    plt.title(title)
    plt.savefig(os.path.join(os.getcwd(), 'output_image2', title))
    #plt.show()
    plt.close()

# valid scheme function
def plot_scheme_delta(array1, array2, text):
    over_num_list = []
    threshold_list = np.linspace(1.0, 0.0, 10+1)
    for threshold in threshold_list:
        num = 0
        for delta in array1-array2:
            if delta>threshold:num+=1
            if delta<-1*threshold:num+=1
        over_num_list.append(num)
    plt.xticks(threshold_list)
    plt.ylim(top=times)
    plt.xlabel('threshold')
    plt.ylabel('delta > threshold number')
    plt.plot(threshold_list, over_num_list)
    plt.title(text)
    plt.savefig(os.path.join(os.getcwd(), 'output_image2', text))
    #plt.show()
    plt.close()


if __name__ == '__main__':
    # check output_image2 exists
    if not os.path.exists(os.path.join(os.getcwd(), 'output_image2')):
        os.mkdir(os.path.join(os.getcwd(), 'output_image2'))

    # parameter initialization
    x_array, y_array, z_array, sita_array, t_array = np.full((times+1), -1.0), np.full((times+1), -1.0), np.full((times+1), -1.0), np.full((times+1), -1.0), np.full((times+1), -1.0)
    x_array[0], y_array[0], z_array[0], sita_array[0], t_array[0] = 0, 10, 0, 45*2*np.pi/360, 0
    for i in range(1, times+1):
        sita_array[i] = sita_array[i-1] + dt
        t_array[i] = t_array[i-1] + dt

    # copy x/y/z array for next three schemes, used to record and valid
    x_array_forward, x_array_leap_frog, x_array_backward = np.copy(x_array), np.copy(x_array), np.copy(x_array)
    y_array_forward, y_array_leap_frog, y_array_backward = np.copy(y_array), np.copy(y_array), np.copy(y_array)
    z_array_forward, z_array_leap_frog, z_array_backward = np.copy(z_array), np.copy(z_array), np.copy(z_array)

    # forward part(know x_n -> know f'(x) -> derive x_n+1, EZ)
    scheme = 'forward'
    for i in range(times):
        if i % 1000 == 0:print('{} epoch i='.format(scheme), i)
        # calculate f_n
        dxdt = get_dxdt(x_array_forward[i], y_array_forward[i], sita_array[i])
        dydt = get_dydt(x_array_forward[i], y_array_forward[i], z_array_forward[i], sita_array[i])
        dzdt = get_dzdt(x_array_forward[i], y_array_forward[i], z_array_forward[i])
        # calculate x_n+1 with x_n and f_n
        x_array_forward[i+1] = forward_scheme(x_array_forward[i], dxdt, dt=dt)
        y_array_forward[i+1] = forward_scheme(y_array_forward[i], dydt, dt=dt)
        z_array_forward[i+1] = forward_scheme(z_array_forward[i], dzdt, dt=dt)
    plot_xyz_t(x_array_forward, t_array, title='{} x vs t'.format(scheme))
    plot_xyz_t(y_array_forward, t_array, title='{} y vs t'.format(scheme))
    plot_xyz_t(z_array_forward, t_array, title='{} z vs t'.format(scheme))
    plot_x_y_z(x_array_forward, y_array_forward, title='{} x vs y'.format(scheme))
    plot_x_y_z(x_array_forward, z_array_forward, title='{} x vs z'.format(scheme))
    plot_x_y_z(z_array_forward, y_array_forward, title='{} z vs y'.format(scheme))
    print()

    # leap_frog part
    # if i=0: forward to know x_1
    # else:  1.using f'(x) and x_n-1 to derive x_n+1  2.using x_n+1 and xn and y_n-1 to derive y_n, then y_n replace x_n
    scheme = 'leap_frog'
    for i in range(times):
        if i % 1000 == 0:
            print('{} epoch i='.format(scheme), i)
        # forward to know x_1
        if i == 0:
            # calculate f_0
            dxdt = get_dxdt(x_array_leap_frog[i], y_array_leap_frog[i], sita_array[i])
            dydt = get_dydt(x_array_leap_frog[i], y_array_leap_frog[i], z_array_leap_frog[i], sita_array[i])
            dzdt = get_dzdt(x_array_leap_frog[i], y_array_leap_frog[i], z_array_leap_frog[i])
            # forward calculate x_1 with x0 and f0
            x_array_leap_frog[i+1] = forward_scheme(x_array_leap_frog[i], dxdt, dt=dt)
            y_array_leap_frog[i+1] = forward_scheme(y_array_leap_frog[i], dydt, dt=dt)
            z_array_leap_frog[i+1] = forward_scheme(z_array_leap_frog[i], dzdt, dt=dt)
            # calculate y_0
            yx, yy, yz = x_array_leap_frog[i], y_array_leap_frog[i], z_array_leap_frog[i]
            continue
        # 1.using f'(x) and x_n-1 to derive x_n+1
        # calculate f_n
        dxdt = get_dxdt(x_array_leap_frog[i], y_array_leap_frog[i], sita_array[i])
        dydt = get_dydt(x_array_leap_frog[i], y_array_leap_frog[i], z_array_leap_frog[i], sita_array[i])
        dzdt = get_dzdt(x_array_leap_frog[i], y_array_leap_frog[i], z_array_leap_frog[i])
        # leap_frog calculate x_n+1 with x_n-1 and f_n
        x_array_leap_frog[i+1] = leap_frog_scheme(x_array_leap_frog[i-1], dxdt, dt=dt)
        y_array_leap_frog[i+1] = leap_frog_scheme(y_array_leap_frog[i-1], dydt, dt=dt)
        z_array_leap_frog[i+1] = leap_frog_scheme(z_array_leap_frog[i-1], dzdt, dt=dt)

        # 2.using x_n+1 and xn and y_n-1 to derive y_n, then y_n replace x_n
        yx = leap_frog_time_filter(x_array_leap_frog[i], x_array_leap_frog[i+1], yx)
        x_array_leap_frog[i] = yx
        yy = leap_frog_time_filter(y_array_leap_frog[i], y_array_leap_frog[i+1], yy)
        y_array_leap_frog[i] = yy
        yz = leap_frog_time_filter(z_array_leap_frog[i], z_array_leap_frog[i+1], yz)
        z_array_leap_frog[i] = yz
        #if i % 100 == 0:
        #    print(i, 'yx', yx, yy, yz)

    plot_xyz_t(x_array_leap_frog, t_array, title='{} x vs t'.format(scheme))
    plot_xyz_t(y_array_leap_frog, t_array, title='{} y vs t'.format(scheme))
    plot_xyz_t(z_array_leap_frog, t_array, title='{} z vs t'.format(scheme))
    plot_x_y_z(x_array_leap_frog, y_array_leap_frog, title='{} x vs y'.format(scheme))
    plot_x_y_z(x_array_leap_frog, z_array_leap_frog, title='{} x vs z'.format(scheme))
    plot_x_y_z(z_array_leap_frog, y_array_leap_frog, title='{} z vs y'.format(scheme))
    print()

    # backward part(1.forward to know x_n+1(fake) and f'(n+1) 2.backward_scheme uses x_n and f'(n+1) to derive x_n+1)
    scheme = 'backward'
    for i in range(times):
        if i % 1000 == 0:print('{} epoch i='.format(scheme), i)
        # 1.forward to know x_n+1(fake) and f'(n+1)
        # calculate f_n
        dxdt = get_dxdt(x_array_backward[i], y_array_backward[i], sita_array[i])
        dydt = get_dydt(x_array_backward[i], y_array_backward[i], z_array_backward[i], sita_array[i])
        dzdt = get_dzdt(x_array_backward[i], y_array_backward[i], z_array_backward[i])
        # calculate x_n+1(fake) with x_n and f_n
        x_array_backward[i+1] = forward_scheme(x_array_backward[i], dxdt, dt=dt)
        y_array_backward[i+1] = forward_scheme(y_array_backward[i], dydt, dt=dt)
        z_array_backward[i+1] = forward_scheme(z_array_backward[i], dzdt, dt=dt)
        # calculate f_n+1
        dxdt = get_dxdt(x_array_backward[i+1], y_array_backward[i+1], sita_array[i+1])
        dydt = get_dydt(x_array_backward[i+1], y_array_backward[i+1], z_array_backward[i+1], sita_array[i+1])
        dzdt = get_dzdt(x_array_backward[i+1], y_array_backward[i+1], z_array_backward[i+1])
        # 2.backward_scheme uses x_n and f'(n+1) to derive x_n+1)
        x_array_backward[i+1] = backward_scheme(x_array_backward[i], dxdt, dt=dt)
        y_array_backward[i+1] = backward_scheme(y_array_backward[i], dydt, dt=dt)
        z_array_backward[i+1] = backward_scheme(z_array_backward[i], dzdt, dt=dt)
    plot_xyz_t(x_array_backward, t_array, title='{} x vs t'.format(scheme))
    plot_xyz_t(y_array_backward, t_array, title='{} y vs t'.format(scheme))
    plot_xyz_t(z_array_backward, t_array, title='{} z vs t'.format(scheme))
    plot_x_y_z(x_array_backward, y_array_backward, title='{} x vs y'.format(scheme))
    plot_x_y_z(x_array_backward, z_array_backward, title='{} x vs z'.format(scheme))
    plot_x_y_z(z_array_backward, y_array_backward, title='{} z vs y'.format(scheme))
    print()


    # scheme_delta check
    plot_scheme_delta(x_array_leap_frog, x_array_forward, text='leap_frog vs forward in x')
    plot_scheme_delta(y_array_leap_frog, y_array_forward, text='leap_frog vs forward in y')
    plot_scheme_delta(z_array_leap_frog, z_array_forward, text='leap_frog vs forward in z')

    plot_scheme_delta(x_array_backward, x_array_forward, text='backward vs forward in x')
    plot_scheme_delta(y_array_backward, y_array_forward, text='backward vs forward in y')
    plot_scheme_delta(z_array_backward, z_array_forward, text='backward vs forward in z')

    plot_scheme_delta(x_array_leap_frog, x_array_backward, text='leap_frog vs backward in x')
    plot_scheme_delta(y_array_leap_frog, y_array_backward, text='leap_frog vs backward in y')
    plot_scheme_delta(z_array_leap_frog, z_array_backward, text='leap_frog vs backward in z')
