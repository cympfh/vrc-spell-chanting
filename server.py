import logging
import subprocess
import tomllib

from fastapi import FastAPI
from Levenshtein import distance
from pydantic import BaseModel
from pythonosc import udp_client

from util.mount import MountFiles

app = FastAPI()
logger = logging.getLogger("uvicorn")
config = tomllib.load(open("./config.toml", "rb"))


def ipwin() -> str:
    cmd = r"ipconfig.exe | nkf | grep IPv4 | grep 192 | grep -o '192[0-9\.]*' | tr -d ' \n\r'"
    return subprocess.run(cmd, shell=True, capture_output=True).stdout.decode().strip()


if config["vrchat"]["host"] == "$WIN":
    config["vrchat"]["host"] = ipwin()


logger.info(config)


class OSC:
    def __init__(self, config):
        self.client = udp_client.SimpleUDPClient(
            config["vrchat"]["host"], config["vrchat"]["send_port"]
        )

    def send(self, dest: str, args: list):
        logger.info("send: %s %s", dest, args)
        self.client.send_message(dest, args)


client = OSC(config)


class Spell(BaseModel):
    text: str


@app.post("/api/spell")
async def post_spell(spell: Spell):
    """Run spell"""
    logger.info("Running spell: %s", spell)
    d, cmd = min(
        [
            (distance(spell.text, cmd["spell"]) / len(spell.text), cmd)
            for cmd in config["spell"]["commands"]
        ],
        key=lambda t: t[0],
    )
    if d > config["spell"]["threshold"]:
        logger.warn("Cannot found similar spells")
        logger.warn("Most similar is: %s with d=%s", cmd, d)
        return {"status": 404}
    else:
        logger.info("Similar spell found: %s with d=%s", cmd, d)
        client.send(cmd["dest"], cmd["args"])
        return {"status": 200}


@app.get("/api/spells")
async def get_spells() -> list[dict]:
    return config["spell"]["commands"]


app.mount("/", MountFiles(directory="web/public", html=True), name="static")
