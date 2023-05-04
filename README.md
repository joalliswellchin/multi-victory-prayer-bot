# multi-victory-prayer-bot
Telegram prayer bot to help you with your Christian walk

# Introduction
This bot can be used for your prayer journey
The idea is to set this up and use this for your personal journeys and count
your victories

The difference between a Full version and a Lite version is the data storage 
strategy. Full version will be a full blown architecture,accommodating for cloud
VM deployments so as to scale for churches. Lite version should store with 
local chat persistence (Using pickle file for now)
For more information you can check these out:
https://github.com/python-telegram-bot/python-telegram-bot/wiki/Making-your-bot-persistent

Do take note that the lite version will eventually not be maintained as much as
the full version. Additionally, earlier versions of lite will only contain 1
main.py file as there were concerns to file upload limits from architecture.

# How to set this up yourself to develop
Note that because these is written to be more non-developer friendly, feel free
to skip steps you find repeated

1. clone/fork this repository or download its binaries
2. change directory to app
3. run the following: (Note that venv is optional)
```
cp sample_env.txt .env
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

4. Installing pip should have also installed aws cli, be sure to follow up on this set up
    - Sign in to the AWS Management Console and navigate to the AWS IAM service.
    - Create a new IAM user or use an existing one.
    - Attach the necessary IAM policies to the user to allow them to deploy infrastructure with the AWS CDK. You can find a list of recommended IAM policies for the AWS CDK in the AWS CDK documentation.
    - Generate an access key and secret access key for the IAM user.
    - Run `aws configure` and fill in the access and secret key
5. Verify that your AWS credentials are correctly configured by running `aws sts get-caller-identity`
6. Go to BotFather on telegram and generate an API key for your bot. Type /newbot and follow the instructions to get the API key
7. Fill in .env with the telegram API key

Other notables after setting up the app
1. As I only cover the app for now, some other things you can do is to add the list of commands on /help to /setcommands on botfather

# How to use this application
Check out the wiki here: https://github.com/joalliswellchin/multi-victory-prayer-bot/wiki 

# How to deploy to cloud
You can deploy to cloud however you like, but it is suggested you put to cloud
for the uptime


# How to contribute
-- this is still work in progress --
You can raise an issue and a pull request (if you found a solution)

# APPENDIX
## Sample env file
```
TELEGRAM_API_KEY=
```
