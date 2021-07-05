"""
Test for the module tempd.agent
"""

# This check is incompatible with pytests conventions
# for fixtures
# pylint: disable=redefined-outer-name
from unittest.mock import patch
from unittest.mock import Mock
import signal

import pytest

from tempd.agent import ThreadDaemon


@pytest.fixture
def action():
    """Mock for the daemon action"""
    return Mock()

@pytest.fixture
def daemon_frequency():
    """Frequency used for the daemon action"""
    return 10.0

@pytest.fixture
def timer():
    """Mock for the daemon timer"""
    return Mock()

@pytest.fixture
def daemon(action, daemon_frequency):
    """Mock for the daemon, using the real timer"""
    the_daemon = ThreadDaemon(daemon_frequency, action)
    yield the_daemon
    the_daemon.stop()

@pytest.fixture
def daemon_mock_timer(action, daemon_frequency, timer):
    """Mock for the daemon, using a mock for the timer"""
    the_daemon = ThreadDaemon(daemon_frequency, action, timer)
    yield the_daemon
    the_daemon.stop()


@patch('signal.signal')
def test_start_registers_signint_to_stop(signal_signal, daemon):
    """
    Check that a signal handler is registered to stop the daemon
    on SIGINT
    """
    # Spying with Moch(wrap=...) doesn't really work because on a method
    # call on the spy we have self pointing to the real object, not the spy
    # daemon_spy = Mock(wraps=self.daemon)
    # This makes things worse becase then self in the ThreadDaemon methods
    # is not properly duck typing
    # ThreadDaemon.start(daemon_spy, blocking=False)
    # So the strategy here is checking the "running" property, and not count
    # on spies
    daemon.start(blocking=False)
    signal_args, _signal_resul = signal_signal.call_args
    signal_arg_signalnum, signal_arg_handler = signal_args
    # The next two lines are equivalent
    # signal_signal.assert_called_with(signal.SIGINT, ANY)
    assert signal_arg_signalnum == signal.SIGINT
    assert daemon.running
    signal_arg_handler(None, None)
    daemon.wait_for_completion(0.5)
    assert not daemon.running

def test_daemon_runs_starts_with_action(action, daemon_frequency, daemon):
    """Check that the daemon runs the action immediately after starting"""
    action.side_effect = daemon.stop

    daemon.start(blocking=False)

    daemon.wait_for_completion(timeout=2*daemon_frequency)
    assert not daemon.running
    action.assert_called_once()

def test_daemon_runs_action_at_expected_frequency(action, daemon_frequency,
    timer, daemon_mock_timer):
    """Check that the daemon runs the action with the specified frequency
     (at least for the first cycle)"""
    daemon = daemon_mock_timer
    timer.time.side_effect = [0, daemon_frequency+1]
    action.side_effect = daemon.stop

    daemon.start(blocking=False)

    daemon.wait_for_completion(timeout=2*daemon_frequency)
    assert not daemon.running
    action.assert_called_once()

def test_daemon_keeps_working_on_action_exception(action, daemon):
    """Check the daemon keeps running even when the action raises
    an exception"""
    def raise_exception():
        raise RuntimeError("Forcing a runtime error")
    action.side_effect = raise_exception

    daemon.start(blocking=False)

    # need to wait to give time for the exception to raise
    # in the thread
    daemon.wait_for_completion(1)
    assert daemon.running
