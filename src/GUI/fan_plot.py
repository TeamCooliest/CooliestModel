import logging
from pathlib import Path

import dash
from dash import dcc
from dash import html
import pandas as pd
import plotly.express as px

from src.model.calculate_wall_temp import calculate_wall_temp


logging.basicConfig(level=logging.DEBUG)


def airflow_cfm_to_m3s(airflow_cfm):
    return airflow_cfm * 0.00047194745


def swap_keys_values(a):
    return dict((v, k) for k, v in a.items())


# read in fan data TODO clean data better
current_dir = Path(__file__).parent
fan_data = pd.read_csv(
    current_dir / "../../data/model/fan_specifications_rack_fans.csv", index_col=0
)
fan_data = fan_data.loc[fan_data.index.dropna()]
airflow = pd.to_numeric(fan_data["Airflow (CFM)"], errors="coerce").dropna()
airflow = airflow_cfm_to_m3s(airflow)
fans = airflow.index
fan_data = fan_data.loc[fans]
fan_data["Airflow (m3/s)"] = airflow


# Define the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div(
    [
        dcc.Input(id="width-input", placeholder="Enter a width...", value=0.938),
        dcc.Input(id="height-input", placeholder="Enter a height...", value=0.04445),
        dcc.Input(id="length-input", placeholder="Enter a length...", value=0.45086),
        dcc.Input(id="T_in-input", placeholder="Enter a T_in...", value=291.15),
        dcc.Input(id="q_chip-input", placeholder="Enter a q_chip...", value=50),
        dcc.Input(
            id="fluid_name-input", placeholder="Enter a fluid_name...", value="air"
        ),
        dcc.Dropdown(
            id="V_dot-radio",
            options={a: a for a in fans.to_list()},
            multi=True,
            value=fans[0],
        ),
        # Create a div to hold the bar chart
        html.Div(id="bar-chart"),
    ]
)


# Define the callback to generate the bar chart
@app.callback(
    dash.dependencies.Output("bar-chart", "children"),
    [
        dash.dependencies.Input("width-input", "value"),
        dash.dependencies.Input("height-input", "value"),
        dash.dependencies.Input("length-input", "value"),
        dash.dependencies.Input("T_in-input", "value"),
        dash.dependencies.Input("q_chip-input", "value"),
        dash.dependencies.Input("fluid_name-input", "value"),
        dash.dependencies.Input("V_dot-radio", "value"),
    ],
)
def update_bar_chart(width, height, length, t_in, q_chip, fluid_name, fan_names):
    width = float(width)
    height = float(height)
    length = float(length)
    t_in = float(t_in)
    q_chip = float(q_chip)

    print(fan_names)

    wall_temps = {
        fan_name: calculate_wall_temp(
            width,
            height,
            length,
            t_in,
            airflow.loc[fan_name],
            q_chip,
            fluid_name,
        )
        for fan_name in fan_names
    }

    wall_temps = pd.DataFrame(pd.Series(wall_temps), columns=["wall_temp"])
    # Create the bar chart using Plotly Express
    fig = px.bar(wall_temps)

    # Return the Plotly graph as a div
    return dcc.Graph(figure=fig)


def main():
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
