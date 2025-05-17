# CUNY Global Search Web Scraper

This software will allow users to give their own supplied Discord bot functionality to scrape CUNY Global Search for course availability, and notify interested users upon the status of the course changing (e.g. from Open to Closed or vice versa)

This is an update to my original Global Search web scraper, as I wanted to update it to be more generic and easily work with all CUNY schools instead of hard coding Queens College for the scraping. There is now minimal user input required in terms of modifying files, as things such as the term code are automatically generated if necessary.

## Instructions

1. Clone this repository.
1. Create a Discord bot at the [Discord Developer Portal](https://discord.com/developers/applications), if you haven't already done so.
1. From the bot section, copy the bot's token. **WARNING:** This token is effectively the bot's password — do NOT share it with anyone, as this will give anyone full access to your bot!
1. You need to set this token as an environmental variable. In the base directory of the repository, make a .env file and set DISCORD_TOKEN = {YOUR_COPIED_DISCORD_BOT_TOKEN}.
1. Under the OAUTH2 section of the developer portal, use the URL Generator to get an invitation link for your bot. Select 'bot' and the necessary permissions ('Read Messages/View Channels', 'Send Messages', and 'Use slash commands').
1. Use the generated URL to invite your bot to a Discord server where you have admin rights.
1. You can install the dependencies by running "pip install -r requirements.txt" on your console in the directory for this project. (This is assuming you already have Python installed)
1. You should be able to then run the Python file "main.py" once you set up these variables properly, will will boot up the bot.
