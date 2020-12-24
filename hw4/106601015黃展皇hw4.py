import numpy as np
import matplotlib.pyplot as plt
import os

# config: sample number and integration's h and power_spectral_endpoint
item_num = 730
gap = (2*np.pi)/item_num
power_spectral_endpoint = 244

# get pressure data and fix error data
def get_p():
    p = np.loadtxt('Ps.dat.txt')
    for i in range(item_num):
        if p[i] < 900.0:
            p[i] = (p[i+1]+p[i-1])/2
    return p
# get temp data and fix error data
def get_t():
    t = np.loadtxt('T.dat.txt')
    for i in range(item_num):
        if t[i] < 7.0:
            t[i] = (t[i+1]+t[i-1])/2
    return t

# trapezoid integral: delta A = (ui + ui+1)*gap/2
def trapezoid(inside_integral):
    integral_area = 0
    for i in range(item_num-1):
        integral_area += (inside_integral[i] + inside_integral[i+1])*gap/2
    #print('trapezoid area:', integral_area)
    return integral_area
#  simpson integral: delta A = (1/3)*gap*(ui + 4*ui+1 + ui+2)  (but i=1, 3, 5...)
def simpson(inside_integral):
    integral_area = 0
    for i in range(0, item_num-2, 2):
        integral_area += (1/3)*gap*(inside_integral[i] + 4*inside_integral[i+1] + inside_integral[i+2])
    #print('simpson area:', integral_area)
    return integral_area
# tick integral: delta A = (1/3)*gap*(1.0752*ui + 3.8496*ui+1 + 1.0752*ui+2)  (but i=1, 3, 5...)
def tick(inside_integral):
    integral_area = 0
    for i in range(0, item_num-2, 2):
        integral_area += (1/3)*gap*(1.0752*inside_integral[i] + 3.8496*inside_integral[i+1] + 1.0752*inside_integral[i+2])
    #print('tick area:', integral_area)
    return integral_area

# a routing for numerical integration
def numerical_integration_routing(inside_integral, way):
    if way == 'trapezoid':
        return trapezoid(inside_integral)
    elif way == 'simpson':
        return simpson(inside_integral)
    elif way == 'tick':
        return tick(inside_integral)
    else:print('numerical_integration way error!!!')

# calculate a0, an and bn
def calculate_a0(p_or_t, way):
    return numerical_integration_routing(p_or_t, way) / (2*np.pi)
def calculate_an(p_or_t, n, way):
    x = np.linspace(0, 2*np.pi, item_num)
    inside_integral = p_or_t*np.cos(n*x)
    return numerical_integration_routing(inside_integral, way) / np.pi
def calculate_bn(p_or_t, n, way):
    x = np.linspace(0, 2*np.pi, item_num)
    inside_integral = p_or_t*np.sin(n*x)
    return numerical_integration_routing(inside_integral, way) / np.pi

# calculate amplitude and phase and date
def calculate_amplitude(a, b):
    return (a**2 + b**2)**0.5
def calculate_phase(a, b):
    return np.arctan(-1*b/a)
def calculate_date(phase, n):
    x = -1*(phase/n)
    return x*365/(2*np.pi)

# plot f(x)(n=1=one year, 2=half year) and source data
def plot_f_of_x(p_or_t, way, text):
    print('plot_f_of_x', text, way)
    x = np.linspace(0, 2*np.pi, item_num)

    # calculate f_of_x_1 and f_of_x_2
    a1 = calculate_an(p_or_t=p_or_t, n=1, way=way)
    b1 = calculate_bn(p_or_t=p_or_t, n=1, way=way)
    f_of_x_1 = calculate_a0(p_or_t, way=way) + a1*np.cos(1*x) + b1*np.sin(1*x)
    a2 = calculate_an(p_or_t=p_or_t, n=2, way=way)
    b2 = calculate_bn(p_or_t=p_or_t, n=2, way=way)
    f_of_x_2 = calculate_a0(p_or_t, way=way) + a2*np.cos(2*x) + b2*np.sin(2*x)

    # plot and save
    plt.plot(p_or_t, color='black', linewidth=0.5)
    plt.plot(f_of_x_1, color='green', linewidth=2)
    plt.plot(f_of_x_2, color='yellow', linewidth=2)
    plt.title('{} {} rule'.format(text, way))

    if not os.path.exists('f_of_x'):
        os.mkdir('f_of_x')
    plt.savefig(os.path.join('f_of_x', 'f_of_x_{}_{}.png'.format(text, way)))
    plt.close()

