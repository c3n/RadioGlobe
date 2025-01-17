#! /bin/sh
sudo apt install vlc pulseaudio python3-pip python3-smbus python3-dev python3-rpi.gpio python3-gpiozero
pip3 install https://github.com/pl31/python-liquidcrystal_i2c/archive/master.zip
pip3 install python-vlc
pip3 install spidev
pip3 install rpi_ws281x
sudo cp services/*.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl start radioglobe.service
sudo systemctl enable radioglobe.service
