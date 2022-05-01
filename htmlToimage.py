#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from html2image import Html2Image
hti = Html2Image()

# Take the screenshot
hti.screenshot(url='http://localhost:8080/image.png', save_as='status.png', size=(600, 800))

# Convert to grayscale
os.system('convert status.png -type GrayScale -depth 8 -colors 256 status.png')

os.system('chmod 777 status.png')

# Copy image to apache dir
os.system('cp -p status.png /srv/http/status.png')