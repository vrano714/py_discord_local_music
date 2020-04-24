# Play your local music file on a discord voice channel

## Setup

### Install deps

Requirements

* python 3 (>3.4)
* discord.py library with voice support
* ffmpeg
* your music file(s)

Firstly, install python3 in a way you prefer.

Secondly, install dicord.py dependencies and discord.py.

Please refer to [dicord.py documentation](https://discordpy.readthedocs.io/en/latest/) for installation.

On the environments with `apt`, installation will be as follows.

```bash
sudo apt install libffi-dev libnacl-dev python3-dev ffmpeg
```

The bot uses `ffmpeg` to stream a file, thus `ffmpeg` must be installed here.

After installing dependencies, install discord.py with voice support.

```bash
python3 -m pip install -U dicord.py[voice]
```

### Register a bot on discord

You need to set up a bot account.

Again, refer to "Creating a Bot Account" section in [dicord.py documentation](https://discordpy.readthedocs.io/en/latest/) for setting up a bot account, getting a token, inviting the bot.

Note: turn off "PUBLIC BOT" toggle button to keep your bot private.

### Get a token of the bot

Open the bot setting in the app page and click "Copy" in "TOKEN" section.

After that, save the token in a file such as...

```token.json
{
    "token": "paste the token you copied"
}
```

Ensure that you never share this token.

### Invite the bot to your server

In your app setting page, open "OAuth2" tab.

Tick "bot" in "SCOPE" section.

Tick the following permissions:

* send messages (in text permissions)
* connect (in voice permissions)
* speak (in voice permissions)

Copy the generated URL, paste it to the favorite browser. Select the server which you want to add the bot.

Note: you must have "Manage server" permissions to do this.

### Prepare music files

Place the music files in a directory and prepare a `json` file with song entries.

```song_db.json
{
    "files_dir": "/home/someuser/Music",
    "songs": [
        {
            "song_keys": [
                "song a",
                "a"
            ],
            "artist_keys": [
                "ham spam egg",
                "hse"
            ],
            "album_keys": [
                "super songs",
                "ss"
            ],
            "filename": "song_a.flac"
        },{
            ...
        }, ...
    ]
}
```

The bot needs this file to get a file corresponding to the query.

## Play on a voice channel

### Launch the bot

Open a terminal and navigate to the directory of ths repo.

Launch the bot with the token and the music db you made above.

```bash
python3 song_bot.py --token_file token.json --database song_db.json
```

Note: terminal multiplexer such as `tmux` and `screen` may be for you to keep the bot active.

This is the end of what you do on your terminal.

### Play

Open discord and connect to a voice channel.

Send a message to play a song such as...

```text
!play --song your-song-name
```

The bot will automatically join the voice channel and play the song.

## Available commands

### join

The bot will connect to a voice channel.

You can specify the channel by passing the name.

```text
!join channel_alpha
```

### play [options]

Play song.

Options are:

* `--album`: play songs in album(s)
* `--artist`: play songs by artist(s)
* `--song`: play song(s)

Combination of these options are not supported.

```text
!play --song song_a song_b
```

### add [options]

Add song to the queue.

Same options can be used with play.

### pause/resume

Pause and resume.

```text
!pause
```

```text
!resume
```

### skip

Skip the current song and play next song in the playlist.

```text
!skip
```

### show

Show the playlist.

```text
!show
```

### quit

The bot will disconnect from the voice channel.

```text
!quit
```

`!q` will do the same (shorthand version).
