#!/usr/bin/python
##-------------------------------##
## Barracuda: UI/Screens         ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
from .about import AboutScreen
from .account.create import CreateScreen as AccountCreateScreen
from .account.detail import DetailScreen as AccountDetailScreen
from .account.list import ListScreen as AccountListScreen
from .authentication import AuthenticationScreen

## Constants
__all__: tuple[str, ...] = (
    "AboutScreen",
    "AccountCreateScreen", "AccountDetailScreen", "AccountListScreen",
    "AuthenticationScreen",
)
