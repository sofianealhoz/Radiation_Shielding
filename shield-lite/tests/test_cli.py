import pytest
from typer.testing import CliRunner
from shield_lite.cli import app

runner = CliRunner()

def test_calibration_command():
    result = runner.invoke(app, ["calibrate", "--data", "examples/config.yaml"])
    assert result.exit_code == 0
    assert "Calibration completed" in result.output

def test_dose_command():
    result = runner.invoke(app, ["dose", "--thicknesses", "material1=10,material2=5", "--mu", "material1=0.1,material2=0.2", "--S", "1.0"])
    assert result.exit_code == 0
    assert "Dose calculated" in result.output

def test_hvl_command():
    result = runner.invoke(app, ["hvl", "--material", "material1", "--energy", "1.0"])
    assert result.exit_code == 0
    assert "Half-Value Layer calculated" in result.output

def test_grid_search_command():
    result = runner.invoke(app, ["grid-search", "--order", "material1,material2", "--ranges", "material1=0-20,material2=0-20", "--Dmax", "1.0"])
    assert result.exit_code == 0
    assert "Grid search completed" in result.output