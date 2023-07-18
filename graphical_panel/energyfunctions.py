import numpy as np


""" parameters """
global mb, mc, l
mb = 0.066  # kg
mc = 0.32    # kg
g= 9.8
l_id1 = 0.1     # cm (this is dependent on the curvature level (ID))
l_id2 = 0.2    # measure again

"""PSE energy of ball 1D"""
def pseudo_energy_ball_1d(theta, a, l):
    # pse_ball = mb * a * l * np.sin(theta) + mb * a * l if a >= 0 else mb * a * l * np.sin(theta) - mb * a * l
    pse_ball = mb * a * l * np.sin(theta) + mb * abs(a) * l
    return pse_ball


""" Total energy of ball 1D"""
def total_energy_1d(theta, omega, a, l):
    # KE + PE + PSE
    KE_ball = 0.5*mb*np.power((l*omega),2)
    PE_ball = mb*g*l*(1-np.cos(theta))
    pse_ball = pseudo_energy_ball_1d(theta, a, l)
    te_ball = KE_ball + PE_ball + pse_ball
    return te_ball

""" Escape energy 1D"""
def escape_energy_1d(theta_esc, a, l):
    e_esc = mb * g * l * (1 - np.cos(theta_esc)) + mb * abs(a) * l * np.sin(theta_esc) + mb * abs(a) * l  # escape energy
    return e_esc

""" Energy Margin 1D """
def energy_margin_1d(theta, omega, theta_esc, a, l):
    e_esc= escape_energy_1d(theta_esc, a, l)
    te_ball = total_energy_1d(theta, omega, a, l)
    em = (e_esc - te_ball) / e_esc;
    return em


"""PSE energy of ball 2D"""
def pseudo_energy_ball_2d(theta1, theta2,  ax, ay,  l):
    # pse_ball = mb * a * l * np.sin(theta) + mb * a * l if a >= 0 else mb * a * l * np.sin(theta) - mb * a * l
    # pse_ball = mb * a * l * np.sin(theta) + mb * abs(a) * l
    pse_ball = (mb * ax * l * np.sin(theta1)*np.cos(theta2) + mb * ay * l * np.sin(theta1)*np.sin(theta2) +
                mb * abs(ax) * l  + mb * abs(ay) *l)  # re-define energy reference
    return pse_ball

""" PE 1D, 2D """
def PE(theta1, l):
    PE_ball = mb*g*l*(1-np.cos(theta1))
    return PE_ball


""" KE_2D can't use cos theat2 because it wraps around 360 and make a sharp jump: bad for omega.
    Use magnitude of velocity calculated from posision instead. 
"""

def KE_2D(theta1, theta2, v, ax, ay, l):
    KE_ball = 0.5*mb*(np.power(v,2))
    return KE_ball

""" Total energy of ball 2D
        theta1: angle from vertical -z
        theta2: angle from horizontal +x."""
def total_energy_2d(theta1, theta2, v, ax, ay, l):
    # KE + PE + PSE
    # KE_ball = 0 #0.5*mb*np.power(l,2)*(np.power(omega1,2)+np.power(omega2,2)) # # the same as 1D when omega is root mean square of the two omegas
    KE_ball = KE_2D(theta1, theta2, v, ax, ay, l)
    PE_ball = PE(theta1, l)     # the same as 1D
    pse_ball = pseudo_energy_ball_2d(theta1, theta2, ax, ay,  l) ### tricky
    te_ball = KE_ball + PE_ball + pse_ball
    return te_ball

""" Escape energy 2D
    marginal condition when KE = 0 """
def escape_energy_2d(theta_esc, theta2,  ax, ay, l):
    # e_esc = mb * g * l * (1 - np.cos(theta_esc)) + mb * abs(a) * l * np.sin(theta_esc) + mb * abs(a) * l  # escape energy
    e_esc =  PE(theta_esc, l) + pseudo_energy_ball_2d(theta_esc, theta2, ax, ay, l)  # escape energy
    return e_esc

""" Energy Margin 2D """
def energy_margin_2d(theta1, theta2, v, theta_esc, ax, ay, l):
    # a = np.sqrt(np.power(ax,2)+np.power(ay,2))
    e_esc= escape_energy_2d(theta_esc, theta2,  ax, ay, l)
    te_ball = total_energy_2d(theta1, theta2, v, ax, ay, l)
    em = (e_esc - te_ball) / e_esc;
    return em