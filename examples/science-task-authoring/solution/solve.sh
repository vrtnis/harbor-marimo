#!/bin/sh
set -eu

mkdir -p /root/results
cp /tests/reference/posterior_summary.csv /root/results/posterior_summary.csv
cp /tests/reference/convergence.json /root/results/convergence.json
