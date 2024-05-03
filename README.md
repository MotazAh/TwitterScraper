# Twitter Scraper

### Usage Instructions:
- Install all modules necessary in the "requirements.txt" file
- You will need session cookies from a logged user to gain access to more posts per user. Login to twitter then inspect element. Go to "Application" tab and expand cookies then click on twitter.com cookie
- Copy the cookie values as in the image: **_twitter_sess, auth_token, twid**

![Cookies ScreenShot](img/sess_data.jpg?raw=true "Title")

- Paste the values into the corresponding key in the .env file 

![env ScreenShot](img/env_data.jpg?raw=true "Title")

- Run the python file. You will be asked to enter the cash tag without "$" sign then you will need to enter the time interval in minutes.

![env ScreenShot](img/input.jpg?raw=true "Title")

- The script will start running and will log the output in "log.txt" file

![env ScreenShot](img/output.jpg?raw=true "Title")