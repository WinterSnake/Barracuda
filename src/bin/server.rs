/*
    Barracuda: Server

    Written By: Ryan Smith
*/

use std::net::{TcpListener, TcpStream};
use barracuda::protocol;

fn main()
{
    let server = TcpListener::bind("127.0.0.1:11234").unwrap();
    for stream in server.incoming()
    {
        match stream
        {
            Ok(stream) => handle_stream(stream),
            Err(e) => eprintln!("Failed to establish connection with client: '{:?}'", e)
        }
    }
}

fn handle_stream(mut stream: TcpStream)
{
    println!("Connection from: '{:?}'", stream.peer_addr().unwrap());
    loop
    {

    }
}
