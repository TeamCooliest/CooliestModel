# first line: 176
def calculate_parameters(w, h, l_in, l_chip, l_out, t_in, v_dot, q, fluid_name):
    """Creates and combines the segments of the channel to calculate all
    important parameters.

    Inputs:
        w (float): Width of duct (bottom of inlet/outlet) (m)
        h (float): Height of duct (sides of inlet/outlet, not heated surface) (m)
        l_in (float): Length of inlet channel (runs along heated surface) (m)
        l_chip (float): Length of chip channel (runs along heated surface) (m)
        l_out (float): Length of outlet channel (runs along heated surface) (m)
        t_in (float): Temperature of inlet fluid (K)
        t_dot (float): Volume flow rate of inlet fluid(m^3/s)
        q (float): Heat applied to bottom wall of chip segment (W)
        fluid_name (string): Name of fluid

    Parameters:
        t_chip (float): Temperature of heated surface (K)
        t_mid_chip (float): Temperature in the middle of the heated channel segment (K)
        t_out (float): Temperature exiting the channel (K)
    """
    # inlet segment
    q_in = 0.10 * q * l_in / (l_in + l_out)
    inlet = Segment(w, h, l_in, t_in, v_dot, q_in, fluid_name)
    inlet.calculate_wall_temp()

    # chip segment
    q_chip = 0.90 * q
    chip = Segment(w, h, l_chip, inlet.t_out, v_dot, q_chip, fluid_name)
    chip.calculate_wall_temp()

    # outlet segment
    q_out = 0.10 * q * l_out / (l_in + l_out)
    outlet = Segment(w, h, l_out, chip.t_out, v_dot, q_out, fluid_name)
    outlet.calculate_wall_temp()

    # summary
    t_chip = chip.t_wall
    t_mid_chip = chip.t_mid
    t_out = outlet.t_out

    return t_chip, t_mid_chip, t_out
