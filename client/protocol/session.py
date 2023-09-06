#!/usr/bin/python
##-------------------------------##
## Barracuda: Protocol           ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Session                       ##
##-------------------------------##

## Imports
import socket
from pathlib import Path

import rsa

from .message import Message

## Constants
KEYSIZE: int = 2000


## Classes
class Session:
    """"""

    # -Constructor
    def __init__(self, keys_folder: Path | None = None) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._public_key: rsa.PublicKey
        self._private_key: rsa.PrivateKey
        if not keys_folder:
            pubkey, prvkey = rsa.newkeys(KEYSIZE)
            self._public_key = pubkey
            self._private_key = prvkey
        pub_key_der = self._public_key._save_pkcs1_der()
        print(len(pub_key_der))
        print(pub_key_der)

    # -Instance Methods
    def send(msg: Message) -> None:
        ''''''
        pass

    def recv() -> Message:
        ''''''
        pass
