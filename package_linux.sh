#!/bin/bash

clear

cp ./dist_linux/EPICpy ../dist2appimage/EPICpy
cd ../dist2appimage/

# ~/Applications/linuxdeployqt-continuous-x86_64.AppImage EPICpy -appimage
# ~/Applications/linuxdeployqt-continuous-x86_64.AppImage EPICpy -appimage -no-strip -always-overwrite
~/Applications/linuxdeployqt-continuous-x86_64.AppImage EPICpy -appimage -always-overwrite


