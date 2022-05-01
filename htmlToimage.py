#!/usr/bin/python
# -*- coding: utf-8 -*-
from html2image import Html2Image
hti = Html2Image()

hti.screenshot(url='http://localhost:8080/data.json', save_as='status.png', size=(600, 800))