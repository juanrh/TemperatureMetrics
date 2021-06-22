"""
Entry point for the temperature measurement agent

NOT following https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html,
but this is not a package utils script, but an entry point
for deployment
"""

from tempd.agent import Dht11TempMeter

def main():
    """Agent's entry point"""
    # TODO: parse init args
    meter = Dht11TempMeter("FIXME")
    print(f"Measurement: {meter.measure()}")

if __name__ == '__main__':
    main()
