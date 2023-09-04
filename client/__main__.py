#!/usr/bin/python
##-------------------------------##
## Barracuda: Client             ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
import asyncio
import sys
from pathlib import Path

from kivy.app import App

from .protocol import Session

## Constants
SESSION: Session = Session()


## Functions
def client_kivy() -> None:
    asyncio.run(BarracudaApp().async_run())


def client_repl() -> None:
    while True:
        command: str = input("Command: ")
        match command:
            case "connect":
                ip: str = input("\t Enter Ip: ")
                port: str = input("\t Enter Port: ")
                connected: bool = SESSION.connect(ip, port)
            case "exit":
                break
            case "help":
                print("Help menu..")
            case _:
                print(f"Unknown command '{command}'")


def main() -> None:
    if sys.argv[1] in ("-r", "--repl"):
        client_repl()
    else:
        client_kivy()


## Classes
class BarracudaApp(App):
    """Barracuda client implementation using Kivy GUI framework"""

    # -Instance Methods
    def build(self) -> None:
        self.title = "Barracuda"
        return None


## Body
main()
