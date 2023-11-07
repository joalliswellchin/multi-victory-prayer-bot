# multi-victory-prayer-bot
Telegram prayer bot to help you with your Christian walk

# Introduction
This bot can be used for your prayer journey
The idea is to set this up and use this for your personal journeys and count
your victories

Check out the bot [here](https://t.me/MVPrayer_bot)

Check out the [guide](https://github.com/joalliswellchin/multi-victory-prayer-bot/wiki) for how to use the telegram bot

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
python main.py
```

Other notables after setting up the app
1. As I only cover the app for now, some other things you can do is to add the list of commands on /help to /setcommands on botfather

# How to deploy to cloud
You can deploy to cloud however you like, but it is suggested you put to cloud
for the uptime. Follow [this](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Hosting-your-bot) for more details

The following are some examples I have thought of. You might have to tweak it to your settings

## on AWS Lambda
Installing pip should have also installed aws cli, be sure to follow up on this set up
    - Sign in to the AWS Management Console and navigate to the AWS IAM service.
    - Create a new IAM user or use an existing one.
    - Attach the necessary IAM policies to the user to allow them to deploy infrastructure with the AWS CDK. You can find a list of recommended IAM policies for the AWS CDK in the AWS CDK documentation.
    - Generate an access key and secret access key for the IAM user.
    - Run `aws configure` and fill in the access and secret key
5. Verify that your AWS credentials are correctly configured by running `aws sts get-caller-identity`
6. Go to BotFather on telegram and generate an API key for your bot. Type /newbot and follow the instructions to get the API key
7. Fill in .env with the telegram API key

Check [this](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Hosting-your-bot) out for how to deploy it on cloud using VM/instance like deployment

## on AWS instance and MongoDB
1. Go to mongodb and create a cluster
2. Fill in the information provided into .env (all those with prefix MONGO_)
3. Create a new collection with MVPBot as the database and chat_data as the collection
4. (Optional) create a screen `screen -S name_of_screen`
5. Run `python main.py`
6. ctrl + A + D to exit screen, and `screen -r name_of_screen` to reconnect
 
Check [this](https://github.com/havebeenfitz/om-random-coffee-bot/wiki/Hosting-the-bot-on-AWS-Lambda) out for how to deploy it via serverless

# How does data persist in this application
There are presently 2 kinds of persistence supported
Local persistence uses python pickle files. This is provided by [ptb](https://github.com/python-telegram-bot/python-telegram-bot), [details](https://docs.python-telegram-bot.org/en/stable/telegram.ext.picklepersistence.html) as follows
Cloud persistence uses MongoDB. I adopt from this [persistence class](https://github.com/LucaSforza/MongoPersistence)

You can create your own persistence using BasePersistence class and fork from this repository (or create an issue, and add a pull request!)
For more information you can check [this](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Making-your-bot-persistent) out

# How to use this application
Check out the [wiki](https://github.com/joalliswellchin/multi-victory-prayer-bot/wiki) here

# How to contribute
If you have found an issue, you can raise an issue and a pull request (if you found a solution)

Alternatively, check out the issues list and create a pull request

# How else to support
You can support me through donation on Ko-fi. Check out the `sponsor` button above!

# APPENDIX
## Sample env file
```
TELEGRAM_API_KEY=
ENV=LOCAL
DB_ENV=LOCAL_FILE
SSM_ID=
MONGODB_USER=
MONGODB_PWD=
MONGODB_CLUSTER=
MONGODB_DBNAME=
MONGODB_COLLECTION_NAME=
MONGODB_UPLOAD_INTERVAL=
MONGODB_USER_DATA=
MONGODB_CHAT_DATA=
MONGODB_BOT_DATA=
MONGODB_CONVO=
DATETIME_FORMAT="%d/%m/%Y, %H:%M:%S"
```
