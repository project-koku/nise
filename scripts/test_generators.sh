#!/usr/bin/env bash


SCRIPTS_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# import common functions
source $SCRIPTS_PATH/common/logging.sh

usage() {
    log-info "Usage: `basename $0` <source_type>"
    log-info ""
    log-info "source_type: <aws|azure|gcp|ocp>"
    log-info "help show usage"
}

# run single test
test_generator() {
    local _source_type=$1
    log-info "Running unit tests for ${_source_type}"
    python3 -m unittest tests.test_${_source_type}_generator
}

run_tox() {
    log-info "running all unit tests"
    tox -e py38
}


# execute
case ${1} in
   "help") usage ;;
   "aws") test_generator aws ;;
   "azure") test_generator azure ;;
   "gcp") test_generator gcp ;;
   "ocp") test_generator ocp ;;
   "all") run_tox ;;
   *) usage ;;
esac
