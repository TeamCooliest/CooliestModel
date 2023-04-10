## multiply cp by 1000
import pandas as pd
import numpy as np


def get_fluid_properties_janaf(fluid_name, temp, pressure):
    """Description:
    This function takes in the name of a fluid, temperature, and pressure (default value = 101325 Pa)
    and returns the specific heat capacity, thermal conductivity, Prandtl number, kinematic viscosity,
    and density of the fluid at the given temperature and pressure from a table with the values acquired from JANAF

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


    """

    filepath = f"../../data/model{fluid_name}.csv"
    table = pd.read_csv(filepath)

    if temp in table["temp"].values():
        # return
        cp = table.loc[table["t"] == temp, "cp"].values[0] * 1000
        k = table.loc[table["t"] == temp, "k"].values[0]
        nu = table.loc[table["t"] == temp, "nu"].values[0]
        rho = table.loc[table["t"] == temp, "rho"].values[0]
        nu_k = nu / rho
        pr = nu * cp / k

    else:
        cp = np.interp(temp, table["t"], table["cp"]) * 1000
        k = np.interp(temp, table["t"], table["k"])
        rho = np.interp(temp, table["t"], table["rho"])
        nu_k = nu / rho
        pr = nu * cp / k
    # interpolate

    return cp, k, pr, nu_k, rho
