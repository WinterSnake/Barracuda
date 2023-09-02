/*
    Barracuda: CLI/REPL Client

    Written By: Ryan Smith
*/

use std::io;
//use std::io::{Read, Write};
use std::net::{TcpStream};
use rsa::{RsaPrivateKey};
use barracuda::{Session};
//use barracuda::{protocol, Session};

fn main()
{
    if let Ok(stream) = TcpStream::connect("127.0.0.1:11234")
    {
        let mut rng = rand::thread_rng();
        let private_key = RsaPrivateKey::new(&mut rng, 2048).expect("failed to generate key");
        let _session = Session::new(stream, private_key);
        let stdin = io::stdin();
        loop
        {
            let mut buffer = String::new();
            let _ = stdin.read_line(&mut buffer);
            match buffer.trim()
            {
                "exit" => break,
                "login" => {
                    println!("Logging in as user..");
                },
                _ => println!("Unknown command '{}'", buffer.trim())
            }
        }
    }
    else { eprintln!("Could not establish a connection to the server.."); }
}
