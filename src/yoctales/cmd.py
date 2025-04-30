from abc import ABC, abstractmethod
import subprocess
import logging
import select
import shlex
import os
import re
from datetime import datetime
import stat


logger = logging.getLogger(__name__)


def extract_git_repo_name_from_uri(uri: str) -> str:
    """ Extract git repository name from the URI used to clone it.

    uri = git://git.openembedded.org/meta-openembedded => meta-openembedded
    uri = git://git.yoctoproject.org/poky => poky
    uri = git@github.com:marifantesuper_repo.git => super_repo

    :param uri: the URI used to clone the repo.
    :return: repository name or an empty string if error.
    """
    pattern = r'^(git(?:@|:\/\/)[^/:\s]+[:/]|https?:\/\/[^/:\s]+\/|ssh:\/\/[^/:\s]+\/)([^/:\s]+\/)?([^/:\s]+?)(?:\.git)?$'
    match = re.search(pattern, uri)

    return match.group(3) if match else ""


class CommandFailed(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Command(ABC):
    @abstractmethod
    def execute(self):
        pass


class CommandShell(Command):
    """ Command executed in the iterator that executes something in a shell. """
    def __init__(self, *args, **kwargs):
        """ Constructor of the shell command.

        :param name: a name to identify this command.
        :param call: the exact call that will be done in the shell.
        :param cwd: in which path will be done the call (default is current path).
        :param shell: set to true if you want invoke a shell to execute the command.
        paset the call inside it and then execute that script file.
        """
        _ = args
        self.name = kwargs['name']
        self.call = kwargs['call']
        self.shell = True if 'shell' in kwargs else False
        self.cwd = '.' if 'cwd' not in kwargs else kwargs['cwd']
        self._fail_prefix = f"Command [{self.name}: {self.call}] failed: "

    def __str__(self):
        """ String reprenstation of the shell command """
        cwd = self.cwd if self.cwd else '.'
        return f"{self.name:25} : {cwd:35} : {self.call}"

    def execute(self) -> None:
        """Execute command in shell."""
        self._execute_check_errors()

    def _execute_check_errors(self) -> None:
        """Execute command in shell.

        If the exit code of the command is non-zero or is not found then
        raise a CommandFailed exception.
        """
        _, _, exit_code, command_not_found = self._execute_in_shell()

        if exit_code != 0:
            raise CommandFailed(f"{self._fail_prefix}Exit code is not zero (it is {exit_code})")

        if command_not_found:
            raise CommandFailed(f"{self._fail_prefix}Command not found")

    def _execute_in_shell(self) -> tuple:
        """Executes a shell command and retrieves stdout, stderr, and exit code.

        :param command: The shell command to execute.
        :param cwd: The directory where the command will be executed. If none is given
        the same directory where the script is executed will be used.
        :returns: (stdout, stderr, exit_code, command_not_found)
        """
        stdout = ""
        stderr = ""
        process_finished = False

        args = self.call if self.shell else shlex.split(self.call)
        logger.info(f"Executing: \"{args}\"")

        try:
            with subprocess.Popen(args, stdout=subprocess.PIPE,  # Capture standard output
                                  stderr=subprocess.PIPE,  # Capture standard error
                                  text=True,
                                  cwd=self.cwd,
                                  shell=self.shell) as process:

                while not process_finished:
                    reads = []

                    if process.stdout:
                        reads.append(process.stdout.fileno())

                    if process.stderr:
                        reads.append(process.stderr.fileno())

                    ret = select.select(reads, [], [])

                    for fd in ret[0]:
                        if process.stdout and fd == process.stdout.fileno():
                            stdout_line = process.stdout.readline()
                            if stdout_line:
                                logger.info(stdout_line)
                                stdout += stdout_line
                        elif process.stderr and fd == process.stderr.fileno():
                            stderr_line = process.stderr.readline()
                            if stderr_line:
                                logger.error(stderr_line)
                                stderr += stderr_line

                    # Check if the process has finished
                    if process.poll() is not None:
                        process_finished = True

                exit_code = process.returncode  # Get the exit code

                command_not_found = (exit_code == 127) or ("command not found" in stderr.lower())

        except FileNotFoundError as excpt:
            logger.error(f"Command \"{self.call}\" not found: {excpt}")
            stdout, stderr = "", "Command not found"
            exit_code = 127
            command_not_found = True

        return stdout, stderr, exit_code, command_not_found


class CommandGitClone(CommandShell):
    """ Specific command to clone a repository into a directory. """
    def __init__(self, *args, **kwargs):
        """ Constructor of the git clone shell command.

        :param uri: the URI of the repository.
        :param revision: the tag, commit or SHA of the repository.
        """
        self._uri = kwargs['uri']
        self._revision = kwargs['revision']
        kwargs['call'] = f"git clone {self._uri} -b {self._revision}"
        super().__init__(*args, **kwargs)

        self._repo_name = extract_git_repo_name_from_uri(self._uri)
        self._repo_path = os.path.join(self.cwd, self._repo_name)

    def git_repo_exists(self) -> bool:
        """ Verify if the repo already exists. """
        return os.path.isdir(os.path.join(self._repo_path, ".git"))

    def execute(self) -> None:
        """Execute command in shell."""
        if self.git_repo_exists():
            logger.info(f"Repository {self._uri} already cloned into {self._repo_path}")
        else:
            self._execute_check_errors()


class CommandExecuteInShellScript(CommandShell):
    """ Specific command to create a temporary script file with the call and execute it. """
    def __init__(self, *args, **kwargs):
        """ Constructor of the temporary shell command. """
        super().__init__(*args, **kwargs)

        self._call_body = self.call
        self._tmp_script_path = f"{os.path.join(self.cwd, self.name)}_tmp_script"
        self.call = os.path.join(".", self._tmp_script_path)
        self._create_temporary_script_file()

    def _create_temporary_script_file(self) -> None:
        """ Create a temporary script with the call. """
        header = "#!/bin/bash\n"
        header += f"# Auto-generated by yoctales on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        with open(self._tmp_script_path, 'w') as tmp_file:
            tmp_file.write(header)
            tmp_file.writelines(self._call_body.split(';'))

        current_permissions = os.stat(self._tmp_script_path).st_mode
        os.chmod(self._tmp_script_path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        logger.info(f"Created temporary script in {self._tmp_script_path}")
