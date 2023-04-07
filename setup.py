from setuptools import setup

setup(
    name="TeamCooliest",
    version="0.0.0",
    packages=["src", "src.model", "src.GUI"],
    entry_points={
        "console_scripts": [
            "model_solve = src.model.calculate_wall_temp:main",
            "gui = src.GUI:main",
        ]
    },
)
