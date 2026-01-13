#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "photon_transport.h"
#include "monte_carlo.cpp"

namespace py = pybind11;
using namespace shield_lite;

PYBIND11_MODULE(_monte_carlo, m) {
    m.doc() = "Monte Carlo photon transport simulation for gamma ray shielding";

    // MonteCarloResult structure
    py::class_<MonteCarloResult>(m, "MonteCarloResult")
        .def(py::init<>())
        .def_readonly("dose_transmitted", &MonteCarloResult::dose_transmitted,
                     "Dose transmitted through the shield (MeV per photon)")
        .def_readonly("dose_absorbed", &MonteCarloResult::dose_absorbed,
                     "Dose absorbed in the shield (MeV per photon)")
        .def_readonly("transmission_factor", &MonteCarloResult::transmission_factor,
                     "Fraction of photons that pass through the shield")
        .def_readonly("buildup_factor", &MonteCarloResult::buildup_factor,
                     "Dose buildup factor (accounts for scattered photons)")
        .def_readonly("uncertainty", &MonteCarloResult::uncertainty,
                     "Statistical uncertainty of the simulation")
        .def_readonly("total_photons", &MonteCarloResult::total_photons,
                     "Total number of photons simulated")
        .def_readonly("transmitted_photons", &MonteCarloResult::transmitted_photons,
                     "Number of photons transmitted through shield")
        .def("__repr__", [](const MonteCarloResult& r) {
            return "MonteCarloResult(transmission=" + std::to_string(r.transmission_factor) +
                   ", buildup_factor=" + std::to_string(r.buildup_factor) +
                   ", transmitted_photons=" + std::to_string(r.transmitted_photons) +
                   "/" + std::to_string(r.total_photons) + ")";
        });

    // MonteCarloSimulator class
    py::class_<MonteCarloSimulator>(m, "MonteCarloSimulator")
        .def(py::init<>(), "Create a Monte Carlo simulator with default random seed")
        .def(py::init<unsigned int>(), py::arg("seed"),
             "Create a Monte Carlo simulator with specified random seed")
        .def("add_layer", &MonteCarloSimulator::addLayer,
             py::arg("material_name"),
             py::arg("thickness_cm"),
             py::arg("mu_total"),
             py::arg("mu_compton"),
             py::arg("mu_photoelectric"),
             py::arg("density_g_cm3"),
             R"pbdoc(
                Add a material layer to the shield.

                Parameters:
                -----------
                material_name : str
                    Name of the material
                thickness_cm : float
                    Thickness of the layer in cm
                mu_total : float
                    Total attenuation coefficient in cm^-1
                mu_compton : float
                    Compton scattering coefficient in cm^-1
                mu_photoelectric : float
                    Photoelectric absorption coefficient in cm^-1
                density_g_cm3 : float
                    Density of the material in g/cm^3
             )pbdoc")
        .def("clear_layers", &MonteCarloSimulator::clearLayers,
             "Remove all layers from the shield configuration")
        .def("run", &MonteCarloSimulator::run,
             py::arg("source_energy_MeV"),
             py::arg("num_photons"),
             py::arg("source_area_cm2") = 1.0,
             R"pbdoc(
                Run the Monte Carlo simulation.

                Parameters:
                -----------
                source_energy_MeV : float
                    Energy of the gamma ray source in MeV
                num_photons : int
                    Number of photons to simulate (more = better statistics)
                source_area_cm2 : float, optional
                    Source area in cm^2 (default: 1.0)

                Returns:
                --------
                MonteCarloResult
                    Simulation results including dose, transmission, and buildup factor
             )pbdoc")
        .def("get_num_layers", &MonteCarloSimulator::getNumLayers,
             "Get the number of layers in the current shield configuration")
        .def("__repr__", [](const MonteCarloSimulator& sim) {
            return "MonteCarloSimulator(layers=" + std::to_string(sim.getNumLayers()) + ")";
        });

    // Module-level constants
    m.attr("ELECTRON_REST_MASS_MEV") = ELECTRON_REST_MASS_MEV;
    m.attr("__version__") = "0.1.0";
}
