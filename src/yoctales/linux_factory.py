import logging
import os
import time

from yoctales.cmd import CommandShell, CommandGitClone, CommandExecuteInShellScript
from yoctales.config_parser import ConfigParser


logger = logging.getLogger(__name__)


class LinuxImageInvoker:
    """
    Linux image factory MVP. In this object you can add (sequentially) all the
    steps needed to create a given image. Then, when all the steps are already
    stored inside the object you can just build the image doing object.execute_all().
    """
    def __init__(self):
        """ Linux image creator constructor. Once you create this object,
        you need to add the sequential commands needed to create the image.
        """
        self.commands = []

    def add_command(self, command: CommandShell) -> None:
        """ Add a command to the list of commands needed to build this image.

        :param command: the command to be executed.
        """
        self.commands.append(command)

    def execute_all(self) -> None:
        """ Execute all the needed commands to build (invoke) the linux image. """
        for idx, command in enumerate(self.commands):
            try:
                logger.info(f"Executing step {idx}: ({command})")
                command.execute()
            except Exception as exc:
                logger.error(f"Command failed: {exc}")
                break

    def describe_plan(self) -> str:
        """ Creates a string with the whole plan to create this linux image. """
        return "\n".join([f"{step:3}: {cmd}" for step, cmd in enumerate(self.commands)])


def scan_for_build_conf_files(path: str) -> list:
    """ This function will scan the given path for all yocto build configuration files
    and return a list with the paths to those files.

    :return: a list with the paths of the configuration files.
    :raises FileNotFoundError: If any of the files are not found.
    """
    files_to_scan = ["bblayers.conf", "local.conf"]
    files_found = []

    for file in files_to_scan:
        file_path = os.path.join(path, file)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found. Please create it before running the tool.")
        else:
            files_found.append(file_path)

    return files_found


def create_linux_image(config_file: str, dry_run: bool = False) -> None:
    """
    Process a configuration file, pick the correct yoctale object and
    execute it to create a linux image.

    :param config_file: the path to the yml file with the configuration
    to create the linux image.
    :param dry_run: set to True if you want to only process the config file
    and check the steps that will be taken.
    """
    t0 = time.monotonic()
    build_conf_files = scan_for_build_conf_files(os.path.dirname(config_file))

    config = ConfigParser(config_file)

    work_directory = f"work/{config.name}"

    invoker = LinuxImageInvoker()

    logger.info("Creating plan to build linux image...")

    invoker.add_command(CommandShell(name = "create work dir", call = f"mkdir -p {work_directory}/layers"))

    for idx, layer in enumerate(config.layers):
        invoker.add_command(CommandGitClone(name = f"clone layer {idx:3}",
                                            uri = layer['uri'],
                                            revision = layer['revision'],
                                            cwd = os.path.join(work_directory, "layers")))

    # Copy build configuration files to the work directory
    work_build_conf_dir = os.path.join(work_directory, "build/conf")
    invoker.add_command(CommandShell(name = "create build conf dir", call = f"mkdir -p {work_build_conf_dir}"))

    for file in build_conf_files:
        invoker.add_command(CommandShell(name = f"copy {os.path.basename(file)}",
                                         call = f"cp {file} {work_build_conf_dir}"))

    if config.setup:
        for idx, cmd in enumerate(config.setup['command']):
            invoker.add_command(CommandShell(name = f"setup command {idx:3}",
                                             call = cmd['call'],
                                             cwd = os.path.join(work_directory, cmd['path'])))

    build_script_cmds = [config.bitbake['setup_script'], config.bitbake['command']]
    invoker.add_command(CommandExecuteInShellScript(name = "build_image_with_bitbake",
                                                    call = '\n'.join(build_script_cmds),
                                                    cwd = work_directory))

    logger.info(f"Plan:\n{invoker.describe_plan()}")

    if not dry_run:
        invoker.execute_all()

    duration_m = (time.monotonic() - t0)/60
    logger.info(f"Linux image creation took {duration_m:.5f} minutes.")
