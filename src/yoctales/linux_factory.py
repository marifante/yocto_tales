import logging
import yaml
import os

from yoctales.cmd import CommandShell, CommandGitClone


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
        for command in self.commands:
            try:
                command.execute()
            except Exception as exc:
                logger.error(f"Command failed: {exc}")
                break

    def describe_plan(self) -> str:
        """ Creates a string with the whole plan to create this linux image. """
        return "\n".join([f"{step:3}: {cmd}" for step, cmd in enumerate(self.commands)])


def create_linux_image(config_file: str, dry_run: bool = False) -> None:
    """
    Process a configuration file, pick the correct yoctale object and
    execute it to create a linux image.

    :param config_file: the path to the yml file with the configuration
    to create the linux image.
    :param dry_run: set to True if you want to only process the config file
    and check the steps that will be taken.
    """
    # Parse config file and create commands
    with open(config_file, "r") as file:
        yaml_data = yaml.safe_load(file)

    work_directory = f"work/{yaml_data['name']}"

    invoker = LinuxImageInvoker()

    logger.info("Creating plan to build linux image...")

    invoker.add_command(CommandShell(name = "create work directory", call = f"mkdir -p {work_directory}/layers"))

    for idx, layer in enumerate(yaml_data['layers']):
        invoker.add_command(CommandGitClone(name = f"clone layer {idx:3}",
                                            uri = layer['uri'],
                                            revision = layer['revision'],
                                            cwd = os.path.join(work_directory, "layers")))

    for idx, cmd in enumerate(yaml_data['setup']['command']):
        invoker.add_command(CommandShell(name = f"setup command {idx:3}",
                                         call = cmd['call'],
                                         cwd = os.path.join(work_directory, cmd['path'])))

    invoker.add_command(CommandShell(name = "build image with bitbake", call = f"bitbake {yaml_data['bitbake']['image']}"))

    logger.info(f"Plan:\n{invoker.describe_plan()}")

    if not dry_run:
        invoker.execute_all()
