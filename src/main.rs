/*
    Barracuda: Server

    Written By: Ryan Smith
*/

use std::net::{Ipv4Addr, SocketAddrV4, TcpListener, TcpStream};

fn main()
{
    let addr = Ipv4Addr::new(127, 0, 0, 1);
    let socket = SocketAddrV4::new(addr, 11123);
    let server = TcpListener::bind(socket).unwrap();
    for conn in server.incoming()
    {
        match conn
        {
            Ok(conn) => {
                println!("Established connection from: {:?}", conn.peer_addr().unwrap());
            }
            Err(e) => eprintln!("Could not accept client: {:?}", e)
        }
    }
    println!("Hello, world!");
}