# calculate and plot power_spectral([1:])
def plot_power_spectral(p_or_t, way, text):
    print('plot_power_spectral', text, way)
    # create and calculate power_spectral
    power_spectral = []
    for n in range(1, power_spectral_endpoint):
        a = calculate_an(p_or_t=p_or_t, n=n, way=way)
        b = calculate_bn(p_or_t=p_or_t, n=n, way=way)
        power_spectral.append(calculate_amplitude(a, b))
    power_spectral = power_spectral[1:]

    # plot and save
    plt.plot(power_spectral, color='black', linewidth=1)
    plt.title('{} {} power_spectral'.format(text, way))

    if not os.path.exists('power_spectral'):
        os.mkdir('power_spectral')
    plt.savefig(os.path.join('power_spectral', 'power_spectral_{}_{}.png'.format(text, way)))
    plt.close()

# return n, power_spectral, amplitude, phase, date for range search_deep=5
def get_max_power_spectral_info(p_or_t, way, text):
    print('get_max_power_spectral_info', text, way)
    search_deep = 5
    complete_power_spectral = []
    n, power_spectral, amplitude, phase, date = [], [], [], [], []

    # create and calculate complete_power_spectral
    for nn in range(1, power_spectral_endpoint):
        a = calculate_an(p_or_t=p_or_t, n=nn, way=way)
        b = calculate_bn(p_or_t=p_or_t, n=nn, way=way)
        complete_power_spectral.append(calculate_amplitude(a, b))
    n = sorted(range(len(complete_power_spectral)), key = lambda k : complete_power_spectral[k], reverse = True)[:search_deep]
    print('n: ', n)

    # calculate and append every list
    count = 0
    for i in n:
        power_spectral.append(complete_power_spectral[i])
        a = calculate_an(p_or_t=p_or_t, n=i, way=way)
        b = calculate_bn(p_or_t=p_or_t, n=i, way=way)
        amplitude.append(calculate_amplitude(a, b))
        phase.append(calculate_phase(a, b))
        date.append(calculate_date(phase[count], i))
        count += 1
    print('power_spectral: ', power_spectral)
    print('amplitude: ', amplitude)
    print('phase: ', phase)
    print('date: ', date)
    print()


if __name__ == "__main__":
    #integration_list = ['trapezoid', 'simpson', 'tick']
    print('main init')

    t = get_t()
    p = get_p()

    # plot_f_of_x
    plot_f_of_x(p_or_t=p, way='trapezoid', text='pressure')
    plot_f_of_x(p_or_t=t, way='trapezoid', text='temp')
    plot_f_of_x(p_or_t=p, way='simpson', text='pressure')
    plot_f_of_x(p_or_t=t, way='simpson', text='temp')
    plot_f_of_x(p_or_t=p, way='tick', text='pressure')
    plot_f_of_x(p_or_t=t, way='tick', text='temp')

    # plot_power_spectral
    plot_power_spectral(p_or_t=p, way='trapezoid', text='pressure')
    plot_power_spectral(p_or_t=t, way='trapezoid', text='temp')
    plot_power_spectral(p_or_t=p, way='simpson', text='pressure')
    plot_power_spectral(p_or_t=t, way='simpson', text='temp')
    plot_power_spectral(p_or_t=p, way='tick', text='pressure')
    plot_power_spectral(p_or_t=t, way='tick', text='temp')

    # get_max_power_spectral_info(n, power_spectral, amplitude, phase, date)
    get_max_power_spectral_info(p_or_t=p, way='trapezoid', text='pressure')
    get_max_power_spectral_info(p_or_t=t, way='trapezoid', text='temp')
    get_max_power_spectral_info(p_or_t=p, way='simpson', text='pressure')
    get_max_power_spectral_info(p_or_t=t, way='simpson', text='temp')
    get_max_power_spectral_info(p_or_t=p, way='tick', text='pressure')
    get_max_power_spectral_info(p_or_t=t, way='tick', text='temp')
