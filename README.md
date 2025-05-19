# CUNY Global Search Web Scraper

This tool allows users to connect their own Discord bot to the [CUNY Global Search](https://globalsearch.cuny.edu/CFGlobalSearchTool/search.jsp) system to monitor course availability. When a course status changes (e.g. from Open to Closed), interested users are automatically notified on Discord.

This is an updated version of my original scraper. It now supports all CUNY schools instead of being hardcoded to Queens College. It also minimizes user configuration — for example, term codes are auto-generated when needed.

[!Example](data/demo.png)

## Features

- Track course availability across all CUNY schools
- Get notified on Discord when a course status changes (e.g. Open → Closed)
- Retrieve information such as Instructor, Meeting Times, Room, etc.

## Prerequisites

- Python 3.9 or higher
- A Discord account
- A Discord server where you have admin access

## Setup Instructions

1. **Clone this repository**

    ```bash
    git clone https://github.com/mkbhuiyan96/cuny-global-search-bot.git
    cd cuny-global-search-bot
    ```

1. **Create a Discord bot**
   Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.

1. **Copy your bot's token**
   Under the **Bot** section, click **Reset Token** to generate a token.

   ⚠️ *This token is your bot’s password — do **not** share it with anyone!*

1. **Create a `.env` file in the base directory**
   Add the following line:

    ```bash
    DISCORD_TOKEN=your_copied_bot_token
    ```

1. **Invite the bot to your server**
   - In the Developer Portal, go to **OAuth2 > URL Generator**
   - Select the **"bot"** scope and these permissions:
     - Read Messages/View Channels
     - Send Messages
     - Use Slash Commands
   - Copy the generated URL and use it to invite the bot to your server

1. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

1. **Run the bot**

    ```bash
    python main.py
    ```
