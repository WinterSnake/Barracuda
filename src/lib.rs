/*
    Barracuda

    Written By: Ryan Smith
*/

use std::net::{TcpStream};
use rsa::{RsaPrivateKey, RsaPublicKey};

pub mod protocol;

use protocol::message::{Message};

pub struct Session
{
    stream: TcpStream,
    private_key: RsaPrivateKey,
    public_key: RsaPublicKey,
    connection_key: Option<RsaPublicKey>,
}

impl Session
{
    // Constructors
    pub fn new(stream: TcpStream, private_key: RsaPrivateKey) -> Session
    {
        let public_key = RsaPublicKey::from(&private_key);
        Session {
            stream: stream,
            private_key: private_key,
            public_key: public_key,
            connection_key: None,
        }
    }
    // Methods
    pub fn send(&mut self, _message: Message)
    {

    }

    pub fn recv(&self) -> Message
    {
        Message::SendKey(&self.public_key)
    }
}
