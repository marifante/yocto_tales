#!/bin/bash

###############################################################################
## Functions
log() {
    echo -e "$(date +"%Y-%m-%dT%H:%M:%S.%03N") - $*"
}

help() {
    echo "Script used to burn a compressed SD image (.wic) image to a SD."
    echo
    echo "Syntax:"
    echo "burn_to_sd.sh [-i <input-dir>] [-d <device path>] [-m <machine>] [-h]"
    echo "options:"
    echo "-w|--wic          Path to .wic file."
    echo "-d|--device       Path to SD device."
    echo ""
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
            ;;
        -d | --device)
            shift
            DEVICE="${1}"
            shift
            ;;
        -w | --wic)
            shift
            WIC_PATH="${1}"
            shift
            ;;
        *)
            echo "Invalid option: $1" >&2
            help
            exit 1
            ;;
        esac
    done
}

check_prereq() {
    # Check if the script is run as root
    if [ "$EUID" -ne 0 ]; then
        log "Please run as root"
        exit 1
    fi

    # Define an array of variables
    variables=("DEVICE" "WIC_PATH")

    # Check if any variable is empty
    for var in "${variables[@]}"; do
        if [ -z "${!var}" ]; then
            echo "Variable $var is empty"
            exit 1
        fi
    done
}

wipe() {
    # Wipe down the SD card
    read -p "WARNING: This will wipe all data on $DEVICE. Are you sure? (yes/no): " CONFIRM
    if [[ $CONFIRM != "yes" ]]; then
        log "Operation cancelled."
        exit 1
    fi

    log "Unmounting all partitions on $DEVICE..."
    umount ${DEVICE}* || log "No partitions to unmount"

    log "Wiping $DEVICE..."
    dd if=/dev/zero of=${DEVICE} bs=512 count=1 status=progress
}

burn_wic() {
    umount ${DEVICE}
    dd if=${WIC_PATH} of=${DEVICE} bs=1M
    sync
}

main() {
    check_prereq
    wipe
    burn_wic
}

parse_args "$@"
main
