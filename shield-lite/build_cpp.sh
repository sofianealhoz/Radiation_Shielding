#!/bin/bash

# Script to build the C++ Monte Carlo extension for shield-lite
# Usage: ./build_cpp.sh [clean]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Building shield-lite C++ extension${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Check if we should clean first
if [ "$1" == "clean" ]; then
    echo -e "${YELLOW}Cleaning build directory...${NC}"
    rm -rf build
    rm -f src/shield_lite/_monte_carlo*.so
    rm -f src/shield_lite/_monte_carlo*.pyd
    echo -e "${GREEN}Clean complete.${NC}"
    echo ""
fi

# Check for required tools
echo "Checking dependencies..."

if ! command -v cmake &> /dev/null; then
    echo -e "${RED}Error: cmake not found. Please install it:${NC}"
    echo "  Ubuntu/Debian: sudo apt-get install cmake"
    echo "  macOS:         brew install cmake"
    echo "  Fedora:        sudo dnf install cmake"
    exit 1
fi

if ! command -v g++ &> /dev/null && ! command -v clang++ &> /dev/null; then
    echo -e "${RED}Error: C++ compiler not found. Please install g++ or clang++${NC}"
    exit 1
fi

echo -e "${GREEN}✓ cmake found${NC}"
echo -e "${GREEN}✓ C++ compiler found${NC}"
echo ""

# Check for pybind11
echo "Checking for pybind11..."
if ! python3 -c "import pybind11" 2>/dev/null; then
    echo -e "${YELLOW}pybind11 not found. Installing...${NC}"
    pip install pybind11
fi
echo -e "${GREEN}✓ pybind11 found${NC}"
echo ""

# Create build directory
mkdir -p build
cd build

# Configure with CMake
echo "Configuring with CMake..."
cmake .. -DCMAKE_BUILD_TYPE=Release

# Build
echo ""
echo "Building (this may take a minute)..."
make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)

# Copy module to package directory
echo ""
echo "Installing module..."
if [ -f _monte_carlo*.so ]; then
    cp _monte_carlo*.so ../src/shield_lite/
    echo -e "${GREEN}✓ Copied _monte_carlo.so${NC}"
elif [ -f _monte_carlo*.pyd ]; then
    cp _monte_carlo*.pyd ../src/shield_lite/
    echo -e "${GREEN}✓ Copied _monte_carlo.pyd${NC}"
else
    echo -e "${RED}Error: Could not find compiled module${NC}"
    exit 1
fi

cd ..

# Test import
echo ""
echo "Testing import..."
if python3 -c "from shield_lite.core import MonteCarloShieldSimulator; print('✓ Import successful')" 2>/dev/null; then
    echo -e "${GREEN}✓ Module import successful!${NC}"
else
    echo -e "${RED}✗ Module import failed${NC}"
    echo "Try running: python3 -c 'from shield_lite.core import MonteCarloShieldSimulator'"
    exit 1
fi

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Build complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Run examples:  python3 examples/example_monte_carlo.py"
echo "  2. Run tests:     pytest tests/test_monte_carlo.py -v"
echo "  3. Read docs:     cat CPP_MONTE_CARLO_README.md"
echo ""
