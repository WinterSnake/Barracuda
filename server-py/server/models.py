##-------------------------------##
## Barracuda(server)             ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Models                        ##
##-------------------------------##

## Imports
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self


## Classes
@dataclass(frozen=True, slots=True)
class User:
    # -Instance Methods
    def with_new_mk(self, _hash: bytes, blob: bytes) -> Self:
        return replace(self, mk_hash=_hash, mk_blob=blob)

    # -Properties
    id: int
    username: str
    salt: bytes
    mk_hash: bytes
    mk_blob: bytes
    rk_hash: bytes
    rk_blob: bytes


@dataclass(frozen=True, slots=True)
class UserSchema:
    # -Properties
    username: str
    salt: bytes
    mk_hash: bytes
    mk_blob: bytes
    rk_hash: bytes
    rk_blob: bytes
