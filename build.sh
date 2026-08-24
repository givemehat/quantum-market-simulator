#!/bin/bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Build the React Dashboard
echo "Building the dashboard..."
cd dashboard
npm install
npm run build
echo "Build complete."
