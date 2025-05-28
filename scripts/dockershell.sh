#!/bin/bash
###############################################################################
## Function
log() {
    echo "$(date +"%Y-%m-%dT%H:%M:%S.%03N") - $*"
}

parse_args() {
    if [ "$#" -eq 0 ]; then
        help
        exit 1
    fi

    while [ $# -gt 0 ]; do
        case "$1" in
        -h | --help)
            shift
            help
            exit 0
            ;;
        -d | --device)
            shift
            DEVICE="--device=${1}"
            log "Using device: ${DEVICE}"
            shift
            ;;
        -r | --rebuild)
            shift
            REBUILD_IMAGE=true
            ;;
        *)
            echo "Invalid option: $1" >&2
            help
            exit 1
            ;;
        esac
    done
}

###############################################################################
## Parameters
DOCKER_IMAGE_EXECUTED_LOCALLY='yocto_tales:local'
DOCKERFILE='Dockerfile.yocto'
REBUILD_IMAGE=false

## Fixed variables
SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
RUN_CMD="docker run --rm -it -v $(pwd):/home/embeddev/yocto_tales -v /tftpboot:/home/embeddev/tftpboot --cap-add=NET_ADMIN"

parse_args "$@"

log "SCRIPT_DIR = ${SCRIPT_DIR}"

if [ "${REBUILD_IMAGE}" = "true" ]; then
    log "erasing ${DOCKER_IMAGE_EXECUTED_LOCALLY}..."
    docker rmi -f ${DOCKER_IMAGE_EXECUTED_LOCALLY}
fi

if [[ "$(docker images -q ${DOCKER_IMAGE_EXECUTED_LOCALLY} 2>/dev/null)" == "" ]]; then
    log "${DOCKER_IMAGE_EXECUTED_LOCALLY} do no exists! building it..."
    uid="$(id -u)"
    gid="$(id -g)"
    echo "Creating docker image (user, UID=${uid} and GID=${gid})"
    docker build -f ${SCRIPT_DIR}/../docker/${DOCKERFILE} \
        --build-arg USER_UID=${uid} --build-arg USER_GID=${gid} \
        -t ${DOCKER_IMAGE_EXECUTED_LOCALLY} . &&
        ${RUN_CMD} "${DEVICE}" ${DOCKER_IMAGE_EXECUTED_LOCALLY}
else
    log "yeah! ${DOCKER_IMAGE_EXECUTED_LOCALLY} exists!!"
    ${RUN_CMD} "${DEVICE}" ${DOCKER_IMAGE_EXECUTED_LOCALLY}
fi
