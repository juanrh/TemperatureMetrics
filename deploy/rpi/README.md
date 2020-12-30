# Deployment on RPI

## Raspian setup

For RPI 3B+, download a Raspian Image for [Raspberry Pi OS with desktop ](https://www.raspberrypi.org/software/operating-systems/), e.g. 2020-12-02-raspios-buster-armhf. Burn it into an SD card, e.g. with [balena Etcher](https://www.balena.io/etcher/)

Enable sshd with `sudo raspi-config`.

WIP local network static IP 192.168.1.4

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