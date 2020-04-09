sudo apt-get update
sudo apt-get upgrade -y

sudo apt install libhdf5-103 -y
sudo apt-get install -y libatlas-base-dev libjasper-dev libqtgui4 python3-pyqt5 libqt4-test
sudo apt-get install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev -y
sudo apt-get install -y libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran
wget https://www.python.org/ftp/python/3.7.7/Python-3.7.7.tar.xz
tar xf Python-3.7.7.tar.xz
cd Python-3.7.7
./configure --prefix=/usr/local/opt/python-3.7.7
make -j 4

sudo make altinstall
sudo ln -s /usr/local/opt/python-3.7.7/bin/pydoc3.7 /usr/bin/pydoc3.7
sudo ln -s /usr/local/opt/python-3.7.7/bin/python3.7 /usr/bin/python3.7
sudo ln -s /usr/local/opt/python-3.7.7/bin/python3.7m /usr/bin/python3.7m
sudo ln -s /usr/local/opt/python-3.7.7/bin/pyvenv-3.7 /usr/bin/pyvenv-3.7
sudo ln -s /usr/local/opt/python-3.7.7/bin/pip3.7 /usr/bin/pip3.7
alias python='/usr/bin/python3.7'
alias python3='/usr/bin/python3.7'
ls /usr/bin/python*
cd ..
sudo rm -r Python-3.7.7
rm Python-3.7.7.tar.xz
. ~/.bashrc

python -V

update-alternatives --config python
sudo pip3.7 install --upgrade pip
sudo apt-get install python3-opencv
sudo pip3.7 install -r ../client/requirements.txt

sudo echo '\ngpu_mem=256' >> /boot/config.txt

sudo echo '
country=US

network={
	ssid="iptime"
	psk="12341234"
}
' >> /etc/wpa_supplicant/wpa_supplicant.conf

sudo reboot

nohup /usr/bin/python3.7 /home/pi/cSync/client/main.py 1> /dev/null 2>&1 &