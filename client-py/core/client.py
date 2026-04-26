##-------------------------------##
## Barracuda(client)             ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Core: Client                  ##
##-------------------------------##

## Import
import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING
import aiohttp
from .keys import MasterKey, RecoveryKey, VaultKey
from .proto import authorization_pb2

if TYPE_CHECKING:
    from typing import Self


## Classes
class BarracudaClient:
    """
    Stateful client implementation for the Barracuda password manager.
    Manages the http/s session and cryptography regarding it's keys.
    """

    # -Constructor
    def __init__(
        self, session: aiohttp.ClientSession,
        username: str, vk: VaultKey
    ) -> None:
        self._session: aiohttp.ClientSession = session
        self.username: str = username
        self._vk: VaultKey = vk

    # -Instance Methods
    async def update_password(self, old_password: str, new_password: str) -> None:
        # -Crypto
        async with self._session.get(f'/account/salt') as resp:
            assert resp.ok # -TODO: Error handling
            salt: bytes = await resp.read()
        mk = MasterKey.derive_from(old_password, salt)
        old_hash = mk.generate_hash(self.username, salt)
        mk = MasterKey.derive_from(new_password, salt)
        new_hash = mk.generate_hash(self.username, salt)
        new_blob = mk.encrypt_vault_key(self._vk)
        # -Http
        proto = authorization_pb2.RekeyRequest()
        proto.old_hash = old_hash
        proto.new_hash = new_hash
        proto.new_blob = new_blob
        data = proto.SerializeToString()
        async with self._session.patch('/account/key', data=data) as resp:
            assert resp.ok # -TODO: Error handling

    # -Class Methods
    @classmethod
    async def login(
        cls, session: aiohttp.ClientSession, username: str, password: str
    ) -> Self:
        '''Derive master key from password and unwrap vault key via server auth'''
        # -Crypto
        async with session.get(f'/salt/{username}') as resp:
            assert resp.ok # -TODO: Error handling
            salt: bytes = await resp.read()
        mk = MasterKey.derive_from(password, salt)
        mk_hash = mk.generate_hash(username, salt)
        # -Http: Authorization
        form = aiohttp.FormData()
        form.add_field('username', username)
        form.add_field('mk_hash', mk_hash, filename="mk_hash", content_type='application/octet-stream')
        async with session.post('/login', data=form) as resp:
            assert resp.ok # -TODO: Error handling
            proto_login = authorization_pb2.SessionResponse()
            proto_login.ParseFromString(await resp.read())
        vk = mk.decrypt_vault_key(proto_login.vault_key)
        session.headers['Authorization'] = f"Bearer {proto_login.token}"
        return cls(session, username, vk)

    @classmethod
    async def recover(
        cls, session: aiohttp.ClientSession, username: str,
        recovery_hex_str: str, new_password: str
    ) -> Self:
        '''Bypass master password using recovery key to re-wrap vault under new password'''
        # -Crypto: Recovery
        async with session.get(f'/salt/{username}') as resp:
            assert resp.ok # -TODO: Error handling
            salt: bytes = await resp.read()
        rk = RecoveryKey(bytes.fromhex(recovery_hex_str))
        rk_hash = rk.generate_hash(username, salt)
        # -Http: Authorization
        form = aiohttp.FormData()
        form.add_field('username', username)
        form.add_field('rk_hash', rk_hash, filename="rk_hash", content_type='application/octet-stream')
        async with session.post('/recovery', data=form) as resp:
            assert resp.ok # -TODO: Error handling
            proto_recovery = authorization_pb2.SessionResponse()
            proto_recovery.ParseFromString(await resp.read())
        vk = rk.decrypt_vault_key(proto_recovery.vault_key)
        session.headers['Authorization'] = f"Bearer {proto_recovery.token}"
        # -Crypto: Master
        mk = MasterKey.derive_from(new_password, salt)
        mk_hash = mk.generate_hash(username, salt)
        mk_blob = mk.encrypt_vault_key(vk)
        # -Http: Upgrade
        form = aiohttp.FormData()
        form.add_field('mk_hash', mk_hash, filename="mk_hash", content_type='application/octet-stream')
        form.add_field('mk_blob', mk_blob, filename="mk_blob", content_type='application/octet-stream')
        async with session.patch('/recovery/upgrade', data=form) as resp:
            assert resp.ok # -TODO: Error handling
        return cls(session, username, vk)

    # -Static Methods
    @staticmethod
    async def register(
        session: aiohttp.ClientSession, username: str, password: str
    ) -> str:
        '''Requests new vault account initialization and returns recovery key'''
        # -Crypto
        salt = os.urandom(16)
        vk = VaultKey.new()
        mk = MasterKey.derive_from(password, salt)
        mk_hash = mk.generate_hash(username, salt)
        mk_blob = mk.encrypt_vault_key(vk)
        rk = RecoveryKey.new()
        rk_hash = rk.generate_hash(username, salt)
        rk_blob = rk.encrypt_vault_key(vk)
        # -Http
        form = aiohttp.FormData()
        form.add_field('username', username)
        form.add_field('salt', salt, filename="salt", content_type='application/octet-stream')
        form.add_field('mk_hash', mk_hash, filename="mk_hash", content_type='application/octet-stream')
        form.add_field('mk_blob', mk_blob, filename="mk_blob", content_type='application/octet-stream')
        form.add_field('rk_hash', rk_hash, filename="rk_hash", content_type='application/octet-stream')
        form.add_field('rk_blob', rk_blob, filename="rk_blob", content_type='application/octet-stream')
        async with session.post('/register', data=form) as resp:
            assert resp.ok # -TODO: Error handling
        return rk.hex_str
