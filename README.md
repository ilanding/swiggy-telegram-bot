# Swiggy Telegram Bot Starter

A minimal Telegram bot scaffold intended for an authorized API integration.

## Railway setup

1. Deploy this repository to Railway.
2. Add the environment variable `BOT_TOKEN` using the token from Telegram's BotFather.
3. Start the service with `python bot.py`.
4. Open the bot in Telegram and send `/start`.

## Commands

- `/start` — bot welcome message
- `/help` — setup guidance
- `/check` — reports whether an authorized API has been configured

This starter does not automate Swiggy login, enumerate phone numbers, or bypass anti-bot protections. Add only an official, authorized API integration that complies with the provider's terms.
