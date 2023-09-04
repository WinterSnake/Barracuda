/*
    Barracuda: Protocol
    - Message

    Written By: Ryan Smith
*/

use rsa::{RsaPublicKey};

pub enum Message<'a>
{
    None,
    SendKey(&'a RsaPublicKey)
}

impl Message<'_>
{
}
