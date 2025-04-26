#!/bin/bash
###############################################################################
## Functions
log() {
	echo "$(date +"%Y-%m-%dT%H:%M:%S.%03N") - $*"
}

help() {
	echo "Script used to setup yocto for the first time."
	echo
	echo "Syntax:"
	echo "setup_yocto.sh -r <repository> -t <repostory_tag> [-h]"
	echo "options:"
	echo "-r|--repository   The repository with the layers used in the init."
	echo "-t|--tag          The tag of the repository with the layers."
	echo "-d|--directory    Directory where yocto will be setup."
	echo ""
}
###############################################################################
## Parameters
ONLY_HELP=""

## Fixed variables
SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

parse_args() {
	if [ "$#" -eq 0 ]; then
		log "No arguments found ("$@")..."
		help
	fi

	while [ $# -gt 0 ]; do
		case "$1" in
		-h | --help)
			shift
			help
			ONLY_HELP=""
			;;
		-r | --repository)
			shift
			REPOSITORY="${1}"
			shift
			;;
		-t | --tag)
			shift
			REPOSITORY_TAG="${1}"
			shift
			;;
		-d | --directory)
			shift
			DIRECTORY="${1}"
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
	# Define an array of variables
	variables=("REPOSITORY" "REPOSITORY_TAG" "DIRECTORY")

	# Check if any variable is empty
	for var in "${variables[@]}"; do
		if [ -z "${!var}" ]; then
			echo "Variable $var is empty"
			exit 1
		fi
	done
}

main() {
	log "Setting up yocto (${REPOSITORY}:${REPOSITORY_TAG}) in ${DIRECTORY}"
	cd ${DIRECTORY}
	repo init -u ${REPOSITORY} -b ${REPOSITORY_TAG}
	repo sync
	log "Repositories already synced"
	ls -lash
	source ${DIRECTORY}/setupsdk
	log "Yocto already setup in ${DIRECTORY}! :)"
}

parse_args "$@"
if [ -n "${ONLY_HELP}" ]; then
	check_prereq
	main
fi
