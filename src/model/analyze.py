#!/usr/bin/env python3
# TODO make everything work with error checking (filenames, divide by zero, bla bla bla)
# TODO move getProperties() into the temperature search function (which hasn't been created)

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd


def solve(w, h, l, T_in, V_dot, q_chip, fluid_name):
    logging.info("Solving...")
    # calculate hydraulic diameter
    A = getArea(w, h, l)
    P = getPerimeter(w, h, l)
    D = 4 * A / P

    # estimate middle and outlet temperature
    fluid_table = get_fluid_table(fluid_name)

    PRINT_COUNTER = 0
    tol = 0.01
    T_mid = 0
    T_guess = T_in
    dT = 0.01

    while np.abs(T_guess - T_mid) > tol:
        PRINT_COUNTER += 1
        T_guess += dT
        Cp = np.interp(T_guess, fluid_table["temp_k"], fluid_table["cp"])
        rho = np.interp(T_guess, fluid_table["temp_k"], fluid_table["rho"])
        T_out = q_chip / (rho * V_dot * Cp) + T_in
        T_mid = (T_in + T_out) / 2
        if PRINT_COUNTER % 1000 == 0:
            logging.debug(
                f"""---------------------------------------------------------\n
                Iter: {PRINT_COUNTER}, T_guess: {T_guess:0.2f}, Err: {np.abs(T_guess - T_mid):0.2f}\n
                ---------------------------------------------------------\n"""
            )

    # calculate Reynold's number
    nu = np.interp(T_mid, fluid_table["temp_k"], fluid_table["nu_k"])
    Re = (V_dot * D) / (A * nu)

    # estimate Nusselt number
    Pr = np.interp(T_mid, fluid_table["temp_k"], fluid_table["pr"])
    Nu = getNusselt(Re, Pr)

    # calculate heat coefficient
    k = np.interp(T_mid, fluid_table["temp_k"], fluid_table["k"])
    h_coeff = Nu * k / D

    # calculate wall temperature
    T_wall = q_chip / (h_coeff * w * l) + T_mid

    return T_wall


def getArea(w, h, l):
    # NOTE assumes rectangular and constant across length
    return w * h


def get_fluid_table(fluid_name):
    current_path = Path(__file__).parent
    fluid_table_path = current_path / f"../../data/model/{fluid_name}_table.xlsx"
    fluid_table = pd.read_excel(fluid_table_path)
    return fluid_table


def getPerimeter(w, h, l):
    # NOTE assumes rectangular and constant across length
    return 2 * (w + h)


def getNusselt(Re, Pr):
    # NOTE assumes turbulence begins at inlet
    # laminar
    if Re < 2300:
        return 4.364
    # turbulent
    else:
        return 0.23 * Re**0.8 * Pr**0.4


def readInputfile(filename):
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
        w, h, l, T_in, V_dot, q_chip, fluid_name = readInputfile(pargs.filename)
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
    T_wall = solve(w, h, l, T_in, V_dot, q_chip, fluid_name)

    # POST PROCESSING ======================
    logging.info(f"Temperature of the Wall = {T_wall:.02f}K or {T_wall - 273.15:.02f}C")


if __name__ == "__main__":
    main()
