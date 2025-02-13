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
    uv run -- coverage run -m unittest tests.test_${_source_type}_generator
}

run_tox() {
    log-info "running all unit tests"
    uv run -- tox -r
}


# execute
case ${1} in
   "help") usage ;;
   "aws") test_generator aws ;;
   "azure") test_generator azure ;;
   "gcp") test_generator gcp ;;
   "ocp") test_generator ocp ;;
   "oci") test_generator oci ;;
   "all") run_tox ;;
   *) usage ;;
esac
