/*
    Barracuda: Server

    Written By: Ryan Smith
*/

use std::env;
use std::net::{TcpListener, TcpStream};
use rsa::{RsaPrivateKey};
use barracuda::{Session};

const KEYSIZE: usize = 2048;

fn main() -> std::io::Result<()>
{
    let args: Vec<String> = env::args().collect();
    let address = &args[1];
    let mut rng = rand::thread_rng();
    let private_key = RsaPrivateKey::new(&mut rng, KEYSIZE).expect("failed to generate key");
    let server = TcpListener::bind(address)?;
    println!("Server running at: '{:?}'", server.local_addr()?);
    for stream in server.incoming()
    {
        handle_client(stream?, &private_key);
    }
    Ok(())
}

fn handle_client(stream: TcpStream, private_key: &RsaPrivateKey)
{
    let peer = stream.peer_addr().unwrap();
    println!("Connected with client: '{:?}'", peer);
    let _session = Session::new(stream, private_key.clone());
    println!("Closing connection with client: '{:?}'..", peer);
}
