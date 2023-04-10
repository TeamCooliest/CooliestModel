#!/usr/bin/env python3
# TODO make everything work with error checking (filenames, divide by zero, bla bla bla)

import argparse
import logging
from pathlib import Path

import cantera as ct
import numpy as np
import pandas as pd


def calculate_wall_temp(w, h, l, t_in, v_dot, q_chip, fluid_name="air"):
    """Calculates the temperature of the bottom wall in a rectangular duct,
    where the bottom wall is producing a constant heat flux.

    Args:
        w (float): Width of duct (bottom of inlet/outlet) (m)
        h (float): Height of duct (sides of inlet/outlet, not heated surface) (m)
        l (float): Length of channel (runs along heated surface) (m)
        t_in (float): Temperature of inlet fluid (K)
        t_dot (float): Volume flow rate of inlet fluid(m^3/s)
        q_chip (float): Heat applied to bottom wall (W)
        fluid_name (string): Name of fluid

    Returns:
        float: Temperature of heated surface (K)
    """
    logging.info("Solving...")
    logging.debug(f"Input parameters: {locals()}")
    # calculate hydraulic diameter
    area = get_area(w, h, l)
    perimeter = get_perimeter(w, h, l)
    diameter_h = 4 * area / perimeter

    print_counter = 0
    tol = 0.01
    t_mid = 0
    t_guess = t_in
    dt = 0.01

    while np.abs(t_guess - t_mid) > tol:
        # TODO we need a better searching algorithm
        print_counter += 1
        t_guess += dt

        cp, k, prandtl, nu_k, rho = get_properties(fluid_name, t_guess)

        t_out = q_chip / (rho * v_dot * cp) + t_in
        t_mid = (t_in + t_out) / 2

        if print_counter % 1000 == 0:
            logging.debug(
                f"""---------------------------------------------------------\n
                Iter: {print_counter}, T_guess: {t_guess:0.2f}, Err: {np.abs(t_guess - t_mid):0.2f}\n
                ---------------------------------------------------------\n"""
            )

    # calculate Reynold's number
    reynolds = v_dot * diameter_h / (area * nu_k)

    # estimate Nusselt number
    nusselt = get_nusselt(reynolds, prandtl)

    # calculate heat coefficient
    h_coeff = nusselt * k / diameter_h

    # calculate wall temperature
    T_wall = q_chip / (h_coeff * w * l) + t_mid

    logging.debug(f"Wall temperature: {T_wall:0.2f} K")
    return T_wall


def get_properties(fluid_name, temp, pressure=101_325):
    """Description:
    This function takes in the name of a fluid, temperature, and pressure (default value = 101325 Pa)
    and returns the specific heat capacity, thermal conductivity, Prandtl number, kinematic viscosity,
    and density of the fluid at the given temperature and pressure.

    Parameters:
    - fluid_name (str): The name of the fluid as a string.
    - temp (float): The temperature of the fluid in Kelvin.
    - pressure (float, optional): The pressure of the fluid in Pascals. Default value is 101325 Pa.

    Returns:
    - cp (float): The specific heat capacity of the fluid in J/(kg*K).
    - k (float): The thermal conductivity of the fluid in W/(m*K).
    - pr (float): The Prandtl number of the fluid.
    - nu_k (float): The kinematic viscosity of the fluid in m^2/s.
    - rho (float): The density of the fluid in kg/m^3.

    NOTE: For `fluid_name="air"`, values may be different due to different definitions of
    an air mixture.
    """
    if fluid_name == "air":
        fluid = ct.Solution(f"{fluid_name}.yaml")
        fluid.TP = temp, pressure
        cp = fluid.cp_mass
        rho = fluid.density
        k = fluid.thermal_conductivity
        nu_k = fluid.viscosity / fluid.density
        pr = (nu_k * cp) / k

    else:
        input_path = f"../../data/{fluid_name}_table.xlsx"
        df = pd.read_excel(input_path)
        if temp in df["temp_k"].values:
            # do everything normally pull values from table
            cp = df.loc[df["temp_k"] == temp, "cp"].values[0]
            k = df.loc[df["temp_k"] == temp, "k"].values[0]
            pr = df.loc[df["temp_k"] == temp, "pr"].values[0]
            nu_k = df.loc[df["temp_k"] == temp, "nu_k"].values[0]
            rho = df.loc[df["temp_k"] == temp, "rho"].values[0]

        else:
            cp = np.interp(temp, df["temp_k"], df["cp"])
            k = np.interp(temp, df["temp_k"], df["k"])
            pr = np.interp(temp, df["temp_k"], df["pr"])
            nu_k = np.interp(temp, df["temp_k"], df["nu_k"])
            rho = np.interp(temp, df["temp_k"], df["rho"])

    return cp, k, pr, nu_k, rho


