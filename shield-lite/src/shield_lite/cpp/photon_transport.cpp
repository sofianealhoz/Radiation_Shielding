#include "photon_transport.h"
#include <cmath>
#include <algorithm>
#include <stdexcept>

namespace shield_lite {

constexpr double ELECTRON_REST_MASS_MEV = 0.511; // MeV
constexpr double PI = 3.14159265358979323846;

PhotonTransport::PhotonTransport(unsigned int seed)
    : rng_(seed), uniform_dist_(0.0, 1.0) {}

void PhotonTransport::setShieldLayers(const std::vector<MaterialLayer>& layers) {
    layers_ = layers;
}

double PhotonTransport::getTotalThickness() const {
    double total = 0.0;
    for (const auto& layer : layers_) {
        total += layer.thickness_cm;
    }
    return total;
}

int PhotonTransport::findLayer(double z_position) const {
    double accumulated_z = 0.0;
    for (size_t i = 0; i < layers_.size(); ++i) {
        accumulated_z += layers_[i].thickness_cm;
        if (z_position < accumulated_z) {
            return static_cast<int>(i);
        }
    }
    return -1; // Beyond shield
}

double PhotonTransport::sampleFreePath(double mu_total) {
    // Sample exponential distribution: -ln(xi) / mu
    double xi = uniform_dist_(rng_);
    return -std::log(xi) / mu_total;
}

bool PhotonTransport::isComptonScattering(double mu_compton, double mu_total) {
    double prob_compton = mu_compton / mu_total;
    return uniform_dist_(rng_) < prob_compton;
}

void PhotonTransport::comptonScatter(Photon& photon) {
    // Klein-Nishina formula - simplified version
    // Sample scattering angle (isotropic approximation for simplicity)
    double cos_theta = 2.0 * uniform_dist_(rng_) - 1.0;
    double phi = 2.0 * PI * uniform_dist_(rng_);

    // Energy after Compton scattering
    double alpha = photon.energy_MeV / ELECTRON_REST_MASS_MEV;
    double energy_ratio = 1.0 / (1.0 + alpha * (1.0 - cos_theta));

    // Update photon energy
    double new_energy = photon.energy_MeV * energy_ratio;

    // Deposit energy to material
    // (In a full simulation, this would be tracked as dose)

    photon.energy_MeV = new_energy;

    // Update direction (simplified - assume isotropic scattering)
    double sin_theta = std::sqrt(1.0 - cos_theta * cos_theta);
    photon.dx = sin_theta * std::cos(phi);
    photon.dy = sin_theta * std::sin(phi);
    photon.dz = cos_theta;

    // Adjust weight for scattering probability (optional - simplified here)
    photon.weight *= 0.95; // Approximate scattering efficiency
}

void PhotonTransport::transportPhoton(Photon& photon, double& dose_deposited, bool& transmitted) {
    transmitted = false;
    dose_deposited = 0.0;

    double total_thickness = getTotalThickness();

    // Transport loop
    while (photon.alive && photon.z < total_thickness && photon.energy_MeV > 0.01) {
        // Find current layer
        int layer_idx = findLayer(photon.z);

        if (layer_idx < 0) {
            // Photon exited the shield
            transmitted = true;
            break;
        }

        const MaterialLayer& current_layer = layers_[layer_idx];

        // Sample free path
        double free_path = sampleFreePath(current_layer.mu_total_cm);

        // Calculate distance to layer boundary
        double layer_start_z = 0.0;
        for (int i = 0; i < layer_idx; ++i) {
            layer_start_z += layers_[i].thickness_cm;
        }
        double layer_end_z = layer_start_z + current_layer.thickness_cm;
        double distance_to_boundary = (layer_end_z - photon.z) / std::abs(photon.dz);

        // Move photon
        if (free_path < distance_to_boundary) {
            // Interaction occurs within the layer
            photon.z += free_path * photon.dz;

            // Determine interaction type
            if (isComptonScattering(current_layer.mu_compton_cm, current_layer.mu_total_cm)) {
                // Compton scattering
                comptonScatter(photon);
            } else {
                // Photoelectric absorption - photon dies
                dose_deposited += photon.energy_MeV * photon.weight;
                photon.alive = false;
                break;
            }
        } else {
            // Move to boundary
            photon.z += distance_to_boundary * std::abs(photon.dz);
        }

        // Check if photon has very low energy
        if (photon.energy_MeV < 0.01) {
            photon.alive = false;
        }
    }

    // Check if transmitted
    if (photon.z >= total_thickness && photon.alive) {
        transmitted = true;
    }
}

MonteCarloResult PhotonTransport::simulate(double source_energy_MeV,
                                          int num_photons,
                                          double source_area_cm2) {
    if (layers_.empty()) {
        throw std::runtime_error("No shield layers defined");
    }

    MonteCarloResult result;
    result.total_photons = num_photons;

    double total_dose_transmitted = 0.0;
    double total_dose_absorbed = 0.0;
    std::vector<double> transmitted_doses;

    // Run Monte Carlo simulation
    for (int i = 0; i < num_photons; ++i) {
        Photon photon(source_energy_MeV);
        double dose_deposited = 0.0;
        bool transmitted = false;

        transportPhoton(photon, dose_deposited, transmitted);

        if (transmitted) {
            result.transmitted_photons++;
            total_dose_transmitted += photon.energy_MeV * photon.weight;
            transmitted_doses.push_back(photon.energy_MeV * photon.weight);
        }

        total_dose_absorbed += dose_deposited;
    }

    // Calculate results
    result.dose_transmitted = total_dose_transmitted / num_photons;
    result.dose_absorbed = total_dose_absorbed / num_photons;
    result.transmission_factor = static_cast<double>(result.transmitted_photons) / num_photons;

    // Calculate buildup factor (ratio of total dose to uncollided dose)
    double uncollided_transmission = std::exp(-getTotalThickness() * layers_[0].mu_total_cm);
    if (uncollided_transmission > 1e-10) {
        result.buildup_factor = result.transmission_factor / uncollided_transmission;
    }

    // Calculate statistical uncertainty (standard error)
    if (!transmitted_doses.empty()) {
        double mean = total_dose_transmitted / transmitted_doses.size();
        double variance = 0.0;
        for (double dose : transmitted_doses) {
            variance += (dose - mean) * (dose - mean);
        }
        variance /= transmitted_doses.size();
        result.uncertainty = std::sqrt(variance / transmitted_doses.size());
    }

    return result;
}

} // namespace shield_lite
