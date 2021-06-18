# Deployment on RPI

## Raspian setup

For RPI 3B+, download a Raspian Image for [Raspberry Pi OS with desktop ](https://www.raspberrypi.org/software/operating-systems/), e.g. 2020-12-02-raspios-buster-armhf. Burn it into an SD card, e.g. with [balena Etcher](https://www.balena.io/etcher/)

To setup networking:

1. Change password with `passwd`. Ver RPI_temperature_metrics en person_SBC.
2. Config wifi with UI.
3. Enable sshd with `sudo raspi-config`.
4. Enable multicast DNS (mDNS) so we can usa a domain name from our local network instead of an actual IP, as that is changing. For that just change the hostname with `sudo raspi-config` and System Options -> Hostname to `temperature.local`, save and reboot. Now we can ssh to the host as `ssh pi@temperature.local` 
5. Setup passwordless ssh with `ssh-copy-id -i ~/.ssh/id_rsa pi@temperature.local`, and adding the following to ~/.ssh/config in my laptop

      ```
      Host temperature
      HostName temperature.local
      User pi
      IdentityFile ~/.ssh/id_rsa
      ```

      Now we can login with `ssh temperature`. Now disable ssh with password editing `/etc/ssh/sshd_config` to have `PasswordAuthentication no` and restarting the daemon with `sudo systemctl restart ssh` 

Using the following RPI machine:

```bash
pi@temperature:~ $ uname -a
Linux temperature.local 5.4.79-v7+ #1373 SMP Mon Nov 23 13:22:33 GMT 2020 armv7l GNU/Linux
pi@temperature:~ $ arch
armv7l
pi@temperature:~ $ lscpu 
Architecture:        armv7l
Byte Order:          Little Endian
CPU(s):              4
On-line CPU(s) list: 0-3
Thread(s) per core:  1
Core(s) per socket:  4
Socket(s):           1
Vendor ID:           ARM
Model:               4
Model name:          Cortex-A53
Stepping:            r0p4
CPU max MHz:         1400,0000
CPU min MHz:         600,0000
BogoMIPS:            51.20
Flags:               half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt vfpd32 lpae evtstrm crc32
pi@temperature:~ $
```

### USB serial access

Using a JBTek USB TTL cable, and following [these instructions](https://www.adafruit.com/product/954) and [this tutorial](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-5-using-a-console-cable). Steps:

- Install client drivers: For Linux we don't need to install any driver, see those instructions for other OS. 
- Enable serial console on the RPI: TODO

TODO as local wifi access is enough for now

## GrovePi+ setup

Following the README from https://github.com/DexterInd/GrovePi, with some additions. __From the RPI__:

```bash
curl -kL dexterindustries.com/update_grovepi | bash

# To update the firmware in the future 
cd /home/pi/Dexter/GrovePi/Firmware
bash firmware_update.sh
```

Now to test this works, connect the temperature and humidity sensor to port D7. Then use the following modification of the [temperature sensor demo](https://github.com/DexterInd/GrovePi/blob/master/Projects/Home_Weather_Display/Home_Weather_Display.py) from a Python shell. Note the installation above installed the grove pi python libraries system wide, at least for the default Python 2.7:

```python
from grovepi import *
import time

dht_sensor_port = 7 # connect the DHt sensor to port 7
dht_sensor_type = 0 # use 0 for the blue-colored sensor and 1 for the white-colored sensor

def measure_n_times(n, sleep_time=1):
    for _ in xrange(n):
        (temp, hum) = dht(dht_sensor_port,dht_sensor_type)
        print("temperature={temp}, humidity={hum}".format(temp=temp, hum=hum))
        time.sleep(sleep_time)

measure_n_times(4)
```

This often returns NaN when you measure too fast

```python 
>>> measure_n_times(4, sleep_time=0.5)
temperature=27.0, humidity=48.0
temperature=nan, humidity=nan
temperature=26.0, humidity=48.0
temperature=nan, humidity=nan
>>> measure_n_times(4, sleep_time=1)
temperature=26.0, humidity=48.0
temperature=26.0, humidity=48.0
temperature=26.0, humidity=48.0
temperature=26.0, humidity=48.0
>>> 
```

TODO:

- Install Grove client C++ libraries, and access temperature and humidity measurements from C++
