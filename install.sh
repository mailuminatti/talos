#!/bin/sh

git clone https://github.com/mailuminatti/talos.git
cd $(pwd)/talos/cli
echo "Installing Talos"
python3 -m pip install .
cd ../../
chown -R $USER: talos
echo "Cleaning up"
rm -f -R talos
