#pragma once
#include <vector>
#include <string>
#include <random>

namespace shield_lite {

// Material layer structure
struct MaterialLayer {
    std::string name;
    double thickness_cm;           // Thickness in cm
    double mu_total_cm;            // Total attenuation coefficient (cm^-1)
    double mu_compton_cm;          // Compton scattering coefficient (cm^-1)
    double mu_photoelectric_cm;    // Photoelectric absorption coefficient (cm^-1)
    double density_g_cm3;          // Density (g/cm^3)

    MaterialLayer(const std::string& n, double thick, double mu_tot,
                  double mu_comp, double mu_photo, double dens)
        : name(n), thickness_cm(thick), mu_total_cm(mu_tot),
          mu_compton_cm(mu_comp), mu_photoelectric_cm(mu_photo),
          density_g_cm3(dens) {}
};

// Photon particle
struct Photon {
    double energy_MeV;
    double x, y, z;               // Position (cm)
    double dx, dy, dz;            // Direction (normalized)
    double weight;                // Statistical weight
    bool alive;

    Photon(double E, double weight_init = 1.0)
        : energy_MeV(E), x(0), y(0), z(0),
          dx(0), dy(0), dz(1), weight(weight_init), alive(true) {}
};

// Result structure
struct MonteCarloResult {
    double dose_transmitted;       // Dose transmitted through shield
    double dose_absorbed;          // Dose absorbed in shield
    double transmission_factor;    // Fraction of photons transmitted
    double buildup_factor;         // Dose buildup factor
    double uncertainty;            // Statistical uncertainty
    int total_photons;
    int transmitted_photons;

    MonteCarloResult() : dose_transmitted(0), dose_absorbed(0),
                        transmission_factor(0), buildup_factor(1.0),
                        uncertainty(0), total_photons(0), transmitted_photons(0) {}
};

// Monte Carlo photon transport engine
class PhotonTransport {
public:
    PhotonTransport(unsigned int seed = 42);

    // Set the shield configuration
    void setShieldLayers(const std::vector<MaterialLayer>& layers);

    // Run Monte Carlo simulation
    MonteCarloResult simulate(double source_energy_MeV,
                             int num_photons,
                             double source_area_cm2 = 1.0);

private:
    std::vector<MaterialLayer> layers_;
    std::mt19937 rng_;
    std::uniform_real_distribution<double> uniform_dist_;

    // Transport a single photon through the shield
    void transportPhoton(Photon& photon, double& dose_deposited, bool& transmitted);

    // Sample free path length
    double sampleFreePath(double mu_total);

    // Sample interaction type (Compton or photoelectric)
    bool isComptonScattering(double mu_compton, double mu_total);

    // Perform Compton scattering
    void comptonScatter(Photon& photon);

    // Find which layer the photon is in
    int findLayer(double z_position) const;

    // Calculate total shield thickness
    double getTotalThickness() const;
};

} // namespace shield_lite
