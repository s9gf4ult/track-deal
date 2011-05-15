#!/bin/bash
for file in tests/*.py; do
    PYTHONPATH="./src:./tests" python $file
done
