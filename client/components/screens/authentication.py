#!/usr/bin/python
##-------------------------------##
## Barracuda: UI/Screens         ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Authentication Screen         ##
##-------------------------------##

## Imports
import socket

from kivy.uix.screenmanager import Screen


## Classes
class AuthenticationScreen(Screen):
    """"""

    # -Constructor
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # -Instance Methods: Event
    def on_login(self) -> None:
        print("Login")
        if not self._connect():
            print("error connecting...")
            return
        self.manager.current = "account_list_screen"

    def on_register(self) -> None:
        print("Register")
        if not self._connect():
            print("error connecting...")
            return
        self.manager.current = "account_list_screen"

    # -Instance Methods: Private
    def _connect(self) -> bool:
        print(self.address)

        try:
            self._socket.connect(self.address)
        except ConnectionRefusedError:
            return False
        self._socket.close()
        return True

    # -Properties
    @property
    def address(self) -> tuple[str, int]:
        return (
            self.ids['ip'].text,
            int(self.ids['port'].text)
        )
