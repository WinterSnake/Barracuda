#!/usr/bin/python
##-------------------------------##
## Barracuda(server)             ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
import hmac
from datetime import timedelta
from typing import TYPE_CHECKING
from flask import Flask, Response, request
from .auth import SessionManager, create_session_response
from .db import DBContext, initialize_database
from .models import UserSchema
from .proto import authorization_pb2

if TYPE_CHECKING:
    from .auth import Session

## Constants
app = Flask(__name__)
sessions = SessionManager(timedelta(minutes=20))


## Functions
@app.route('/register', methods=['POST'])
def user_register() -> tuple[str, int]:
    username = request.form['username']
    register = UserSchema(
        username,
        request.files['salt'].read(),
        request.files['mk_hash'].read(),
        request.files['mk_blob'].read(),
        request.files['rk_hash'].read(),
        request.files['rk_blob'].read(),
    )
    with DBContext.new() as db:
        if db.write_user(register):
            return ('', 200)
        return (f"Username '{username}' already exists", 409)


@app.get('/salt/<string:username>')
def user_salt(username: str) -> Response:
    with DBContext.new() as db:
        salt: bytes
        user = db.read_user(username)
        if user is not None:
            salt = user.salt
        else:
            salt = hmac.digest(
                b'server-salt-generation',
                username.encode('utf-8'),
                'sha256'
            )
        return Response(salt, status=200, mimetype='application/octet-stream')


@app.route('/login', methods=['POST'])
def user_login() -> Response:
    username = request.form['username']
    mk_hash = request.files['mk_hash'].read()
    with DBContext.new() as db:
        user = db.read_user(username)
        if user and hmac.compare_digest(user.mk_hash, mk_hash):
            session = sessions.create_session(user.id)
            proto = create_session_response(user, session, False)
            return Response(
                proto.SerializeToString(),
                mimetype='application/x-protobuf',
                status=200
            )
    return Response(status=401)


@app.route('/recovery', methods=['POST'])
def user_recovery() -> Response:
    username = request.form['username']
    rk_hash = request.files['rk_hash'].read()
    with DBContext.new() as db:
        user = db.read_user(username)
        if user and hmac.compare_digest(user.rk_hash, rk_hash):
            session = sessions.create_session(user.id, is_recovery=True)
            proto = create_session_response(user, session, True)
            return Response(
                proto.SerializeToString(),
                mimetype='application/x-protobuf',
                status=200
            )
        return Response(status=401)


@app.patch('/recovery/upgrade')
@sessions.get_session_context(Response(status=403), is_recovery_context=True)
def user_recovery_upgrade(session: Session) -> Response:
    mk_hash = request.files['mk_hash'].read()
    mk_blob = request.files['mk_blob'].read()
    with DBContext.new() as db:
        user = db.get_user(session.user_id)
        user = user.with_new_mk(mk_hash, mk_blob)
        db.update_user(user)
    session.upgrade()
    return Response(status=200)


@app.get('/account/salt')
@sessions.get_session_context(Response(status=403))
def account_salt(session: Session) -> Response:
    with DBContext.new() as db:
        user = db.get_user(session.user_id)
        return Response(
            user.salt, status=200, mimetype='application/octet-stream'
        )


@app.patch('/account/key')
@sessions.get_session_context(Response(status=403))
def account_key(session: Session) -> Response:
    proto = authorization_pb2.RekeyRequest()
    proto.ParseFromString(request.get_data())
    with DBContext.new() as db:
        user = db.get_user(session.user_id)
        if not hmac.compare_digest(user.mk_hash, proto.old_hash):
            return Response(status=403)
        user = user.with_new_mk(proto.new_hash, proto.new_blob)
        db.update_user(user)
        return Response(status=200)


## Body
initialize_database("accounts.db")
app.run(debug=True)
