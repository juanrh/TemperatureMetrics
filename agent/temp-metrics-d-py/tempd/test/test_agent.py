"""
Test for the module tempd.agent
"""

# This check is incompatible with pytests conventions
# for fixtures
# pylint: disable=redefined-outer-name
import math
from unittest.mock import patch
from unittest.mock import Mock
import signal

import pytest

from tempd.agent import CloudwatchMeasurementRecorder, TempMeter
from tempd.agent import TempMeterConfig, TempMeasurement, ThreadDaemon


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
    """Create a daemon, using the real timer"""
    the_daemon = ThreadDaemon(daemon_frequency, action)
    yield the_daemon
    the_daemon.stop()

@pytest.fixture
def daemon_mock_timer(action, daemon_frequency, timer):
    """Create a daemon, using a mock for the timer"""
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


@pytest.fixture
def sensor():
    """Mock for the temp meter sensor"""
    return Mock()

@pytest.fixture
def meter_source():
    """Name of the source of the meter"""
    return "foo_source"

@pytest.fixture
def temp_meter_config(timer, sensor):
    """Create a test config using mocks for timer and sensor"""
    return TempMeterConfig(1, sensor, timer)

@pytest.fixture
def temp_meter(meter_source, temp_meter_config):
    """Create a temp meter"""
    return TempMeter(meter_source, temp_meter_config)

def test_meter_measure(meter_source, timer, sensor, temp_meter_config, temp_meter):
    """Check the meter uses the sensor correctly, uses the right timestamp,
    and retris nan measurements"""
    expected_epoch_secs = 10
    timer.time.return_value = 10 + 0.5
    expected_temp = 100.0
    expected_humidity = 200.1
    sensor.measure.side_effect = [(math.nan, math.nan), (expected_temp, expected_humidity)]

    measurement = temp_meter.measure()

    assert measurement.source == meter_source
    assert measurement.timestamp == expected_epoch_secs
    assert measurement.temperature == expected_temp
    assert measurement.humidity == expected_humidity
    timer.sleep.assert_called_once_with(temp_meter_config.retry_sleep_time)


@pytest.fixture
def cloudwatch():
    """Mock for the AWS cloudwatch client"""
    return Mock()

@pytest.fixture
def boto_session(cloudwatch):
    """Mock for the boto session"""
    session = Mock()
    session.client.return_value = cloudwatch
    return session

@pytest.fixture
def cw_namespace():
    """Cloudwach namespace for the CloudwatchMeasurementRecorder"""
    return "foo_namespace"

@pytest.fixture
def storage_resolution():
    """Storage resolution for the CloudwatchMeasurementRecorder"""
    return 12

@pytest.fixture
def cloudwatch_recorder(boto_session, cw_namespace, storage_resolution):
    """Create a CloudwatchMeasurementRecorder"""
    return CloudwatchMeasurementRecorder(boto_session, cw_namespace, storage_resolution)

def test_cloudwatch_recorder_record(cloudwatch, cw_namespace,
    storage_resolution, cloudwatch_recorder):
    """Check measurements are sent to cloudwatch as expected"""

    measurement = TempMeasurement('foo_source', 10, 20.1, 40.2)

    cloudwatch_recorder.record(measurement)

    def expected_metric(metric_name, value):
        return {
            'MetricName': metric_name,
            'Dimensions': [
                {
                    'Name': 'source',
                   'Value': measurement.source
                },
            ],
            'Timestamp': measurement.timestamp,
            'Value': value,
           'StorageResolution': storage_resolution
        }

    cloudwatch.put_metric_data.assert_called_once_with(Namespace=cw_namespace,
        MetricData=[
            expected_metric('temperature', measurement.temperature),
            expected_metric('humidity', measurement.humidity)
        ]
    )
