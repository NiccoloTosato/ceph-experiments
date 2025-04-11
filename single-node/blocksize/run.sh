#!/bin/bash

for i in {1..5}
do
  echo "Run #$i:"
  fio --output-format=json+ --output=results/bs-experiment_${i}.json bs-experiment.fio
done