def get_area(w, h, l):
    # NOTE assumes rectangular and constant across length
    return w * h


def get_fluid_table(fluid_name):
    current_path = Path(__file__).parent
    fluid_table_path = current_path / f"../../data/model/{fluid_name}_table.xlsx"
    fluid_table = pd.read_excel(fluid_table_path)
    return fluid_table


def get_perimeter(w, h, l):
    # NOTE assumes rectangular and constant across length
    return 2 * (w + h)


def get_nusselt(Re, Pr):
    # NOTE assumes turbulence begins at inlet
    # laminar
    if Re < 2300:
        return 4.364
    # turbulent
    else:
<<<<<<< HEAD
        return 0.23 * Re ** 0.8 * Pr ** 0.4
=======
        return 0.23 * Re**0.8 * Pr**0.4
>>>>>>> 31aefeeabc5ace6f5f209047ee860cbc2477fd56


def read_input_file(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
        w = float(lines[3].split()[-1])
        h = float(lines[4].split()[-1])
        l = float(lines[5].split()[-1])
        T_in = float(lines[6].split()[-1])
        V_dot = float(lines[7].split()[-1])
        q_chip = float(lines[8].split()[-1])
        fluid_name = lines[9].split()[-1]
    return w, h, l, T_in, V_dot, q_chip, fluid_name


def main():
    # ARG PARSING ==========================
    parser = argparse.ArgumentParser(
        description="Team Cooliest's ~ proprietary ~ model."
    )

    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode.")

    subparser = parser.add_subparsers(dest="subparser")

    # Input File ---------------------------
    inputfile = subparser.add_parser("inputfile")
    inputfile.add_argument(
        "-f", "--filename", type=str, required=True, help="Name of the input file."
    )

    # Arguments ----------------------------
    # help strings include SI units
    args = subparser.add_parser("args")
    args.add_argument(
        "--width", type=float, required=True, help="Width of the channel (m)."
    )
    args.add_argument(
        "--height", type=float, required=True, help="Height of the channel (m)."
    )
    args.add_argument(
        "--length", type=float, required=True, help="Length of the channel (m)."
    )
    args.add_argument("--Tin", type=float, required=True, help="Inlet temperature (K).")
    args.add_argument(
        "--Vdot", type=float, required=True, help="Volumetric flow rate (m^3/s)."
    )
    args.add_argument(
        "--qChip", type=float, required=True, help="Heat generated by the chip (?)."
    )
    args.add_argument(
        "--fluid",
        type=float,
        required=True,
        help="The fluid flowing through the channel (-).",
    )

    pargs = parser.parse_args()
    if pargs.subparser == "inputfile":
        w, h, l, T_in, V_dot, q_chip, fluid_name = read_input_file(pargs.filename)
    elif pargs.subparser == "args":
        w = pargs.width
        h = pargs.height
        l = pargs.length
        T_in = pargs.Tin
        V_dot = pargs.Vdot
        q_chip = pargs.qChip
        fluid_name = pargs.fluid

    if pargs.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # SOLVE ================================
    T_wall = calculate_wall_temp(w, h, l, T_in, V_dot, q_chip, fluid_name)

    # POST PROCESSING ======================
    logging.info(f"Temperature of the Wall = {T_wall:.02f}K or {T_wall - 273.15:.02f}C")


if __name__ == "__main__":
    main()
