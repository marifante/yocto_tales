"""
Command Line Interface used to launch yoctales application.
"""
import logging
import argparse
import pkg_resources

from yoctales.linux_factory import create_linux_image


FORMAT = (
    "%(asctime)-15s "
    "%(levelname)-6s %(module)-15s:%(lineno)-8s %(message)s"
)


log = logging.getLogger(__name__)

def get_package_version(package_name: str) -> str:
    """Retrieve the version of an installed pip package."""
    try:
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        return f"Package {package_name} not found"

def parse_args():
    """ Parse arguments given to this CLI. """
    parser = argparse.ArgumentParser(description="Application used to build linux images using yocto.")

    # Ensure at least one group of arguments is provided
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--config", type=str, help="Yoctales config yml.")
    group.add_argument("--version", default=False, action="store_true", help="Print yoctales installed version.")

    parser.add_argument("--log-level", default="INFO", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set logging level")
    parser.add_argument("--dry-run", default=False, action="store_true", help="Use this flag to only see the current plan that would be executed.")

    return parser.parse_args()


def main():
    """ Main Command Line Interface tool entrypoint. """
    args = parse_args()

    logging.basicConfig(format=FORMAT, level=args.log_level)

    log.info("Starting yoctales CLI!")

    if args.version:
        log.info(f"Yoctales version: {get_package_version('yoctales')}")
    elif args.config:
        create_linux_image(args.config, args.dry_run)
    else:
        raise ValueError(f"Unhandled case, at least args.version or args.config should be set.")


if __name__ == "__main__":
    main()
