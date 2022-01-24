# Astronomy Picture of The Day

This project uses Python to scrape photos from [NASA's Astronomy Picture of the Day](https://apod.nasa.gov/apod/astropix.html) and sets them as your monitor(s) wallpaper.  

### Python Enviroment 
All required python libraries and versions are defined in requirments.txt. 

`pip3 install -r requirements.txt`

### Running Ad-Hoc
 In the terminal navigate to the directory where the source code lives, for example, 

`cd /Users/{username}/astronompy_picture_of_the_day-main/scripts`
 
 To run the script, enter

`python3 soupv2.py`

### Running periodically using crontab
First you'll need to mark the shell script that executes the python code as executable. In the terminal, navigate to the directory where update_background.zsh is. Then run the following [chmod command](https://en.wikipedia.org/wiki/Chmod) to allow the shell script to be executed.

`chmod +x update_background.zsh`

Next, you'll need to update your cronjobs to run the code. In the terminal, type
`crontab -e`
to edit the [crontab](https://www.geeksforgeeks.org/crontab-in-linux-with-examples/#:~:text=The%20crontab%20is%20a%20list,the%20Greek%20word%20for%20time.) and add the follwowing text:

`30 9 * * 1-5 /Users/{username}/astronompy_picture_of_the_day-main/scripts/update_background.zsh`