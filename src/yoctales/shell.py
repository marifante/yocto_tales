import subprocess
import logging
import shlex
import select


logger = logging.getLogger(__name__)


def execute_in_shell(call: str, cwd: str, shell: bool = False) -> tuple:
    """Executes a shell command and retrieves stdout, stderr, and exit code.

    :param call: The shell command to execute.
    :param cwd: The directory where the command will be executed. If none is given
    the same directory where the script is executed will be used.
    :returns: (stdout, stderr, exit_code, command_not_found)
    """
    stdout = ""
    stderr = ""
    process_finished = False

    args = call if shell else shlex.split(call)
    logger.info(f"Going to {cwd} to execute: \"{args}\"")

    try:
        with subprocess.Popen(args, stdout=subprocess.PIPE,  # Capture standard output
                              stderr=subprocess.PIPE,  # Capture standard error
                              text=True,
                              cwd=cwd,
                              shell=shell) as process:

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
                            logger.info(stdout_line.rstrip('\n'))
                            stdout += stdout_line
                    elif process.stderr and fd == process.stderr.fileno():
                        stderr_line = process.stderr.readline()
                        if stderr_line:
                            logger.error(stderr_line.rstrip('\n'))
                            stderr += stderr_line

                # Check if the process has finished
                if process.poll() is not None:
                    process_finished = True

            exit_code = process.returncode  # Get the exit code

            command_not_found = (exit_code == 127) or ("command not found" in stderr.lower())

    except FileNotFoundError as excpt:
        logger.error(f"Command \"{call}\" not found: {excpt}")
        stdout, stderr = "", "Command not found"
        exit_code = 127
        command_not_found = True

    return stdout, stderr, exit_code, command_not_found

