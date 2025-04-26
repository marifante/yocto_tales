"""
Command Line Interface used to launch yoctales application.
"""
import logging
import argparse

from yoctales.linux_factory import create_linux_image


FORMAT = (
    "%(asctime)-15s %(threadName)-15s "
    "%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s"
)


log = logging.getLogger(__name__)


def parse_args():
    """ Parse arguments given to this CLI. """
    parser = argparse.ArgumentParser(description="Application used to build linux images using yocto.")

    parser.add_argument("--config", required=True, type=str, help="Yoctales config yml.")
    parser.add_argument("--log-level", default="INFO", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set logging level")
    parser.add_argument("--dry-run", default=False, action="store_true", help="Use this flag to only see the current plan that would be executed.")

    return parser.parse_args()


def main():
    """ Main Command Line Interface tool entrypoint. """
    args = parse_args()

    logging.basicConfig(format=FORMAT, level=args.log_level)

    log.info("Starting yoctales CLI!")

    create_linux_image(args.config, args.dry_run)


if __name__ == "__main__":
    main()
