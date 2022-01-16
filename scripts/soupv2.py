#!/usr/local/bin/python3
import os
import subprocess
import json
import time
import cv2
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from random import randrange
import numpy as np
import io
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from statistics import mean

def clear_images():
    '''
    Clears the wallpaper directory of all old jpgs 
    '''
    
    os.system("rm /Users/jacobl/wallpaper/*.jpg")

def get_monitor_count(resolutions,displays = {}):
    nth = {
        0: "first",
        1: "second",
        2: "third",
        3: "fourth",
        4: "fifth",
    }
    resolutions = [x.strip() for x in resolutions if x]
    for ii,monitor in enumerate(resolutions):
        displays[nth[ii]] = " ".join(monitor.replace('Resolution: ','').split(' ')[0:3])
    return displays

def get_monitor_resolutions(displays = {}):
    resolutions = os.popen('system_profiler SPDisplaysDataType | grep Resolution').read().split('\n')
    displays = get_monitor_count(resolutions,displays)
    return displays

def get_dates(delta):
    '''
    The site uses this URL to host the https://apod.nasa.gov/apod/image/2201/PIA19048europa.jpg, so we need to calculate the date in YMd format.
    '''
    today = datetime.today() - timedelta(days=delta)
    date = today.strftime('%y%m%d')
    return date

def find_image(site):
    """
    God bless this library
    """
    soup = BeautifulSoup(requests.get(site).text, 'html.parser')
    img_tag = soup.find('img')
    img_url = img_tag.get('src')
    description = soup.find_all('b')[0].text
    return img_url,description

def get_opencv_img_from_buffer(buffer):
    thing = np.asarray(bytearray(buffer.read()), dtype="uint8")
    return thing

def make_request(url):
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504 ])
    s.mount('http://', HTTPAdapter(max_retries=retries))
    response = s.get(url, stream=True)
    return response

def get_image(img_dir,site,date):
    '''
    Gets the space photo from the NASA site
    '''
    img_url = f"{site.replace(f'ap{date}.html','')}{img_dir}"
    space_photo = make_request(img_url).content
    
    space_photo = io.BytesIO(space_photo)
    space_photo.decode_content = True
    image = np.asarray(bytearray(space_photo.read()), dtype="uint8")
    return image

def up_scale(space_photo,date,description,resolution):
    '''
    Uses opencv to upscale the image to and write their description
    '''
    img = cv2.imdecode(space_photo, cv2.IMREAD_COLOR)

    res = [int(resolution.split('x')[0].strip()),int(resolution.split('x')[1].strip())]
    scale_percent = 0.5*mean(res)
    if res[0]>res[1]:
       img = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE)
    width = int(res[0] * scale_percent / 100)
    height = int(res[1] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_LINEAR)
    '''
    textX = mean(resized.shape) - (len(description) / 2)
    textY = mean(resized.shape) - (len(description) / 2)
    org = (int(textX), int(textY))
    cv2.putText(resized, description, org,cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
    '''
    cv2.imwrite(f'/Users/jacobl/wallpaper/{date}_up.jpg',resized) 

def main():
    clear_images()
    displays = get_monitor_resolutions()
    for display,resolution in displays.items():
        x = randrange(0,2000)
        date = get_dates(x)
        site = f'https://apod.nasa.gov/apod/ap{date}.html'
        img_url,description = find_image(site)
        space_photo = get_image(img_url,site,date)
        up_scale(space_photo,date,description,resolution)
        time.sleep(.5)
        os.system(f"osascript -e 'tell application \"System Events\" to set picture of {display} desktop to \"/Users/jacobl/wallpaper/{date}_up.jpg\"'") #update the desktop backround for each monitor

if __name__ == "__main__":
    main()

