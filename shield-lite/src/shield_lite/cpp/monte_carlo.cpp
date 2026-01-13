#include "photon_transport.h"
#include <map>
#include <stdexcept>

namespace shield_lite {

// Helper class for easy Python interface
class MonteCarloSimulator {
public:
    MonteCarloSimulator(unsigned int seed = 42) : transport_(seed) {}

    // Add a material layer to the shield
    void addLayer(const std::string& material_name,
                  double thickness_cm,
                  double mu_total,
                  double mu_compton,
                  double mu_photoelectric,
                  double density_g_cm3) {
        layers_.emplace_back(material_name, thickness_cm, mu_total,
                           mu_compton, mu_photoelectric, density_g_cm3);
    }

    // Clear all layers
    void clearLayers() {
        layers_.clear();
    }

    // Run the simulation
    MonteCarloResult run(double source_energy_MeV,
                        int num_photons,
                        double source_area_cm2 = 1.0) {
        transport_.setShieldLayers(layers_);
        return transport_.simulate(source_energy_MeV, num_photons, source_area_cm2);
    }

    // Get number of layers
    size_t getNumLayers() const {
        return layers_.size();
    }

private:
    PhotonTransport transport_;
    std::vector<MaterialLayer> layers_;
};

} // namespace shield_lite
