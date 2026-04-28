#!/usr/bin/python
##-------------------------------##
## Barracuda(client)             ##
## Written By: Ryan Smith        ##
##-------------------------------##
## REPL                          ##
##-------------------------------##

## Imports
import asyncio
from getpass import getpass
from aiohttp import ClientSession
from barracuda.core import BarracudaClient


## Functions
def main() -> None:
    asyncio.run(_main(get_base_url()))


async def _main(url: str) -> None:
    async with ClientSession(url) as session:
        client: BarracudaClient | None = None
        while True:
            command = input("> ")
            # -[Command]Exit|Quit
            if command in ('e', 'q', "exit", "quit"):
                break
            # -[Command]Help
            elif command in ('h', "help"):
                print(get_help_commands(client is not None))
                continue
            # -[Context]Logged Out
            if client is None:
                command, *args = command.split(' ')
                # -[Command]Register
                if command in ('r', "register"):
                    if len(args) != 1:
                        print("Must provide exactly one argument to register")
                        continue
                    password = getpass("Password: ")
                    try:
                        key = await BarracudaClient.register(session, args[0], password)
                        print(f"Registration successful. Recovery key: '{key}'")
                    except:
                        print("Failed to register account")
                    continue
                # -[Command]Login
                elif command in ('l', "login"):
                    if len(args) != 1:
                        print("Must provide exactly one argument to login")
                        continue
                    password = getpass("Password: ")
                    try:
                        client = await BarracudaClient.login(session, args[0], password)
                        print(f"Logged in as '{client.username}'")
                    except:
                        print(f"Failed to login as '{args[0]}'")
                    continue
                # -[Command]Recover
                elif command in ('R', "recover"):
                    if len(args) != 2:
                        print("Must provide exactly two arguments to recover")
                        continue
                    password = getpass("New Password: ")
                    try:
                        client = await BarracudaClient.recover(
                            session, args[0], args[1], password
                        )
                        print(f"Recovered and logged in as '{client.username}'")
                    except:
                        print(f"Failed to recover '{args[0]}'")
                    continue
            # -[Context]Logged In
            else:
                if command in ('l', "logout"):
                    await client.logout()
                    client = None
                    print("Logged out")
                    continue
                elif command in ('p', "password"):
                    old_password = getpass("Old Password: ")
                    new_password = getpass("New Password: ")
                    try:
                        await client.update_password(old_password, new_password)
                        print("Password changed successfully")
                    except:
                        print("Failed to change password")
                    continue
                elif command in ('r', "recovery"):
                    password = getpass("Password: ")
                    try:
                        key = await client.renew_recovery_key(password)
                        print(f"New recovery key: {key}")
                    except:
                        print("Failed to change recovery key")
                    continue
                elif command in ('d', "delete"):
                    password = getpass("Password: ")
                    try:
                        await client.delete(password)
                        client = None
                        print("Account deleted")
                    except:
                        print("Failed to delete account")
                    continue
            print(f"Unknown command '{command}'")


def get_base_url() -> str:
    """Load or get base URL for Barracuda server"""
    # -TODO: store url location
    url = input("Enter Barracuda URL: ")
    return url


def get_help_commands(is_authenticated: bool) -> str:
    constants = (
        "e, q, exit, quit: End the program",
        "h, help: Get current available commands and their arguments",
    )
    if is_authenticated:
        return '\n'.join((*constants, *(
            "l, logout: Logout of account",
            "p, password: Change current password",
            "r, recovery: Change current recovery key",
            "d, delete: Delete current account",
        )))
    return '\n'.join((*constants, *(
        "r, register <username>: Register an account with given username and password",
        "l, login <username>: Log into an account using username and password",
        "R, recover <username> <key>: Recover an account with a given username and password",
    )))


## Body
if __name__ == "__main__":
    main()
