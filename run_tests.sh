#!/bin/bash

RUN_UNIT_TESTS=0
RUN_E2E_TESTS=0

run_local_tests() {
    set -o allexport
    source .envs/local-test.env
    pytest dataworkspace/dataworkspace $@
}

while getopts "udte" opt; do
  case ${opt} in
    u) make services-up; shift ;;
    d) make services-down; shift ;;
    t) RUN_UNIT_TESTS=1; shift ;;
    e) RUN_E2E_TESTS=1; shift ;;
  esac
done

if [[ ${RUN_UNIT_TESTS} == 1 ]]; then
    run_local_tests $@
elif [[ ${RUN_E2E_TESTS} == 1 ]]; then
    echo "Not currently supported."
fi
