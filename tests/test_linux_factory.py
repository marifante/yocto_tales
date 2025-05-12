import pytest
from unittest.mock import Mock, patch
from yoctales.cmd import CommandShell
from yoctales.linux_factory import LinuxImageInvoker


@pytest.fixture
def invoker():
    """ Fixture to create a LinuxImageInvoker instance. """
    return LinuxImageInvoker()


def test_add_command(invoker):
    """ Test the add_command method. """
    mock_command = Mock(spec=CommandShell)
    invoker.add_command(mock_command)
    assert mock_command in invoker.commands
    assert len(invoker.commands) == 1


def test_execute_all_success(invoker):
    """Test the execute_all method when all commands execute successfully."""
    mock_command1 = Mock(spec=CommandShell)
    mock_command2 = Mock(spec=CommandShell)
    invoker.add_command(mock_command1)
    invoker.add_command(mock_command2)

    invoker.execute_all()

    mock_command1.execute.assert_called_once()
    mock_command2.execute.assert_called_once()


@patch("yoctales.linux_factory.logger")
def test_execute_all_with_failure(mock_logger, invoker):
    """Test the execute_all method when a command fails."""
    mock_command1 = Mock(spec=CommandShell)
    mock_command2 = Mock(spec=CommandShell)
    mock_command1.execute.side_effect = Exception("Mocked failure")
    invoker.add_command(mock_command1)
    invoker.add_command(mock_command2)

    invoker.execute_all()

    mock_command1.execute.assert_called_once()
    mock_command2.execute.assert_not_called()
    mock_logger.error.assert_called_with("Command failed: Mocked failure")


def test_describe_plan(invoker):
    """Test the describe_plan method."""
    mock_command1 = Mock(spec=CommandShell)
    mock_command2 = Mock(spec=CommandShell)
    mock_command1.__str__ = Mock(return_value="Mock Command 1")
    mock_command2.__str__ = Mock(return_value="Mock Command 2")
    invoker.add_command(mock_command1)
    invoker.add_command(mock_command2)

    plan = invoker.describe_plan()

    expected_plan = "  0: Mock Command 1\n  1: Mock Command 2"
    assert plan == expected_plan
