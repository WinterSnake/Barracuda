#!/usr/bin/python
##-------------------------------##
## Barracuda: Protocol           ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Message                       ##
##-------------------------------##

## Imports
from __future__ import annotations
from enum import IntEnum

import rsa


## Classes
class Message:
    """"""

    # -Constructor
    def __init__(self, type_: Message.Type, *args) -> None:
        self.type: Message.Type = type_
        match type_:
            case Message.Type.SendKey:
                self.key: rsa.PublicKey = args[0]

    # -Instance Methods
    def as_bytes(self) -> bytes:
        ''''''
        pass

    # -Class Methods
    @classmethod
    def from_bytes(cls) -> Message:
        pass

    @classmethod
    def exchange_key(cls, key: rsa.PublicKey) -> Message:
        ''''''
        cls(Message.Type.ExchangeKey, key)

    # -Sub-Classes
    class Type(IntEnum):
        ''''''
        ExchangeKey = 0x0001
