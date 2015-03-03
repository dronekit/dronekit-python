#!/bin/bash
python=$(which python)
for testCase in $(ls | grep 'test\.py$')
do
    $python $testCase
done
