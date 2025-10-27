#! /bin/bash -e

script_dir=$(dirname "$0")

echo "Resetting jumppad environment to clean huggingface state"
jumppad down
sudo rm -rf $script_dir/data
jumppad up $script_dir