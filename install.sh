#!/bin/sh

git clone https://github.com/mailuminatti/talos.git
cd $(pwd)/talos.cli
echo "Installing Talos"
pip3 install --editable .
cd ../../
chown -R $USER: talos
echo "Cleaning up"
rm -f -R talos
