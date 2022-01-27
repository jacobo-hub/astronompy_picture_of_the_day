#!/usr/local/bin/python3
import io
import os
import cv2
import json
import time
import glob
import requests
import numpy as np
from statistics import mean
from random import randrange
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_directories():
    '''
    Creates a directory for the images to live in
    '''
    working_dir = "/".join(os.getcwd().split("/")[0:3])
    if not os.path.exists(f"{working_dir}/wallpaper"):
        os.mkdir(f"{working_dir}/wallpaper")
    return f'{working_dir}/wallpaper'
    
def clear_images(directory):
    '''
    Removes all old desktop images, as the upscaliing process increases their size
    '''
    old_images = f"{directory}/*.jpg"
    for image in glob.glob(old_images): 
        os.remove(image)

def get_monitor_resolutions(displays = {}):
    '''
    Uses the system command to get the resolution of each monitor
    '''
    resolutions = os.popen('/usr/sbin/system_profiler SPDisplaysDataType | grep Resolution').read().split('\n')
    displays = get_monitor_count(resolutions,displays)
    return displays


def get_monitor_count(resolutions,displays = {}):
    '''
    returns a dictionary of monitor resolutions and their names
    '''
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

def get_site(log = {}):
    '''
    Selects a random day between today and the last year, and returns the NASA space image url for the day
    '''
    delta = randrange(0,9000)
    today = datetime.today() - timedelta(days=delta)
    date = today.strftime('%y%m%d')
    site = f'https://apod.nasa.gov/apod/ap{date}.html'
    log_date = today.strftime('%Y-%m-%d')
    return site,date,log_date

def find_image(site):
    '''
    Takes the NASA site of any days, attempts to find the image url and description
    '''
    try:
        soup = BeautifulSoup(requests.get(site).text, 'html.parser')
        img_tag = soup.find('img')
        img_url = img_tag.get('src')
        description = soup.find_all('b')[0].text
        return img_url,description

    except AttributeError as e: # since some days don't have an image, we catch the error and try again
        time.sleep(5.0)
        site,date = get_site()
        img_url,description = find_image(site)
        return img_url,description


def make_request(url):
    '''
    Uses the retquest library to make a get request to a URL, with a retry policy
    '''
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504 ])
    s.mount('http://', HTTPAdapter(max_retries=retries))
    response = s.get(url, stream=True)
    return response

def get_image(img_dir,site,date):
    '''
    Gets the space photo from the NASA site and encodes as a numpy arrary
    '''
    img_url = f"{site.replace(f'ap{date}.html','')}{img_dir}"
    space_photo = make_request(img_url).content
    space_photo = io.BytesIO(space_photo)
    space_photo.decode_content = True
    image = np.asarray(bytearray(space_photo.read()), dtype="uint8")
    return image

def up_scale(dir,space_photo,date,scale_factor,resolution):
    '''
    Uses opencv to upscale the image to the resolution of the monitor
    '''
    img = cv2.imdecode(space_photo, cv2.IMREAD_COLOR)
    res = [int(resolution.split('x')[0].strip()),int(resolution.split('x')[1].strip())]
    scale_percent = scale_factor*mean(res)
    if res[0]<res[1]: # if the monitor is wider than it is tall, we rotate the image
       img = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE)
    width = int(res[0] * scale_percent / 100)
    height = int(res[1] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_LINEAR)
    cv2.imwrite(f'{dir}/{date}_up.jpg',resized) 

def cron_log(cron_logs):
    print(json.dumps(cron_logs,indent=2))

def main():
    '''
    Calls the above function to retrieve a space photo for each monitor, and then upscales the image to the resolution of the monitor
    '''
    cron_logs = []
    scale_factor = 0.35
    dir = create_directories()
    clear_images(dir)
    displays = get_monitor_resolutions()
    for display,resolution in displays.items():
        site,date,log_date = get_site()
        img_url,description = find_image(site)
        space_photo = get_image(img_url,site,date)
        up_scale(dir,space_photo,date,scale_factor,resolution)
        time.sleep(.5)
        os.system(f"osascript -e 'tell application \"System Events\" to set picture of {display} desktop to \"{dir}/{date}_up.jpg\"'") #update the desktop backround for each monitor

        cron_logs.append({
            'date': log_date,
            'site': site
        })
    cron_log(cron_logs)
if __name__ == "__main__":
    main()
