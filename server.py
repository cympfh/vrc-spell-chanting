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


class Spell(BaseModel):
    text: str


def similar_spell(spell: Spell) -> tuple[bool, float, dict]:
    dist, cmd = min(
        [
            (distance(spell.text.lower(), cmd["spell"].lower()) / len(spell.text), cmd)
            for cmd in config["spell"]["commands"]
        ],
        key=lambda t: t[0],
    )
    ok = dist <= config["spell"]["threshold"]
    return ok, dist, cmd


class OSC:

    client: udp_client.SimpleUDPClient
    chating: bool

    def __init__(self, config):
        host = config["vrchat"]["host"]
        port = config["vrchat"]["send_port"]
        logger.info("Connecting to host=%s, port=%s", host, port)
        self.client = udp_client.SimpleUDPClient(host, port)
        self.chating = False

    def chat_mode(self, dest: str) -> bool:
        if dest == "/textchat/start":
            self.chating = True
            return True
        elif dest == "/textchat/end":
            self.chating = False
            return True
        else:
            return False

    def send(self, dest: str, args: list):
        self.client.send_message(dest, args)

    def chat(self, message: str):
        self.client.send_message("/chatbox/input", [message, True])


client = OSC(config)


@app.post("/api/spell")
async def post_spell(spell: Spell):
    """Run spell"""
    logger.info("POST spell: %s", spell)
    assert len(spell.text) > 0
    ok, dist, cmd = similar_spell(spell)

    if ok and client.chat_mode(cmd["dest"]):
        if client.chating:
            logger.info("Start to chat")
            return {"status": 200, "spell": "[chat mode]"}
        else:
            logger.info("End to chat")
            return {"status": 200, "spell": "[spell mode]"}
    elif client.chating:
        logger.info("Chat: %s", spell.text)
        client.chat(spell.text)
        return {"status": 200, "spell": "[chat mode]"}
    elif ok:
        logger.info("Running Spell: %s with dist=%s", cmd, dist)
        client.send(cmd["dest"], cmd["args"])
        return {"status": 200, "spell": cmd["spell"]}
    else:
        logger.warn("Cannot found similar spells")
        logger.warn("Most similar one is: %s with dist=%s", cmd, dist)
        return {"status": 404}


@app.get("/api/lang")
async def get_lang() -> str:
    return config["spell"]["lang"]


@app.get("/api/spells")
async def get_spells() -> list[dict]:
    return config["spell"]["commands"]


app.mount("/", MountFiles(directory="web/public", html=True), name="static")
