sudo apt-get update
sudo apt-get install vim git openssh-server python3 python3-dev python3-pip -y
sudo apt-get install python3.7 -y

sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2

sudo update-alternatives --config python3
# type 2

pip3 install picamera
pip3 install ntplib

sudo echo 'network={ \
    ssid="iptime" \
    key_mgmt=NONE \
}' >> /etc/wpa_supplicant/wpa_supplicant.conf

sudo reboot