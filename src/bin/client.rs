/*
    Barracuda: Client

    A REPL client implementation

    Written By: Ryan Smith
*/
use std::io;
use std::io::{Read, Write};
use std::net::{TcpStream};

fn main()
{
    if let Ok(mut client) = TcpStream::connect("127.0.0.1:11234")
    {
        println!("Connected to server, exiting!");
        let stdin = io::stdin();
        loop
        {
            // Get input
            let mut buffer = String::new();
            let _ = stdin.read_line(&mut buffer);
            match buffer.trim()
            {
                "exit" => break,
                "login" => login(&mut client),
                _ => println!("Unknown command '{}'", buffer.trim())
            }
        }
    }
    else
    {
        eprintln!("Could not connect to server..");
    }
}

fn login(stream: &mut TcpStream)
{
    let mut bytes_written: usize = 0;
    let msg: [u8; 4] = [1, 1, 1, 2];
    bytes_written += stream.write(&msg).unwrap();
    println!("Bytes written: {}", bytes_written);
}
