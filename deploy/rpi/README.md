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

### USB serial access

Using a JBTek USB TTL cable, and following [these instructions](https://www.adafruit.com/product/954) and [this tutorial](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-5-using-a-console-cable). Steps:

- Install client drivers: For Linux we don't need to install any driver, see those instructions for other OS. 
- Enable serial console on the RPI: TODO

TODO as local wifi access is enough for now

## GrovePi+ setup

TODO:

- Install Grove drivers on raspbian https://github.com/DexterInd/GrovePi
- Install Grove client libraries
- Check it works ok: hello world with led https://www.dexterindustries.com/GrovePi/projects-for-the-raspberry-pi/
- Wrap C client from Rust in LED hello world
- Access temperature mesaurements from Rust