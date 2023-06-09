# VRC/spell-chanting

__This is Experimental__

VRChat/OSC by Speech Recognition

## ARCHITECTURE

```
[Google Chrome]--(speech recognition)->[Python]--(OSC)->[VRChat]
```

## Requirements

- Python3.11 or Docker
- Google Chrome browser
    - or other chromium can work? (not tested)

## Setup & Startup

Spells are defined in `config.toml`.
Please edit it at first.

### if you can use Python3.11...

```bash
make serve
```

### if you can use Docker...

```bash
make serve-docker
```

And open `localhost:8080`.

## About textchat

There are 2 magic commands: `/textchat/start` and `/textchat/end`.
It starts/ends chat mode.
On chat mode, your spells will be sent as textchat.

### Translation

Set `spell.translate = true` in `config.toml` and set ENV `DEEPL_AUTH_KEY`.

## config.toml

```toml
[spell]
lang       # Language for Chrome/SpeechRecognition
threshold  # How rate you can allow for miss recognition
commands   # An array of command, which has spell and OSC destination and arguments

translate  # true or false; Enable to translate your textchat using DeepL
translate_langs = ["en", "zh", "ko"]  # List of languages, which translate to

[vrchat]
send_port  # 9000 by default
recv_port  # 9001 by default
host       # hostname or IP of VRChat. Usually "localhost" is OK.
```

### spell.commands

A command has 3 fields.

```toml
{
    spell,  # Your speech text
    dest,   # OSC destination (e.g. /avatar/parameters/XXX)
    args,   # Usually, one parameter (int, float, string)
}
```

There are 2 special `dest`, `/textchat/start` and `/textchat/end`.
Once `/textchat/start`, later your speech will be broadcasted as textchat, until `/textchat/end`.
