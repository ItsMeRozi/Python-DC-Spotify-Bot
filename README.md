# Discord Bot for Extracting Songs

## Overview
A Discord bot designed to extract songs, albums, and artists' songs information from Spotify. The extracted data is organized and saved in both CSV and Excel files. The script utilizes the `discord`, `spotipy`, and `pandas` modules.

## Features
- Extract songs from playlists, artists, and albums
- Organize and save data in both CSV and Excel formats
- User-friendly commands for interaction (`//playlist`, `//artist`, `//album`)
- Automatic installation of required modules
- Automatic creation of data folders if not present
- Command list and help functionality (`//help`)
- Discord bot token, Spotify API information, and other constants are configurable

## How to Use
1. Run the script; required modules will be automatically installed.
2. Provide your Discord bot token, Spotify API information, and other required constants.
3. The bot will be ready to use.
4. Use commands like `//playlist [playlist_link]`, `//artist [artist_link]`, and `//album [album_link]` to extract song information.
5. Extracted data will be saved in the `data\csv\` and `data\excel\` folders.

## Latest Update
- 15.11.2023: Improved data extraction and storage functionality. Added help command and commands list.

Feel free to customize the script based on your preferences and enjoy extracting song information effortlessly with this Discord bot!
