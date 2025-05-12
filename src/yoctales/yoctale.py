import logging
import yaml

logger = logging.getLogger(__name__)


class CommandExecuter:
    def __init__(self):
        self.commands = []

    def add_command(self, command):
        self.commands.append(command)

    def execute_all(self):
        for command in self.commands:
            try:
                command.execute()
            except Exception as e:
                print(f"Command failed: {e}")
                break



