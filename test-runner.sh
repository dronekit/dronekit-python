#!/bin/bash
python=$(which python)
for testCase in $(ls | grep 'test' | grep 'py')
do
    $python $testCase
done
