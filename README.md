# Telegram-Bridgebot

Floating brige bot for telegram.

## Getting Started

The following instructions will guide you on how to host the bot on your machine.

### Prerequisites

Here are the things you need to have installed in your machine:
* Python 3.6 or newer
* Python Telepot module 12.7 or newer (12.7 was used for development)

### Setup

First, clone this repo using this command in your terminal: `git clone https://github.com/hanstjua/Telegram-Bridgebot.git`

Next, create your own Telegram bot ([instructions here](https://core.telegram.org/bots#3-how-do-i-create-a-bot)) and get your bot token.

With your token ready, go into your Telegram-Bridgebot directory and create a Python file called **bot_data.py** (refer to the directory tree below).

```
- Telegram-Bridgebot
  - stateless_bridge.py
  - telegram_manager.py
  - bridge.py
  - util.py
  - main.py
  - **bot_data.py**
```

In the **bot_data.py**, add the line below to store your bot token value:

`token = '<YOUR_TOKEN_VALUE>'`

(Remember to replace *<YOUR\_TOKEN\_VALUE>* with your bot's token value obtained from the **BotFather**)

Finally, save the file and your are ready to host your Bridgebot!

**Important: _Always keep your bot token secret!_ Should your bot's token be exposed (e.g. accidentally uploaded to online platforms), immediately ask the BotFather for a new token.**

### Hosting your Bot

To host your bot, simply run the **telegram_manager.py**.
