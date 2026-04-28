##-------------------------------##
## Barracuda(server)             ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Authorization                 ##
##-------------------------------##

## Imports
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import IntFlag, auto
from functools import wraps
from typing import TYPE_CHECKING
from flask import request
from .proto import authorization_pb2

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, ClassVar, Self
    from .db import DBContext
    from .models import User


## Functions
def create_session_response(
    user: User, token: str, is_recovery: bool
) -> authorization_pb2.SessionResponse:
    """Maps user mk vault key blob and auth/refresh token to Session proto"""
    proto = authorization_pb2.SessionResponse()
    proto.token = token
    proto.vault_key = user.rk_blob if is_recovery else user.mk_blob
    return proto


## Classes
@dataclass(slots=True)
class Session:
    """Sliding window session token"""
    # -Instance Methods
    def refresh(self, delta: timedelta) -> None:
        self.expires_at = datetime.now(timezone.utc) + delta

    def upgrade(self) -> None:
        self.context = Session.Context.Full

    # -Class Methods
    @classmethod
    def new(cls, _id: int, delta: timedelta, context: Session.Context) -> Self:
        dt = datetime.now(timezone.utc)
        return cls(_id, os.urandom(32).hex(), context, dt, dt + delta)

    # -Properties
    user_id: int
    token: str
    context: Session.Context
    created_at: datetime
    expires_at: datetime

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at

    # -Sub-Classes
    class Context(IntFlag):
        Full = auto()
        Recovery = auto()
        Any = Full | Recovery


class SessionManager:
    # -Constructor
    def __init__(self, auth_delta: timedelta) -> None:
        self._active_sessions: dict[str, Session] = {}
        self._auth_delta: timedelta = auth_delta

    # -Instance Methods
    def clear_sessions(self, expired_only: bool = True) -> None:
        if not expired_only:
            self._active_sessions = {}
            return
        tokens = tuple(
            session.token
            for session in self._active_sessions.values()
            if session.is_expired
        )
        for token in tokens:
            del self._active_sessions[token]

    def create_session(self, _id: int, is_recovery: bool = False) -> str:
        '''
        Creates an authorized session for API usage.
        Can either be a non-recovery or recovery typed session.
        '''
        context = Session.Context.Recovery if is_recovery else Session.Context.Full
        session = Session.new(_id, self._auth_delta, context)
        self._active_sessions[session.token] = session
        return session.token

    def delete_session(self, session: Session) -> None:
        del self._active_sessions[session.token]

    # -Instance Methods: Decorator
    def get_session_context[T, **P](
        self,
        auth_error_value: T,
        ctx_error_value: T,
        is_context: Session.Context = Session.Context.Full,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        def decorate(func: Callable[P, T]) -> Callable[P, T]:
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                auth_str = request.headers.get('Authorization', None)
                if auth_str is None:
                    return auth_error_value
                auth = auth_str.split(' ')
                if len(auth) != 2:
                    return auth_error_value
                scheme, token = auth
                if scheme.lower() != 'bearer':
                    return auth_error_value
                session = self._active_sessions.get(token, None)
                # -Check if session in valid state
                if not session:
                    return auth_error_value
                elif session.is_expired:
                    self.delete_session(session)
                    return auth_error_value
                elif session.context not in is_context:
                    self.delete_session(session)
                    return ctx_error_value
                # -Slide session expiration out by new delta
                session.refresh(self._auth_delta)
                # -TODO: Concat P + Session
                kwargs['session'] = session
                return func(*args, **kwargs)
            return wrapper
        return decorate

    # -Class Properties
    __slots__: ClassVar[list[str]] = [
        '_active_sessions', '_auth_delta'
    ]
