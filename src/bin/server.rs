/*
    Barracuda: Server

    Written By: Ryan Smith
*/

use std::net::{TcpListener, TcpStream};
use rsa::{RsaPrivateKey};
use barracuda::{Session};

fn main()
{
    let mut rng = rand::thread_rng();
    let private_key = RsaPrivateKey::new(&mut rng, 2048).expect("failed to generate key");
    let server = TcpListener::bind("127.0.0.1:11234").unwrap();
    for stream in server.incoming()
    {
        match stream
        {
            Ok(stream) => handle_stream(stream, &private_key),
            Err(e) => eprintln!("Failed to establish connection with client: '{:?}'", e)
        }
    }
}

fn handle_stream(stream: TcpStream, private_key: &RsaPrivateKey)
{
    println!("Connection from: '{:?}'", stream.peer_addr().unwrap());
    let _session = Session::new(stream, private_key.clone());
    loop
    {

    }
}
