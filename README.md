The idea comes from [this project](https://github.com/Embraser01/INSA-Planning-generator).

## Configuration

The program requires an `.env` file of the following form at the root of the project: 

```bash
LOGIN=flastname  # INSA login, usually first initial + last name
PASSWORD=password  # INSA password
YEAR=3  # desired year of the schedule (3, 4 or 5)

DISCORD_TOKEN=XXX  # the token of the bot
DISCORD_CHANNEL_ID=XXX  # the channel id in which the bot must write
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Launch the bot:

```bash
python3 src/bot.py
```