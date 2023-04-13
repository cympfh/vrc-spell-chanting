# VRC/spell-chanting

__This is Experimental__

VRChat/OSC by Speech Recognition

## ARCHITECTURE

```
[Google Chrome]--(speech recognition)->[Python]--(OSC)->[VRChat]
```

## Requirements

- Python3.11
    - Plan: also works on Docker
- Google Chrome browser
    - or other chromium can work? (not tested)

## Setup & Startup

Spell and OSC destinations are defined in `config.toml`.
Please edit it at first.

```bash
# on local
make build
make serve
```

```bash
# on docker
make build-docker
make serve-docker
```

And open `localhost:8080`.
