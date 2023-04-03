#!/usr/bin/env python3
# TODO make everything work with error checking (filenames, divide by zero, bla bla bla)
# TODO wtf are the units for q_chip

import argparse
import pandas as pd
import numpy as np

def solve(w, h, l, T_in, V_dot, q_chip, fluid_name):
    # calculate hydraulic diameter
    A = getArea(w, h, l)
    P = getPerimeter(w, h, l)
    D = 4 * A / P
    # estimate middle and outlet temperature
    tol     = 0.01
    T_mid   = 0
    T_guess = T_in
    dT      = 0.01
    while (np.abs(T_guess - T_mid) > tol):
        T_guess += dT
        Cp, k, Pr, nu, rho = getProperties(fluid_name, T_guess)
        T_out = q_chip / (rho * V_dot * Cp) + T_in
        T_mid = (T_in + T_out) / 2
    # calculate Reynold's number
    Re = (V_dot * D) / (A * nu)
    # estimate Nusselt number
    Nu = getNusselt(Re, Pr)
    # calculate heat coefficient
    h_coeff = Nu * k / D
    # calculate wall temperature
    T_wall = q_chip / (h_coeff * w * l) + T_mid
    return T_wall

def getArea(w, h, l):
    # NOTE assumes rectangular and constant across length
    return w * h

def getPerimeter(w, h, l):
    # NOTE assumes rectangular and constant across length
    return 2 * (w + h)

def getProperties(fluid_name, temp):
    # NOTE only supports air
    input_path = f"../../data/model/{fluid_name}_table.xlsx"
    df = pd.read_excel(input_path)
    if (temp in df["temp_k"].values):
        # do everything normally pull values from table
        Cp = df.loc[df["temp_k"] == temp, "cp"].values[0]
        k = df.loc[df["temp_k"] == temp, "k"].values[0]
        Pr = df.loc[df["temp_k"] == temp, "pr"].values[0]
        nu = df.loc[df["temp_k"] == temp, "nu_k"].values[0]
        rho = df.loc[df["temp_k"] == temp, "rho"].values[0]
    else:
        # interpolate
        Cp = np.interp(temp, df["temp_k"], df["cp"])
        k = np.interp(temp, df["temp_k"], df["k"])
        Pr = np.interp(temp, df["temp_k"], df["pr"])
        nu = np.interp(temp, df["temp_k"], df["nu_k"])
        rho = np.interp(temp, df["temp_k"], df["rho"])
    return Cp, k, Pr, nu, rho

def getNusselt(Re, Pr):
    # NOTE assumes turbulence begins at inlet
    # laminar
    if (Re < 2300):
        return 4.364
    # turbulent
    else: 
        return 0.23 * Re**0.8 * Pr**0.4

def readInputfile(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        w = float(lines[3].split()[-1])
        h = float(lines[4].split()[-1])
        l = float(lines[5].split()[-1])
        T_in = float(lines[6].split()[-1])
        V_dot = float(lines[7].split()[-1])
        q_chip = float(lines[8].split()[-1])
        fluid_name = lines[9].split()[-1]
    return w, h, l, T_in, V_dot, q_chip, fluid_name

if __name__ == "__main__":
    # ARG PARSING ==========================
    parser = argparse.ArgumentParser(
        description="Team Cooliest's ~ proprietary ~ model."
    )
    subparser = parser.add_subparsers(dest="subparser")