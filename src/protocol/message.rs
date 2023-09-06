/*
    Barracuda: Protocol
    - Message

    Written By: Ryan Smith
*/

use rsa::{RsaPublicKey};

const MessageExchangeKeyHeader: usize = 0x0001;

pub enum Message
{
    None,
    ExchangeKey(RsaPublicKey)
}

impl Message
{
    fn from_bytes() -> Message
    {
        Message::None
    }
}
