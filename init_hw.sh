#!/bin/sh
I=eth0
echo 7 > /proc/sys/kernel/printk
modprobe -r nvhost_vi
modprobe soc_camera
insmod /home/ubuntu/ov4682.ko
modprobe tegra_camera
dmesg | tail

ifconfig $I up
dhclient $I
