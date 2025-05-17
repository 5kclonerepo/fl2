# Telegram Auto Filter Bot

A telegram bot to find files saved in its database and to serve in them groups.

## Features

- Auto index files from given database channel/group.
- Group settings for customization.
- Admin settings within the bot.
- Show search results as Button or List or List-Hyperlink.
- Manual index of files from channels.
- Supports document, video and audio file formats with file name caption support.
- Add manual text filters.
- Add username in file caption.
- Ban/Unban users.
- Broadcast to users.
- Auto delete files after a certain time.
- Force Subscription option.
- Option for Custom Caption
- Get logs / Restart from within the bot.

## Environment Variables

Required Variables

- `BOT_TOKEN`: Create a bot using [@BotFather](https://telegram.dog/BotFather), and get the Telegram API token.
- `APP_ID`: Get this value from [telegram.org](https://my.telegram.org/apps).
- `API_HASH`: Get this value from [telegram.org](https://my.telegram.org/apps).
- `DB_CHANNELS`: ID of database channel or group. Separate multiple IDs by space
- `OWNER_ID`: User ID of owner.
- `ADMINS`: User ID of Admins. Separate multiple Admins by space.
- `DB_URL`: Link to connect postgresql database (setup details given below).

## Database Setup

```bash
# Install postgresql:
sudo apt-get update && sudo apt-get install postgresql && sudo apt-get install redis-server 

# Change to the postgres user:
sudo su - postgres

# Create a new database user (change YOUR_USER appropriately):
createuser -P -s -e YOUR_USER
# This will be followed by you needing to input your password.

# create a new database table:
createdb -O YOUR_USER YOUR_DB_NAME
#Change YOUR_USER and YOUR_DB_NAME appropriately.

# finally: To verify
psql -h YOUR_HOST -p YOUR_PORT -d YOUR_DB_NAME -U YOUR_USER

#This will allow you to connect to your database via your terminal.
By default, YOUR_HOST should be `localhost` & YOUR_PORT should be `5432`.

If connected, write \q then Enter to exit
Again type `exit` and Enter to exit postgres user


You should now be able to build your database URI. This will be:
postgresql://username:password@hostname:port/db_name

Replace your sqldbtype, username, password, hostname (localhost?), port (5432?), and db name in .env file.
```

## Deployment

Run Locally / On VPS

```bash
# Clone this repo
git clone https://github.com/EL-Coders/groupfilter

# cd folder
cd groupfilter

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
venv\Scripts\activate # For Windows
source venv/bin/activate # For Linux or MacOS

# Install Packages
pip3 install -r requirements.txt

# Copy .env.sample file & add variables
cp .env.sample .env

# Run bot
python3 -m groupfilter
```

If you want to modify start & help messages, copy [`sample_const.py`](sample_const.py) to `const.py` and do the changes.

```bash
cp sample_const.py const.py
```
