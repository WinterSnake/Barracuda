#!/usr/bin/python
##-------------------------------##
## Barracuda(server)             ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
import hmac
from datetime import timedelta
from typing import TYPE_CHECKING
from flask import Flask, Response, make_response, request
from .auth import Session, SessionManager, create_session_response
from .db import DBContext, initialize_database
from .models import UserSchema
from .proto import authorization_pb2

if TYPE_CHECKING:
    from .models import User

## Constants
app = Flask(__name__)
sessions = SessionManager(timedelta(minutes=20))


## Functions: [Endpoints]User
@app.delete('/session')
@sessions.get_session_context(
    Response(status=401), Response(status=403), is_context=Session.Context.Any
)
def session_delete(session: Session) -> Response:
    sessions.delete_session(session)
    return Response(status=204)


@app.post('/session/auth')
def session_create_auth() -> Response:
    username = request.form['username'].lower()
    mk_hash = request.files['mk_hash'].read()
    with DBContext.new() as db:
        user = db.user_find(username)
        if not is_valid_user(mk_hash, user):
            return make_response('', 401)
        assert user is not None
        session = sessions.create_session(user.id)
        proto = create_session_response(user, session, is_recovery=False)
        return Response(
            proto.SerializeToString(), status=201,
            mimetype='application/x-protobuf',
        )


@app.post('/session/recovery')
def session_create_recovery() -> Response:
    username = request.form['username'].lower()
    rk_hash = request.files['rk_hash'].read()
    with DBContext.new() as db:
        user = db.user_find(username)
        if not is_valid_user(rk_hash, user, is_recovery=True):
            return make_response('', 401)
        assert user is not None
        session = sessions.create_session(user.id, is_recovery=True)
        proto = create_session_response(user, session, is_recovery=True)
        return Response(
            proto.SerializeToString(), status=201,
            mimetype='application/x-protobuf',
        )


@app.post('/session/upgrade')
@sessions.get_session_context(
    Response(status=401), Response(status=403),
    is_context=Session.Context.Recovery
)
def session_upgrade(session: Session) -> Response:
    mk_hash = request.files['mk_hash'].read()
    mk_blob = request.files['mk_blob'].read()
    with DBContext.new() as db:
        user = db.user_get(session.user_id)
        user = user.with_new_mk(mk_hash, mk_blob)
        db.user_update(user)
    session.upgrade()
    return make_response('', 200)


@app.post('/user')
def user_create() -> Response:
    username = request.form['username'].lower()
    user = UserSchema(
        username,
        request.files['salt'].read(),
        request.files['mk_hash'].read(),
        request.files['mk_blob'].read(),
        request.files['rk_hash'].read(),
        request.files['rk_blob'].read(),
    )
    with DBContext.new() as db:
        if db.user_write(user):
            return make_response('', 201)
        return make_response(f"Username '{username}' already exists", 409)


@app.delete('/user')
@sessions.get_session_context(Response(status=401), Response(status=403))
def user_delete(session: Session) -> Response:
    mk_hash = request.get_data()
    with DBContext.new() as db:
        user = db.user_get(session.user_id)
        if not is_valid_user(mk_hash, user):
            return make_response('', 403)
        db.user_delete(user.id)
        return make_response('', 204)


@app.patch('/user/auth')
@sessions.get_session_context(Response(status=401), Response(status=403))
def user_patch_mk(session: Session) -> Response:
    proto = authorization_pb2.RekeyRequest()
    proto.ParseFromString(request.get_data())
    with DBContext.new() as db:
        user = db.user_get(session.user_id)
        if not is_valid_user(proto.old_hash, user):
            return make_response('', 403)
        user = user.with_new_mk(proto.new_hash, proto.new_blob)
        db.user_update(user)
        return make_response('', 200)


@app.patch('/user/recovery')
@sessions.get_session_context(Response(status=401), Response(status=403))
def user_patch_rk(session: Session) -> Response:
    proto = authorization_pb2.RekeyRequest()
    proto.ParseFromString(request.get_data())
    with DBContext.new() as db:
        user = db.user_get(session.user_id)
        if not is_valid_user(proto.old_hash, user):
            return make_response('', 403)
        user = user.with_new_rk(proto.new_hash, proto.new_blob)
        db.user_update(user)
        return make_response('', 200)


@app.get('/user/salt')
@sessions.get_session_context(
    Response(status=401), Response(status=403), is_context=Session.Context.Any
)
def user_get_salt(session: Session) -> Response:
    with DBContext.new() as db:
        user = db.user_get(session.user_id)
        return Response(
            user.salt, status=200, mimetype='application/octet-stream'
        )


@app.get('/user/<string:username>/salt')
def user_get_salt_named(username: str) -> Response:
    username = username.lower()
    salt: bytes = hmac.digest(
        b'server-salt-generation', username.encode('utf-8'), 'sha256'
    )[:16]
    with DBContext.new() as db:
        user = db.user_find(username)
        if user is not None:
            salt = user.salt
    return Response(salt, status=200, mimetype='application/octet-stream')


## Functions: [Endpoints]Vault
## Functions: Helpers
def is_valid_user(
    _hash: bytes, user: User | None, is_recovery: bool = False
) -> bool:
    if user is None:
        return False
    cmp_hash = user.rk_hash if is_recovery else user.mk_hash
    if hmac.compare_digest(_hash, cmp_hash):
        return True
    return False


## Body
initialize_database("accounts.db")
app.run(debug=True)
