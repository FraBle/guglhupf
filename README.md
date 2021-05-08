<p align="center">
  <img src="docs/guglhupf.jpg" alt="guglhupf" width="50%"/></br>
  Photo from <a href="https://pxhere.com/en/photo/1489677" target="_blank">PxHere</a>
</p>

<h1 align="center">guglhupf</h1>

<div align="center">

[![Codacy][codacy-badge]][codacy-url]
[![Code Climate][code-climate-badge]][code-climate-url]
[![CodeFactor][codefactor-badge]][codefactor-url]
[![lgtm][lgtm-badge]][lgtm-url]
[![SonarQube][sonarqube-badge]][sonarqube-url]

</div>

`guglhupf` is an extensible, distributed camera feed processing platform powered by Raspberry Pis and a comprehensive stack of open source tools, libraries, and frameworks. It has been developed targetting the use case of dashcams but can also be customized to serve other camera-based scenarios such as home security.  
The platform consists of one controller acting as a central hub and multiple agents, each serving a camera video feed.

## Controller

The controller hosts the main components of the platform:

- the `guglhupf` Python backend based on [`FastApi`](https://fastapi.tiangolo.com/)
- the [`zuckerguss`](https://github.com/FraBle/zuckerguss) frontend based on [`React`](https://reactjs.org/)
- the `nginx` reverse proxy to serve as entry point
- the `nfs`-managed storage for video recordings and gps location sharing
- the `gps-sync` command and cronjob to continously update location data from [`gpsd`](https://gpsd.gitlab.io/gpsd/)
- the `guglhupf-sync` command and cronjob to upload recordings to Google Drive using [`drive`](https://github.com/odeke-em/drive)

### Controller Setup Guides

#### Setting up `nginx` as reverse proxy

1. Install `nginx` using `dietpi-software`.

2. Create a `guglhupf.conf` nginx config file.

    ```bash
    sudo nano /etc/nginx/conf.d/guglhupf.conf`
    ```

    > The content of [`guglhupf.conf`](https://github.com/FraBle/guglhupf/blob/main/resources/controller/guglhupf.conf) can be found in the `resources` folder.

3. Disable the default `nginx` config.

    ```bash
    sudo unlink /etc/nginx/sites-enabled/default
    ```

4. Restart the nginx service.

    ```bash
    sudo systemctl restart nginx.service
    ```

## Agents

The Camera Agents use the [Video4Linux V4L2](https://www.kernel.org/doc/html/latest/driver-api/media/v4l2-core.html) API to process the video feed from the [Raspberry Pi Camera Module](https://www.raspberrypi.org/products/camera-module-v2/).

### Agent Setup Guides

#### Preparing a Raspberry Pi as Camera Agent

These steps have been verified using a Raspberry Pi 3 Model B+ but should be the same on newer models like the Raspberry Pi 4 Model B.
This tutorial is based on [DietPi](https://dietpi.com/), but the steps should be similar on Raspberry Pi OS and other Raspberry Pi OS-based systems.
Your Raspberry Pi should have the [Camera Module](https://www.raspberrypi.org/products/camera-module-v2/) connected.

1. Follow the [DietPi instructions](https://dietpi.com/docs/install/) to download the latest DietPi release and flash it to an SD card with balenaEtcher.

    > Stop after step "2. Flash the DietPi image" since we will prepare a
    > headless install and need to change some files before the first boot.

2. Reinsert/mount the SD card (typically called `boot`) once more after balenaEtcher is finished.
3. Open `boot/dietpi.txt` in your favorite editor/IDE and update the settings for a headless boot.

    > An [example `dietpi.txt`](https://github.com/FraBle/guglhupf/blob/main/resources/agent/dietpi.txt) can be found in the `resources` folder.  
    > Some of your settings might differ (e.g., regional settings)

    Overview of changed values:

    ```diff
    -AUTO_SETUP_ACCEPT_LICENSE=0
    +AUTO_SETUP_ACCEPT_LICENSE=1

    -AUTO_SETUP_LOCALE=C.UTF-8
    +AUTO_SETUP_LOCALE=en_US.UTF-8

    -AUTO_SETUP_KEYBOARD_LAYOUT=gb
    +AUTO_SETUP_KEYBOARD_LAYOUT=us

    -AUTO_SETUP_TIMEZONE=Europe/London
    +AUTO_SETUP_TIMEZONE=America/Los_Angeles
    
    -AUTO_SETUP_NET_WIFI_ENABLED=0
    +AUTO_SETUP_NET_WIFI_ENABLED=1

    -AUTO_SETUP_NET_WIFI_COUNTRY_CODE=GB
    +AUTO_SETUP_NET_WIFI_COUNTRY_CODE=US

    -AUTO_SETUP_NET_HOSTNAME=DietPi
    +AUTO_SETUP_NET_HOSTNAME=<custom hostname>

    -AUTO_SETUP_HEADLESS=0
    +AUTO_SETUP_HEADLESS=1

    -AUTO_SETUP_AUTOSTART_TARGET_INDEX=0
    +AUTO_SETUP_AUTOSTART_TARGET_INDEX=7

    -AUTO_SETUP_AUTOMATED=0
    +AUTO_SETUP_AUTOMATED=1

    -AUTO_SETUP_GLOBAL_PASSWORD=dietpi
    +AUTO_SETUP_GLOBAL_PASSWORD=<custom password>

    -#AUTO_SETUP_INSTALL_SOFTWARE_ID=23
    +AUTO_SETUP_INSTALL_SOFTWARE_ID=0   #OpenSSH Client
    +AUTO_SETUP_INSTALL_SOFTWARE_ID=7   #FFmpeg
    +AUTO_SETUP_INSTALL_SOFTWARE_ID=16  #Build-Essentials
    +AUTO_SETUP_INSTALL_SOFTWARE_ID=17  #Git
    +AUTO_SETUP_INSTALL_SOFTWARE_ID=103 #DietPi-RAMlog
    +AUTO_SETUP_INSTALL_SOFTWARE_ID=104 #Dropbear
    +AUTO_SETUP_INSTALL_SOFTWARE_ID=110 #NFS Client

    -SURVEY_OPTED_IN=-1
    +SURVEY_OPTED_IN=0

    -CONFIG_BOOT_WAIT_FOR_NETWORK=1
    +CONFIG_BOOT_WAIT_FOR_NETWORK=2
    ```

    Next, update `boot/dietpi-wifi.txt` by setting `aWIFI_SSID[0]` to your WiFi
    SSID and `aWIFI_KEY[0]` to your WiFi password.

4. Unmount the SD card, insert it into the Raspberry Pi, and power it on.

    > It might take a moment to fully boot up and allow an SSH session since it
    > will install all listed software on the first boot.

5. Check your WiFi router for connected devices to retrieve the IP of the Raspberry Pi.
6. Open an SSH session to the Raspberry Pi: `ssh root@<rpi-ip>`

    > All upcoming steps are executed on the Raspberry Pi.  
    > You can also use `ssh-copy-id` to install your public SSH key as an
    > authorized key on the Raspberry Pi to avoid typing your password for
    > new SSH sessions.

    ```bash
    ssh-copy-id root@<rpi-ip>
    ssh-copy-id dietpi@<rpi-ip>
    ```

7. Run `dietpi-config` to enable the camera and adjust the GPU memory.

    > Under `1  : Display Options`, turn on  `8  : RPi Camera` and adjust the
    > `2  : GPU/RAM Memory Split`, e.g. to `256 : General Gaming`.

8. Mount the NFS directory of the guglhupf controller to using `dietpi-drive_manager`.

    > Select `Add network drive`, then `NFS`, enter the guglhupf controller IP,
    > and give it a unique folder name (e.g., `recordings`).

9. Follow the other steps below to set up...

    - [the open-source `bcm2835-v4l2` camera driver](#set-up-bcm2835-v4l2-camera-driver)
    - [the camera utils `v4l-utils` for controlling rotation and resolution](#install-v4l-utils-and-set-up-camera-automatically-with-v4l2-ctl)
    - [a loopback device using `v4l2loopback` to mirror `dev/video0` for multi-client access](#install-and-set-up-v4l2loopback-for-devvideo1-loopback-device)
    - [a mirror from `dev/video0` to `dev/video1` using FFmpeg](#set-up-ffmpeg-to-mirror-devvideo0-to-devvideo1)
    - [a live video stream with `webrtc-streamer`](#install-and-set-up-webrtc-streamer-for-live-stream-of-camera-feed)
    - [a recording service with FFmpeg](#set-up-ffmpeg-to-record-camera-feed-in-segments-to-file)

#### Set up `bcm2835-v4l2` camera driver

1. Add `bcm2835-v4l2` to `/etc/modules-load.d/` (kernel modules to load at boot time).

    `sudo nano /etc/modules-load.d/bcm2835-v4l2.conf`:

    ```plain
    bcm2835-v4l2
    ```

2. Reboot and check that `/dev/video0` exists.

#### Install `v4l-utils` and set up camera automatically with `v4l2-ctl`

1. Install `v4l-utils` for debugging & control commands.

    ```bash
    sudo apt install -y v4l-utils
    ```

    Example command "rotatation of camera":

    ```bash
    v4l2-ctl --set-ctrl=rotate=90
    ```

    Example command  "list video devices":

    ```bash
    v4l2-ctl --list-devices
    ```

    Example command  "list video device details":

    ```bash
    v4l2-ctl --device=/dev/video0 --all
    ```

2. Add `v4l2-ctl` command to system boot via `udev` subsystem.

    `sudo nano /etc/udev/rules.d/99-local-webcam.rules`:

    ```plain
    SUBSYSTEM=="video4linux", PROGRAM="/usr/bin/v4l2-ctl --set-fmt-video=width=640,height=480 --set-ctrl=rotate=90"
    ```

    > Adjust the settings according to your needs (e.g., camera mounting
    > rotation).

3. Reboot and check updated settings with `v4l2-ctl --device=/dev/video0 --all`.

#### Install and set up `v4l2loopback` for `dev/video1` loopback device

1. Install [`v4l2loopback`](https://github.com/umlaeute/v4l2loopback).

    ```bash
    sudo apt install -y linux-headers v4l2loopback-dkms v4l2loopback-utils
    ```

2. Add `v4l2loopback` to `/etc/modules-load.d/` (kernel modules to load at boot time).

    `sudo nano /etc/modules-load.d/v4l2loopback.conf`:

    ```plain
    v4l2loopback
    ```

3. Set parameters for `v4l2loopback` by creating a config file:

    > [Parameters for `v4l2loopback`](https://github.com/umlaeute/v4l2loopback#options)

    `sudo nano /etc/modprobe.d/v4l2loopback.conf`:

    ```plain
    options v4l2loopback devices=1
    options v4l2loopback card_label="front"
    ```

    > Adjust the label to your preference. For guglhupf, there are two
    > Raspberry Pis acting as Camera Agents with the camera labels `front` and
    > `back`.

4. Reboot and check that `/dev/video1` exists.

#### Set up FFmpeg to mirror `/dev/video0` to `/dev/video1`

> Based on [this](https://unix.stackexchange.com/a/186903) StackOverflow answer.

1. Add video devices to `systemd` via `udev` subsystem.

    `sudo nano /lib/udev/rules.d/99-systemd.rules`, before `LABEL="systemd_end"`:

    ```plain
    # Systemd events for video devices
    KERNEL=="video0", SYMLINK="video0", TAG+="systemd"
    KERNEL=="video1", SYMLINK="video1", TAG+="systemd"
    ```

2. Reboot to activate new `udev` rules.

3. Register `video-mirror` service with `systemd`.

    `sudo nano /lib/systemd/system/video-mirror.service`:

    ```ini
    [Unit]
    Description=Mirror /dev/video0 to /dev/video1 with FFmpeg
    BindsTo=dev-video0.device dev-video1.device
    After=dev-video0.device dev-video1.device

    [Service]
    Type=simple
    ExecStart=ffmpeg -f v4l2 -i /dev/video0 -codec copy -f v4l2 /dev/video1
    Restart=always
    RestartSec=1
    StartLimitInterval=0

    [Install]
    WantedBy=multi-user.target
    ```

4. Enable and start `video-mirror` service in `systemd`.

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable video-mirror.service
    sudo systemctl start video-mirror.service
    ```

#### Install and set up `WebRTC-streamer` for live stream of camera feed

1. Retrieve the [latest `armv7l-Release`](https://github.com/mpromonet/webrtc-streamer/releases).

    ```bash
    cd /tmp
    wget https://github.com/mpromonet/webrtc-streamer/releases/download/v0.6.3/webrtc-streamer-v0.6.3-Linux-armv7l-Release.tar.gz
    tar -zxf webrtc-streamer-v0.6.3-Linux-armv7l-Release.tar.gz
    ```

2. Move `webrtc-streamer` binary.

    ```bash
    cd /tmp/webrtc-streamer-v0.6.3-Linux-armv7l-Release
    sudo mv ./webrtc-streamer /usr/local/bin/webrtc-streamer
    ```

3. Verify availability of  `webrtc-streamer` command.

    ```bash
    webrtc-streamer --help
    ```

4. Register `webrtc-streamer` service with `systemd`.

    `sudo nano /lib/systemd/system/webrtc-streamer.service`:

    ```ini
    [Unit]
    Description=WebRTC-streamer
    After=video-mirror.service

    [Service]
    Type=simple
    ExecStart=webrtc-streamer
    Restart=always
    RestartSec=1
    StartLimitInterval=0

    [Install]
    WantedBy=multi-user.target
    ```

5. Enable and start `webrtc-streamer` service in `systemd`.

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable webrtc-streamer.service
    sudo systemctl start webrtc-streamer.service
    ```

6. Validate WebRTC stream using a [simple HTML page](https://github.com/FraBle/guglhupf/blob/main/resources/agent/webrtc-test.html)

#### Set up FFmpeg to record camera feed in segments to file

1. Add monospaced `SourceCodePro` font.

    ```bash
    cd /tmp
    wget https://fonts.google.com/download?family=Source%20Code%20Pro -O SourceCodePro.zip
    unzip SourceCodePro.zip -d /tmp/SourceCodePro
    sudo mv /tmp/SourceCodePro /usr/share/fonts/truetype/
    ```

2. Add new `video-recording` command (bash script wrapping `ffmpeg` with parameters).

    `sudo nano /usr/local/bin/video-recording`:

    ```bash
    #!/bin/bash

    ffmpeg \
    -f v4l2 \
    -video_size 640x480 \
    -i /dev/video1 \
    -map 0 \
    -segment_time 300 \
    -g 30 \
    -sc_threshold 0 \
    -force_key_frames "expr:gte(t,n_forced*300)" \
    -f segment \
    -reset_timestamps 1 \
    -strftime 1 \
    -vf "[in]\
    drawtext=\
    fontfile=/usr/share/fonts/truetype/SourceCodePro/SourceCodePro-Regular.ttf: \
    textfile=/mnt/recordings/gps.txt: \
    reload=1: \
    x=10: \
    y=h-text_h-10: \
    fontsize=15: \
    fontcolor=black: \
    box=1: \
    boxcolor=white@0.5: \
    boxborderw=5,\
    drawtext=\
    fontfile=/usr/share/fonts/truetype/SourceCodePro/SourceCodePro-Regular.ttf: \
    text='%{localtime}': \
    x=w-text_w-10: \
    y=h-text_h-10: \
    fontsize=15: \
    fontcolor=black: \
    box=1: \
    boxcolor=white@0.5: \
    boxborderw=5
    [out]" \
    -c:v h264_omx \
    -pix_fmt yuv420p \
    /mnt/recordings/guglhupf/video_front_%Y-%m-%d_%H-%M-%S.mp4
    ```

    > A lot is going on here, and you might have to adjust a couple of settings
    > (e.g., the filename template string).  
    > FFmpeg reads from `/dev/video1` in a fixed resolution of 640x480. It
    > writes segments of the video feed to disk. Each segment is 5min (300sec),
    > with keyframes enforced at the same time mark to allow a smooth cutover.
    > It uses two `drawtext` filters: one to add GPS coordinates from a file
    > (`gps.txt`) to the lower-left corner and one to add timestamps to the
    > lower-right corner of every frame. It uses the hardware-accelerated
    > `h264_omx` codec and writes the output files to the configured NFS folder
    > `/mnt/recordings` with timestamps in the file name.

3. Give execution rights to the new `video-recording` command:

    ```bash
    sudo chmod +x /usr/local/bin/video-recording
    ```

4. Test `video-recording` command:

    ```bash
    video-recording
    ```

5. Register `video-recording` service with `systemd`.

    `sudo nano /lib/systemd/system/video-recording.service`:

    ```ini
    [Unit]
    Description=Video Recording with FFmpeg
    After=video-mirror.service

    [Service]
    Type=simple
    ExecStart=video-recording
    Restart=always
    RestartSec=1
    StartLimitInterval=0

    [Install]
    WantedBy=multi-user.target
    ```

6. Enable and start `video-recording` service in `systemd`.

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable video-recording.service
    sudo systemctl start video-recording.service
    ```

7. Use `htop` to verify that `video-recording` is running. You can also check the configured output folder, which should contain `.mp4` files now.

<!--
Badges
-->
[codacy-badge]:https://img.shields.io/codacy/grade/a6fe36617f1944b0b0da8d60a4c89d35?label=Codacy%20Grade&style=flat-square
[code-climate-badge]:https://img.shields.io/codeclimate/maintainability/FraBle/guglhupf?label=Code%20Climate%20Grade&style=flat-square
[codefactor-badge]:https://img.shields.io/codefactor/grade/github/FraBle/guglhupf/main?label=CodeFactor%20Grade&style=flat-square
[lgtm-badge]:https://img.shields.io/lgtm/grade/python/github/FraBle/guglhupf?label=lgtm%20Grade&style=flat-square
[sonarqube-badge]:https://img.shields.io/sonar/tech_debt/FraBle_guglhupf?label=Sonar%20Tech%20Debt&server=https%3A%2F%2Fsonarcloud.io&style=flat-square

<!--
Badge URLs
-->
[codacy-url]:https://app.codacy.com/gh/FraBle/guglhupf
[code-climate-url]:https://codeclimate.com/github/FraBle/guglhupf
[codefactor-url]:https://www.codefactor.io/repository/github/frable/guglhupf
[lgtm-url]:https://lgtm.com/projects/g/FraBle/guglhupf/
[sonarqube-url]:https://sonarcloud.io/dashboard?id=FraBle_guglhupf
