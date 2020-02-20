#!/bin/bash
COMMAND=$@
export KOKU_PATH="${KOKU_PATH}"
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
NISE_PATH="$(dirname $(pwd))"
IMAGE="docker-registry.upshift.redhat.com/insights-qe/iqe-tests"

FLAGS=
HOST=$(uname)
if [ $HOST == 'Linux' ]; then
    FLAGS=':Z'
fi

main() {
    if command -v docker > /dev/null 2>&1; then
        CONTAINER_RUNTIME=docker
    elif command -v podman > /dev/null 2>&1; then
        CONTAINER_RUNTIME=podman
    else
        echo "Please install podman or docker first"
        exit 1
    fi

    $CONTAINER_RUNTIME pull $IMAGE

    $CONTAINER_RUNTIME run -it \
                           --rm \
                           --network="host" \
                           --name "iqe-nise" \
                           -e "IQE_TESTS_LOCAL_CONF_PATH=/iqe_conf" \
                           -e "ENV_FOR_DYNACONF=local" \
                           -v $KOKU_PATH/testing/conf:/iqe_conf${FLAGS} \
                           -v $KOKU_PATH/local_providers/aws_local:/tmp/local_bucket${FLAGS} \
                           -v $KOKU_PATH/local_providers/aws_local_0:/tmp/local_bucket_0${FLAGS} \
                           -v $KOKU_PATH/local_providers/aws_local_1:/tmp/local_bucket_1${FLAGS} \
                           -v $KOKU_PATH/local_providers/aws_local_2:/tmp/local_bucket_2${FLAGS} \
                           -v $KOKU_PATH/local_providers/aws_local_3:/tmp/local_bucket_3${FLAGS} \
                           -v $KOKU_PATH/local_providers/aws_local_4:/tmp/local_bucket_4${FLAGS} \
                           -v $KOKU_PATH/local_providers/aws_local_5:/tmp/local_bucket_5${FLAGS} \
                           -v $KOKU_PATH/local_providers/azure_local:/tmp/local_container${FLAGS} \
                           -v $KOKU_PATH/pvc_dir/insights_local:/var/tmp/masu/insights_local${FLAGS} \
                           -v $NISE_PATH:/var/nise/${FLAGS} \
                           $IMAGE \
                           bash -c "cd /var/nise/scripts/; ./entrypoint_append.sh; cd -; $COMMAND" \

}

main
