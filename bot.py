"""
Discord bot for extracting songs/albums/artists songs.
Latest update: 15.11.2023
A Discord-based program for providing organized data to users via CSV and Excel files.
"""

# Import necessary modules
import importlib
import subprocess
import time
import sys
import os  # Added for folder creation

# Create necessary folders if they don't exist
CSV_FOLDER = "data\\csv\\"
EXCEL_FOLDER = "data\\excel\\"

if not os.path.exists(CSV_FOLDER):
    os.makedirs(CSV_FOLDER)

if not os.path.exists(EXCEL_FOLDER):
    os.makedirs(EXCEL_FOLDER)

# Installing necessary modules
required_modules = ['discord', 'spotipy', 'pandas']

missing_modules = []

for module in required_modules:
    try:
        importlib.import_module(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    for module in missing_modules:
        try:
            subprocess.check_call([f"pip install {module}"])
        except subprocess.CalledProcessError as e:
            print(f'Start failed. Program will break in 5s')
            time.sleep(5)
            sys.exit()

# Import necessary modules
import discord
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import csv
import pandas as pd

# Constants
CSV_FOLDER = "data\\csv\\"
EXCEL_FOLDER = "data\\excel\\"

# Your Discord bot token
TOKEN = ''

# Your Spotify API information
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = ''

# Spotify client setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope='playlist-read-private'))

# Discord bot setup
client = commands.Bot(command_prefix='//', intents=discord.Intents.all())

# Writes data to both CSV and Excel files.
def write_to_csv_and_excel(file_name, headers, data):
    csv_path = f"{CSV_FOLDER}{file_name}.csv"
    excel_path = f"{EXCEL_FOLDER}{file_name}.xlsx"

    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(headers)
            csv_writer.writerows(data)

        df = pd.DataFrame(data, columns=headers)
        df.to_excel(excel_path, index=False)

    except Exception as e:
        print(f"Error writing to files: {e}")

# Extracts songs based on the provided link and type.
async def extract_songs(ctx, link, extract_type):
    async def send_and_check_length(user, text):
        # Sending to the user's private channel, dividing into messages if it exceeds the limit
        chunks = [text[i:i + 2000] for i in range(0, len(text), 2000)]
        for chunk in chunks:
            await user.send(chunk)

    data = []
    offset = 0
    limit = 50

    if extract_type == 'playlist':
        i = 0
        results = sp.playlist_tracks(link, limit=100)

        playlist_info = sp.playlist(link)
        songs_text = ""  # Variable to store the text of songs
        for idx, track in enumerate(playlist_info['tracks']['items']):
            track_info = track['track']
            artists = ', '.join([artist['name'] for artist in track_info['artists'] if artist.get('name')])
            album_name = track_info['album']['name'] if 'album' in track_info and 'name' in track_info['album'] else 'Unknown Album'
            track_name = track_info['name']
            data.append([track_name, album_name, artists])
            current_line = f"{track_name} - {artists} - Album: {album_name}\n"
            i += 1

            if len(songs_text + current_line) <= 2000:
                songs_text += current_line
            else:
                await send_and_check_length(ctx.author, songs_text)
                songs_text = current_line
                i += 1

        while results['next']:
            results = sp.next(results)
            for idx, track in enumerate(results['items']):
                track_info = track['track']
                album_name = track_info['album']['name'] if 'album' in track_info and 'name' in track_info['album'] else None
                track_name = track_info['name']
                artists = ', '.join([artist['name'] for artist in track_info['artists']])
                data.append([track_name, album_name, artists])
                current_line = f"{track_name} - {artists} - Album: {album_name}\n"
                if len(songs_text + current_line) <= 2000:
                    songs_text += current_line
                    i += 1
                else:
                    await send_and_check_length(ctx.author, songs_text)
                    songs_text = current_line
                    i += 1

        if songs_text:
            await send_and_check_length(ctx.author, songs_text)
            await ctx.send(f"Number of songs extracted: {i-1}")

    elif extract_type == 'artist':
        results = sp.artist_albums(link, album_type='album', offset=offset, limit=limit)
        albums = results['items']
        for album in albums:
            album_id = album['id']
            album_tracks_info = sp.album_tracks(album_id, limit=limit)
            album_tracks = album_tracks_info['items']

            songs_text = ""  # Variable to store the text of songs
            for track_info in album_tracks:
                if 'name' in track_info:
                    track_name = track_info['name']
                    artists = ', '.join([artist['name'] for artist in track_info['artists']])
                    album_name = album['name'] if 'name' in album else 'Unknown Album'
                    data.append([track_name, album_name, artists])
                    current_line = f"Album: {album_name}, Track: {track_name}, Artists: {artists}\n"
                    if len(songs_text + current_line) <= 2000:
                        songs_text += current_line
                    else:
                        await send_and_check_length(ctx.author, songs_text)
                        songs_text = current_line

            if songs_text:
                await send_and_check_length(ctx.author, songs_text)
    else:
        album_tracks_info = sp.album_tracks(link, offset=offset, limit=limit)
        tracks = album_tracks_info['items']

        songs_text = ""  # Variable to store the text of songs
        for track_info in tracks:
            if 'name' in track_info:
                track_name = track_info['name']
                artists = ', '.join([artist['name'] for artist in track_info['artists']])
                album_name = track_info['album']['name'] if 'album' in track_info and 'name' in track_info['album'] else None
                data.append([track_name, album_name, artists])
                current_line = f"{extract_type.capitalize()}: {track_name}, Artists: {artists}, Album: {album_name}\n"
                if len(songs_text + current_line) <= 2000:
                    songs_text += current_line
                else:
                    await send_and_check_length(ctx.author, songs_text)
                    songs_text = current_line

        if songs_text:
            await send_and_check_length(ctx.author, songs_text)

    # Sending information about the number of songs to the Discord channel
    if extract_type == 'artist' or extract_type == 'album':
        await ctx.send(f"Number of songs extracted: {len(data)}")

    if data:
        headers = ['Track Name', 'Album', 'Artists']
        write_to_csv_and_excel(f"{extract_type}_songs", headers, data)

@client.event
async def on_ready():
    print("Bot on")

@client.command()
async def shutdown(ctx):
    if ctx.author.id == 440491887745564672:
        await ctx.send("Shutting down... Goodbye!")
        await client.close()
    else:
        await ctx.send("You do not have permission to shut down the bot.")

@client.command()
async def playlist(ctx, playlist_link):
    await extract_songs(ctx, playlist_link, 'playlist')

@client.command()
async def artist(ctx, artist_link):
    await extract_songs(ctx, artist_link, 'artist')

@client.command()
async def album(ctx, album_link):
    await extract_songs(ctx, album_link, 'album')

class MyNewHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page)
            await destination.send(embed=emby)

client.help_command = MyNewHelp()
client.remove_command('help')

@client.command()
async def help(ctx):
    embed = discord.Embed(
        title="Bot Command Help",
        description="Type `//help` for everything you need.",
    )
    embed.add_field(
        name="Command List",
        value="```• Extract every song from playlist:\n   //playlist [playlist_link]\n\n"
              "• Extract every song from artist:\n   //artist [artist_link]\n\n"
              "• Extract every song from album:\n   //album [album_link]```"
    )
    await ctx.send(embed=embed)

client.run(TOKEN)
