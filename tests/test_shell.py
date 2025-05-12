import pytest
import subprocess
from unittest.mock import patch, MagicMock
from yoctales.shell import execute_in_shell


@pytest.fixture
def mock_popen():
    with patch("yoctales.shell.subprocess.Popen") as mock:
        yield mock


@pytest.fixture
def mock_select():
    with patch("yoctales.shell.select.select") as mock:
        yield mock


@pytest.mark.parametrize(
    "mock_stdout_lines, expected_stdout, mock_stderr_lines, expected_stderr",
    [
        (["Single log line\n"], "Single log line\n", ["super duper stderr line!#@!#4d\n"], "super duper stderr line!#@!#4d\n"),
        (["First log line\n", "Second log line\n"], "First log line\nSecond log line\n", ["super duper stderr line!#@!#4d\n", "2144\n", "1555FA\n"], "super duper stderr line!#@!#4d\n2144\n1555FA\n"),
        ([""], "", ["super duper stderr line!#@!#4d\n", "2144\n", "1555FA\n"], "super duper stderr line!#@!#4d\n2144\n1555FA\n"),
        (["First log line\n", "Second log line\n"], "First log line\nSecond log line\n", [""], ""),
    ],
)
def test_execute_in_shell_normal_shell_false_one_iteration(mock_popen, mock_select, mock_stdout_lines, expected_stdout, mock_stderr_lines, expected_stderr):
    """Test normal execution with shell=False.

    Here, in the first iteration the process is already done.
    And we are testing multiple cases for stdout and stderr.
    """
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = mock_stdout_lines + [""] # add an empty line to simulate end of output
    mock_process.stderr.readline.side_effect = mock_stderr_lines + [""] # add an empty line to simulate end of error
    mock_process.poll.side_effect = [0] # end in the first iteration
    mock_process.returncode = 0
    mock_popen.return_value.__enter__.return_value = mock_process

    mock_select.return_value = ([mock_process.stdout.fileno(), mock_process.stderr.fileno()],
                                [],
                                [])

    stdout, stderr, exit_code, command_not_found = execute_in_shell(
        call="ls -l", cwd="/tmp", shell=False
    )

    mock_popen.assert_called_once_with(
        ["ls", "-l"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/tmp",
        shell=False,
    )
    assert stdout == expected_stdout
    assert stderr == expected_stderr
    assert exit_code == 0
    assert not command_not_found


@pytest.mark.parametrize(
    "mock_stdout_lines, expected_stdout, mock_stderr_lines, expected_stderr",
    [
        (["Single log line\n"], "Single log line\n", ["super duper stderr line!#@!#4d\n"], "super duper stderr line!#@!#4d\n"),
        (["First log line\n", "Second log line\n"], "First log line\nSecond log line\n", ["super duper stderr line!#@!#4d\n", "2144\n", "1555FA\n"], "super duper stderr line!#@!#4d\n2144\n1555FA\n"),
        ([""], "", ["super duper stderr line!#@!#4d\n", "2144\n", "1555FA\n"], "super duper stderr line!#@!#4d\n2144\n1555FA\n"),
        (["First log line\n", "Second log line\n"], "First log line\nSecond log line\n", [""], ""),
    ],
)
def test_execute_in_shell_normal_shell_true_one_iteration(mock_popen, mock_select, mock_stdout_lines, expected_stdout, mock_stderr_lines, expected_stderr):
    """Test normal execution with shell=True.

    Here, in the first iteration the process is already done.
    And we are testing multiple cases for stdout and stderr.
    """
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = mock_stdout_lines + [""] # add an empty line to simulate end of output
    mock_process.stderr.readline.side_effect = mock_stderr_lines + [""] # add an empty line to simulate end of error
    mock_process.poll.side_effect = [0] # end in the first iteration
    mock_process.returncode = 0
    mock_popen.return_value.__enter__.return_value = mock_process

    mock_select.return_value = ([mock_process.stdout.fileno(), mock_process.stderr.fileno()],
                                [],
                                [])

    stdout, stderr, exit_code, command_not_found = execute_in_shell(
        call="ls -l", cwd="/tmp", shell=True
    )

    mock_popen.assert_called_once_with(
        "ls -l",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/tmp",
        shell=True,
    )
    assert stdout == expected_stdout
    assert stderr == expected_stderr
    assert exit_code == 0
    assert not command_not_found



def test_execute_in_shell_normal_shell_false_two_iterations(mock_popen, mock_select):
    """Test normal execution with shell=False.

    Here, the process is ready in the second iteration.
    """
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = ["incredible first output line\n", "incredible second output line\n", "", "pepe\n", ""]
    mock_process.stderr.readline.side_effect = ["the worst error ever seen in the first line\n", "a minimal error log\n", "", "messi10\n", ""]
    mock_process.poll.side_effect = [None, 0] # end in the second iteration
    mock_process.returncode = 0
    mock_popen.return_value.__enter__.return_value = mock_process

    mock_select.return_value = ([mock_process.stdout.fileno(), mock_process.stderr.fileno()],
                                [],
                                [])

    stdout, stderr, exit_code, command_not_found = execute_in_shell(
        call="ls -l /tmp/super/path", cwd="/tmp", shell=False
    )

    mock_popen.assert_called_once_with(
        ["ls", "-l", "/tmp/super/path"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/tmp",
        shell=False,
    )
    assert stdout == "incredible first output line\nincredible second output line\npepe\n"
    assert stderr == "the worst error ever seen in the first line\na minimal error log\nmessi10\n"
    assert exit_code == 0
    assert not command_not_found


def test_execute_in_shell_file_not_found_shell_false(mock_popen):
    """Test FileNotFoundError with shell=False."""
    mock_popen.side_effect = FileNotFoundError

    stdout, stderr, exit_code, command_not_found = execute_in_shell(
        call="nonexistent-command", cwd="/tmp", shell=False
    )

    mock_popen.assert_called_once_with(
        ["nonexistent-command"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/tmp",
        shell=False,
    )
    assert stdout == ""
    assert stderr == "Command not found"
    assert exit_code == 127
    assert command_not_found


def test_execute_in_shell_file_not_found_shell_true(mock_popen):
    """Test FileNotFoundError with shell=True."""
    mock_popen.side_effect = FileNotFoundError

    stdout, stderr, exit_code, command_not_found = execute_in_shell(
        call="nonexistent-command", cwd="/tmp", shell=True
    )

    mock_popen.assert_called_once_with(
        "nonexistent-command",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/tmp",
        shell=True,
    )
    assert stdout == ""
    assert stderr == "Command not found"
    assert exit_code == 127
    assert command_not_found
