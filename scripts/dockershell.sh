#!/bin/bash
###############################################################################
## Function
log() {
    echo "$(date +"%Y-%m-%dT%H:%M:%S.%03N") - $*"
}

DOCKER_RUN_ARGS=()

help() {
    echo "Usage: $0 [OPTIONS] [DOCKER_RUN_ARGS]"
    echo "Options:"
    echo "  -h, --help          Show this help message and exit"
    echo "  -r, --rebuild       Rebuild the Docker image before running"
    echo ""
    echo "DOCKER_RUN_ARGS are passed directly to the docker run command."
    echo ""
    echo "Example:"
    echo "  $0 -r --rm -p 8006:8006 -> rebuild docker image and run it with --rm and port mapping"
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
        -r | --rebuild)
            shift
            REBUILD_IMAGE=true
            ;;
        *)
            DOCKER_RUN_ARGS=("$@")
            log "Extra docker run args: ${DOCKER_RUN_ARGS[@]}"
            break
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

DOCKER_RUN_FULL_CMD="${RUN_CMD} ${DOCKER_RUN_ARGS[@]} ${DOCKER_IMAGE_EXECUTED_LOCALLY}"

log "Welcome to $0: Yocto Tales Docker Shell script!"
log "SCRIPT_DIR = ${SCRIPT_DIR}"
log "Docker run full command: ${DOCKER_RUN_FULL_CMD}"

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
        ${DOCKER_RUN_FULL_CMD}
else
    log "yeah! ${DOCKER_IMAGE_EXECUTED_LOCALLY} exists!!"
    ${DOCKER_RUN_FULL_CMD}
fi
