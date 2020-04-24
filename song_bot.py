#-*-coding:utf-8-*-

import argparse
import asyncio
import json
import os

import discord
from discord.ext import commands

ffmpeg_options = {
    'options': '-vn'
}


class MusicBot(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.song_parent = db["files_dir"]
        print("Music files will be loaded from {}.".format(self.song_parent))
        self.song_database = db["songs"]
        print("songs: ", end="")
        for x in self.song_database:
            print(x["song_keys"][0], ", ", end="")
        print("")
        self.playlist = []
        self.current = "#NA"

        self. ctx = None
        self.volume = 0.2

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--artist", action="store", nargs="+")
        self.parser.add_argument("--song", action="store", nargs="+")
        self.parser.add_argument("--album", action="store", nargs="+")
        self.parser.add_argument("--random", action="store_true")
        self.parser.add_argument("--all", action="store_true")

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        self.ctx = ctx
        await channel.connect()

    def parse(self, query):
        play_args = self.parser.parse_args(query.split(" "))
        target_songs = []
        # process args!
        if "artist" in play_args and play_args.artist is not None:
            print("Query artists: ", end="")
            print(play_args.artist)
            for artist in play_args.artist:
                artist_clean = artist.lower().replace(" ", "")  # sanitize
                tmp = [x for x in self.song_database if artist_clean in x["artist_keys"]]
                target_songs = [*target_songs, *tmp]
        if "album" in play_args and play_args.album is not None:
            print("Query album: ", end="")
            print(play_args.album)
            for album in play_args.album:
                album_clean = album.lower().replace(" ", "")
                tmp = [x for x in self.song_database if album_clean in x["album_keys"]]
                target_songs = [*target_songs, *tmp]
        if "song" in play_args and play_args.song is not None:
            query_songs = [x.replace("\"", "").replace("\'", "") for x in  play_args.song]
            print("Query songs: ", end="")
            print(query_songs)
            if len(target_songs) != 0: # filter!
                target_songs_new = []
                for song in query_songs:
                    song_clean = song.lower().replace(" ", "")
                    tmp = [x for x in target_songs if song_clean in x["song_keys"]]
                    target_songs_new = [*target_songs_new, *tmp]
                target_songs = target_songs_new
            else:
                for song in query_songs:
                    song_clean = song.lower().replace(" ", "")
                    tmp = [x for x in self.song_database if song_clean in x["song_keys"]]
                    target_songs = [*target_songs, *tmp]

        return target_songs

    @commands.command()
    async def add(self, ctx, *, query):
        self.ctx = ctx

        target_songs = self.parse(query)
        self.playlist = [*self.playlist, *target_songs]

    @commands.command()
    async def play(self, ctx, *, query):
        self.ctx = ctx
        print("Incoming query: ", query)

        target_songs = self.parse(query)

        self.playlist = [*self.playlist, *target_songs]
        print("Current playlist: ", end="")
        for x in self.playlist:
            print("    {} by {}".format(x["song_keys"][0], x["artist_keys"][0]))

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        else:
            await self.play_song(None)

    async def play_song(self, error):
        if error is not None:
            print("Error: {}".format(e))
            return
        print("Checking playlist...")
        if len(self.playlist) == 0:
            await self.ctx.send("Playlist empty")
            self.is_playing = False
            return

        print("looking for the file")
        target_file_path = os.path.join(self.song_parent, self.playlist[0]["filename"])
        target_song = self.playlist[0]["song_keys"][0]
        target_artist = self.playlist[0]["artist_keys"][0]
        del self.playlist[0]

        await self.ensure_voice(self.ctx)

        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(target_file_path, options="-b:a 128k")
        )
        source.volume = self.volume
        await self.ctx.send("Now playing: {} by {}".format(target_song, target_artist))
        self.current = "{} by {}".format(target_song, target_artist)
        self.ctx.voice_client.play(
            source,
            after=self.dispatch_play_song
        )
        print("Now playing: {} by {}".format(target_song, target_artist))

    def dispatch_play_song(self, e):
        print("dispatch!")
        if e is not None:
            print("Error: ", end="")
            print(e)
            return

        # asyncio.run(self.play_song(None), self.bot.loop)
        coro = self.play_song(None)
        fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
        try:
            print("fut.result")
            fut.result()
        except:
            pass

        return

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()

    @commands.command()
    async def skip(self, ctx, *, how_many=0):
        m_del = int(how_many)
        m_del = m_del if m_del <= len(self.playlist) else len(self.playlist)
        for _ in range(m_del):
            del self.playlist[0]
        # await self.play_song(None)
        ctx.voice_client.stop()

    @commands.command()
    async def show(self, ctx):
        to_show = [
            "Now playing: " + self.current,
            "Songs in playlist: "
        ]
        if len(self.playlist) == 0:
            to_show[-1] = "Playlist empty"
        for i, song in enumerate(self.playlist):
            to_add = "{0:02d}. ".format(i) + song["song_keys"][0] + " by " + song["artist_keys"][0]
            to_show.append(to_add)

        await ctx.send("\n".join(to_show))

    @commands.command()
    async def quit(self, ctx):
        self.playlist = []

        ctx.voice_client.stop()

        await ctx.voice_client.disconnect()

    @commands.command()
    async def q(self, ctx):
        await self.quit(ctx)

    @commands.command()
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        self.volume = volume / 100
        if ctx.voice_client.source is not None:
            ctx.voice_client.source.volume = self.volume
        await ctx.send("Changed volume to {}%".format(volume))

    # これわるさしてるかも
    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing(): #こいつだああああああああああああああああああああああああ
            pass

def main(args):
    print("Initializing...")
    if "token_file" in args:
        with open(args.token_file, "r") as f:
            tmp = json.load(f)
        token = tmp["token"]
    elif "token" in args:
        token = args.token
    print("Token loaded.")

    # load database
    with open(args.database, "r") as f:
        db = json.load(f)

    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(">", "!"),
        description='Plays local music file in voice channel'
    )

    @bot.event
    async def on_ready():
        print("Logged in as {0} ({0.id})".format(bot.user))
        print('------')

    bot.add_cog(MusicBot(bot, db))
    bot.run(token)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    token_group = parser.add_mutually_exclusive_group(required=True)
    token_group.add_argument("--token_file", action="store", help="json file which has discord bot token")
    token_group.add_argument("--token", action="store", help="bot token")

    parser.add_argument("--database", "-d", action="store", help="json file which has song file path and info", required=True)

    args = parser.parse_args()

    main(args)
