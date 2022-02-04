#!/usr/local/bin/python3
import os
import glob
import shutil
import logging
import requests
import numpy as np
from statistics import mean
from random import randrange
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import sys

def config_logs():
    log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep + os.pardir), 'logs')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_fname = os.path.join(log_dir, 'info.log')
    logging.basicConfig(filename=log_fname, level=logging.INFO,
    format=	'%(asctime)s:%(levelname)s:%(message)s') # set the logging level


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
    
    old_images = f"{directory}/*.jpeg"
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

def random_date():
    '''
    Selects a random day between today and the last year, and returns the NASA space image url for the day
    '''
    delta = randrange(0,500)
    today = datetime.today() - timedelta(days=delta)
    log_date = today.strftime('%Y-%m-%d')
    return log_date

def get_image(dir,date):
    '''
    Gets the space photo from the NASA site and encodes as a numpy arrary
    '''
    
    url = 'https://api.nasa.gov/planetary/apod'
    params = {
        'date': "1997-05-14",
        'api_key': 'gIyYysKXvewhmzbl6SY1z46MxNCfLaFhOuuo36xq',
        'thumbs': False
        }
    try:
        img_url = requests.get(url, params = params).json()['url']
    except KeyError:
       # time.sleep(5.0)
        log_date = random_date()
        img_url = get_image(dir,log_date)
    title = requests.get(url, params = params).json()['title'].replace(' ','_').replace("'",'')
    image = requests.get(img_url, stream=True)
    out_file = f'{dir}/{title}.jpeg'
    fname = f'{dir}/{title}.jpeg'
    with open(out_file, 'wb') as out_file:
        shutil.copyfileobj(image.raw, out_file)
    del image
    return fname


def main():
    '''
    Calls the above function to retrieve a space photo for each monitor, and then upscales the image to the resolution of the monitor
    '''
    config_logs()
    dir = create_directories()
    clear_images(dir)
    displays = get_monitor_resolutions()
    for display,resolution in displays.items():
        date = random_date()
        space_photo = get_image(dir,date)
        print(space_photo)
        os.system(f"osascript -e 'tell application \"System Events\" to set picture of {display} desktop to \"{space_photo}\"'") #update the desktop backround for each monitor
        logging.info(f"{display} monitor | APOD date: '{date}'")
        

if __name__ == "__main__":
    main()
