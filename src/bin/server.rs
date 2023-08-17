/*
    Barracuda: Server

    Written By: Ryan Smith
*/
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};

fn main()
{
    let server = TcpListener::bind("127.0.0.1:11234").unwrap();
    for stream in server.incoming()
    {
        match stream
        {
            Ok(stream) => {
                println!("Connection from: {:?}", stream.peer_addr().unwrap());
                handle_client(stream);
            }
            Err(e) => {
                eprintln!("Failed to establish connection with client: '{:?}'", e);
            }
        }
    }
}

fn handle_client(mut stream: TcpStream)
{
    let mut bytes_read: usize = 0;
    let mut buffer: [u8; 4] = [0; 4];
    loop
    {
        bytes_read += stream.read(&mut buffer).unwrap();
        if bytes_read == 0
        {
            break;
        }
        println!("Read {} bytes: [{:?}]", bytes_read, buffer);
        bytes_read = 0;
    }
    println!("Client disconnected..");
}
