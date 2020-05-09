# Telegram-Bridgebot

Floating brige bot for telegram.

## Introduction

Floating bridge is a modified version of the original contract bridge game with laxer rules. Most of the game rules from the original contract bridge are preserved in floating bridge, with the exception of the rules on how partners are determined and which of the declarer partners will be playing the game. [Wikipedia](https://en.wikipedia.org/wiki/Singaporean_bridge) has a pretty good explanation on how the game works.

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

## Running your Bot

First, host your bot by running the **telegram_manager.py**.

Next, add your bot into a telegram group chat (with at least 4 members).

To start a game, type `/start` command inside the telegram group chat.

## FAQs

1. Is it possible to play a contract bridge game with this bot?
- **Yes, _to a certain extent_.** Since floating bridge is practically contract bridge with less restrictions, you can always manually implement additional restrictions (e.g. fixed NS-EW partnerships) in the game and play it as a contract bridge game. One issue, though, is that the declarer partners will have to expose one of the cards belonging to the non-playing partner during the partner selection phase. In contract bridge, the non-playing partner will only expose his/her entire hand to the table after the first defender has opened the first round.

2. It seems like you wrote a **_stateless_** implementation of the floating bridge logic in the **stateless_bridge.py**. Is there any specific reason why such a _stateless_, _functional_ implementation was chosen?
- **Nope.** I was just too bored and was looking for something challenging to do. Since I am familiar with floating bridge, I thought it'd be a good idea to create a Telegram bot for it. However, it seemed like implementing the bridge logic in the typical [OO](https://en.wikipedia.org/wiki/Object-oriented_programming) style would be pretty easy, and as such, I thought I'd try to implement it in a stateless and purely functional way instead to add more **_oomph_** to the task. In retrospect, I might have underestimated the complexity of the game logic, and the choice to write a _stateless_ implementation of the naturally _stateful_ game might have been a mistake. But then again, I had quite a lot of fun working on it, so ... ¯\\_(ツ)_/¯

3. It seems like you are using the **stateless_bridge.py** as some sort of back-end engine and the Telegram bot as a front-end interface. Is it possible to implement a different front-end interface (e.g. web application) for the **stateless_bridge.py**?
- **Yes, it is possible, but do take note that the stateless_bridge.py was developed with Telegram bot as front-end interface in mind.** As such, the implementation may not lands itself naturally in a typical back-end and front-end implementations for web applications. If you are interested to learn more, feel free to contact me.
