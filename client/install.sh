sudo apt-get update
sudo apt-get install vim git openssh-server python3 python3-dev python3-pip -y

pip3 install picamera
pip3 install ntplib

sudo echo 'network={ \
    ssid="iptime" \
    key_mgmt=NONE \
}' >> /etc/wpa_supplicant/wpa_supplicant.conf

sudo reboot