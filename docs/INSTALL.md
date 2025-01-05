# Installation Guide
This guide will help you set up the SimplicityPlayer on your Raspberry Pi. The
installation process is divided into several steps, each of which is detailed
below.

## Prerequisites
Before you start, make sure you have the following components ready:
- Raspberry Pi 3A+ (other models may work, but the software was tested on this
  model)
- InnoMaker HiFi DAC HAT (RPI-HIFI-DAC-PCM5122)
- RFID Reader (RC522)
- LCD1602 + LCD I2C Interface (PCF8574)
- Cherry MX Button with a 4k7 Ohm Resistor

## Step 1: Prepare the Raspberry Pi
1. Install Raspberry Pi OS Lite on your Raspberry Pi. You can find the official
   installation guide [here](https://www.raspberrypi.org/documentation/installation/installing-images/).
2. Set up your Raspberry Pi, connect it to the network and connect to it via
   SSH.
3. Update the system by running the following commands:
   ```bash
   sudo apt update
   sudo apt upgrade
   ```
4. Enable the I2C & SPI interface by running:
   ```bash
   sudo raspi-config
   ```
   - Select `3 Interfacing Options`.
   - Select `I4 SPI`.
   - `Would you like the SPI interface to be enabled?` -> `Yes`
   - The SPI interface is now enabled.
   - Select `3 Interfacing Options`.
   - Select `I5 I2C`.
   - `Would you like the ARM I2C interface to be enabled?` -> `Yes`
   - The ARM I2C interface is now enabled.
   - Select `Finish`.
   
## Step 2: Set up the Audio Output
1. Connect the InnoMaker HiFi DAC HAT to your Raspberry Pi (only when the
   Raspberry Pi is powered off!)
2. Edit the `/boot/firmware/config.txt` file by running:
   ```bash
   sudo nano /boot/firmware/config.txt
   ```
3. Add the following lines to the end of the file:
   ```
   dtoverlay=allo-boss-dac-pcm512x-audio
   ```
4. Save the file by pressing `Ctrl + X`, then `Y`, and finally `Enter`.
5. Reboot your Raspberry Pi by running:
   ```bash
   sudo reboot
   ```

## Step 3: Set the default audio output
1. Check the audio output devices by running:
   ```bash
   aplay -l
   ```
2. Find the device that corresponds to the InnoMaker HiFi DAC HAT. It should
   look similar to this:
   ```
   card 2: sndrpihifiberry [snd_rpi_hifiberry_dac], device 0: HifiBerry DAC HiFi pcm512x-hifi-0 []
   Subdevices: 1/1
   Subdevice #0: subdevice #0
   ```
3. Edit the `/etc/asound.conf` file by running:
   ```bash
   sudo nano /etc/asound.conf
   ```
4. Insert the following lines to the file:
   ```
   pcm.!default {
       type hw
       card 2
   }
   ctl.!default {
       type hw
       card 2
   }
   ```
   change the `card 2` to the card number you found in step 2.
5. Save the file by pressing `Ctrl + X`, then `Y`, and finally `Enter`.
6. Reboot your Raspberry Pi by running:
   ```bash
   sudo reboot
   ```
7. Test the audio output by running:
   ```bash
   speaker-test -c2 -t wav
   ```
   You should hear a voice saying "Front Left" and "Front Right" from your
   speakers.

## Step 4: Install and configure MPD
1. Install MPD by running:
   ```bash
   sudo apt install alsa-utils mpd
   ```
2. Edit the `/etc/mpd.conf` file by running:
   ```bash
   sudo nano /etc/mpd.conf
   ```
3. Add the following lines to the end of the file:
   ```
   audio_output {
       type "alsa"
       name "RPI-HIFI-DAC-PCM5122"
       device "hw:2,0"
       mixer_control   "Analogue"
   }
   ```
   change the `device "hw:2,0"` to the device number you found in step 2.
4. Save the file by pressing `Ctrl + X`, then `Y`, and finally `Enter`.
5. Enable and restart MPD service by running:
   ```bash
   sudo systemctl enable mpd
   sudo systemctl restart mpd
   ```
## Step 5: Install automount for USB drives
1. Install the required packages by running:
   ```bash
   sudo apt install udevil
   ```
2. Create a new file by running:
   ```bash
   sudo nano /etc/systemd/system/devmon.servic
   ```
3. Insert the following lines to the file:
   ```
   [Unit]
   Description=Automount USB drives
   After=network.target
    
   [Service]
   Type=simple
   User=pi
   Restart=on-abort
   ExecStart=/usr/bin/devmon
    
   [Install]
   WantedBy=multi-user.target
   ```
4. Save the file by pressing `Ctrl + X`, then `Y`, and finally `Enter`.
5. Enable and start the service by running:
   ```bash
   sudo systemctl enable devmon
   sudo systemctl start devmon
   ```

## Step 6: Install the SimplicityPlayer
1. Install the required packages by running:
   ```bash
   sudo apt install python3-virtualenv git
   ```
2. Clone the repository by running:
   ```bash
   cd ~
   git clone https://github.com/meteyou/SimplicityPlayer.git
   ```
3. Create a new virtual environment by running:
   ```bash
   cd ~
   virtualenv -p python3 ./SimplicityPlayer-env
   ./SimplicityPlayer-env/bin/pip install -r ./SimplicityPlayer/requirements.txt
   ```
4. Copy config.ini.example to config.ini by running:
   ```bash
   cp ~/SimplicityPlayer/config.ini.example ~/SimplicityPlayer/config.ini
   ```
5. Copy the systemd service file by running:
   ```bash
   sudo cp ~/SimplicityPlayer/SimplicityPlayer.service /etc/systemd/system/
   ```
6. Enable and start the service by running:
   ```bash
   sudo systemctl enable SimplicityPlayer
   sudo systemctl start SimplicityPlayer
   ```
