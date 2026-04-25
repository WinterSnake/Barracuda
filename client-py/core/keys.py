##-------------------------------##
## Barracuda(client)             ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Core: Keys                    ##
##-------------------------------##

## Import
import hmac
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING
import argon2
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

if TYPE_CHECKING:
    from typing import Self

## Constants
__all__ = ("MasterKey", "RecoveryKey", "VaultKey")


## Functions
def encrypt(key: bytes, data: bytes) -> bytes:
    """Performs an AES-GCM encryption and prepends a random nonce"""
    cipher = AESGCM(key)
    nonce = os.urandom(12)
    return nonce + cipher.encrypt(nonce, data, None)


def decrypt(key: bytes, blob: bytes) -> bytes:
    """Extracts the nonce and decrypts AES-GCM ciphertext"""
    cipher = AESGCM(key)
    nonce = blob[:12]
    blob = blob[12:]
    return cipher.decrypt(nonce, blob, None)


## Classes
@dataclass(frozen=True, slots=True)
class MasterKey:
    """
    Root key derived from password; used to manage
    authorization and vault key security.
    """
    # -Instance Methods
    def encrypt_vault_key(self, vk: VaultKey) -> bytes:
        '''Encrypt VaultKey using recovery and return tagged cipher blob'''
        return encrypt(self._key, vk._key)

    def decrypt_vault_key(self, blob: bytes) -> VaultKey:
        '''Decrypt tagged cipher blob using recovery and return reconstructed VaultKey'''
        return VaultKey(decrypt(self._key, blob))

    def generate_hash(self, username: str, salt: bytes) -> bytes:
        '''Generate a hash for client-server authentication using key A'''
        return hmac.digest(
            self._key,
            username.encode('utf-8') + salt,
            'sha256'
        )

    # -Class Methods
    @classmethod
    def derive_from(cls, password: str, salt: bytes) -> Self:
        '''Derives a 64-byte hash from a password and salt using Argon2id'''
        return cls(argon2.low_level.hash_secret_raw(
            password.encode('utf-8'),
            salt,
            time_cost=8,
            memory_cost=1024 * 128,
            parallelism=4,
            hash_len=64,
            type=argon2.low_level.Type.ID,
        ))

    # -Properties
    _key: bytes

    @property
    def key_a(self) -> bytes:
        return self._key[:32]

    @property
    def key_b(self) -> bytes:
        return self._key[32:]


@dataclass(frozen=True, slots=True)
class RecoveryKey:
    """
    Used to recover vault access as a secondary context.
    Bypasses password authentication.
    """
    # -Instance Methods
    def encrypt_vault_key(self, vk: VaultKey) -> bytes:
        '''Encrypt VaultKey using recovery and return tagged cipher blob'''
        return encrypt(self._key, vk._key)

    def decrypt_vault_key(self, blob: bytes) -> VaultKey:
        '''Decrypt tagged cipher blob using recovery and return reconstructed VaultKey'''
        return VaultKey(decrypt(self._key, blob))

    def generate_hash(self, username: str, salt: bytes) -> bytes:
        '''Generate a hash for client-server authentication using recovery key'''
        return hmac.digest(
            self._key,
            username.encode('utf-8') + salt,
            'sha256'
        )

    # -Class Methods
    @classmethod
    def new(cls) -> Self:
        return cls(os.urandom(32))

    # -Properties
    _key: bytes

    @property
    def hex_str(self) -> str:
        return self._key.hex()


@dataclass(frozen=True, slots=True)
class VaultKey:
    """Symmetric key used for bulk data encryption"""
    # -Instance Methods
    def encrypt(self, data: bytes) -> bytes:
        '''Encrypt data using the vault key'''
        return encrypt(self._key, data)

    def decrypt(self, blob: bytes) -> bytes:
        '''Decrypt data using the vault key'''
        return decrypt(self._key, blob)

    # -Class Methods
    @classmethod
    def new(cls) -> Self:
        return cls(os.urandom(32))

    # -Properties
    _key: bytes
