sudo apt-get update
sudo apt-get upgrade -y

sudo apt-get install vim git openssh-server python3 python3-dev python3-pip build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev -y
sudo apt-get install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev -y
wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tar.xz
tar xf Python-3.7.0.tar.xz
cd Python-3.7.0
./configure --prefix=/usr/local/opt/python-3.7.0
make -j 4

sudo make altinstall
sudo ln -s /usr/local/opt/python-3.7.0/bin/pydoc3.7 /usr/bin/pydoc3.7
sudo ln -s /usr/local/opt/python-3.7.0/bin/python3.7 /usr/bin/python3.7
sudo ln -s /usr/local/opt/python-3.7.0/bin/python3.7m /usr/bin/python3.7m
sudo ln -s /usr/local/opt/python-3.7.0/bin/pyvenv-3.7 /usr/bin/pyvenv-3.7
sudo ln -s /usr/local/opt/python-3.7.0/bin/pip3.7 /usr/bin/pip3.7
alias python='/usr/bin/python3.7'
alias python3='/usr/bin/python3.7'
ls /usr/bin/python*
cd ..
sudo rm -r Python-3.7.0
rm Python-3.7.0.tar.xz
. ~/.bashrc

python -V

update-alternatives --config python

sudo pip3.7 install --upgrade pip
sudo pip3.7 install picamera
sudo pip3.7 install ntplib
sudo pip3.7 install RPi.GPIO

sudo echo '\ngpu_mem=256' >> /boot/config.txt

sudo echo '
country=US

network={
	ssid="iptime"
	psk="12341234"
}
' >> /etc/wpa_supplicant/wpa_supplicant.conf

sudo reboot