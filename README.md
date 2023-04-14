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
