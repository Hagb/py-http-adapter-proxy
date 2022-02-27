from socket import MSG_WAITALL, socket
from struct import Struct
from pickle import dumps, loads
# from itertools import chain
uint8 = Struct("B")
uint32 = Struct(">I")


def recvall(conn: socket, size: int) -> bytes:
    return b''.join(
        conn.recv(min(1024, rest), MSG_WAITALL) for rest in range(size, 0, -1024)
    )


def recvobjs(conn: socket) -> tuple:
    return tuple(
        loads(
            recvall(
                conn,
                uint32.unpack(conn.recv(uint32.size, MSG_WAITALL))[0]
            )
        )
        for _ in range(uint8.unpack(conn.recv(uint8.size, MSG_WAITALL))[0])
    )


def sendobjs(conn: socket, *objs):
    conn.send(uint8.pack(len(objs)))
    for obj in objs:
        data = dumps(obj)
        conn.send(uint32.pack(len(data)))
        conn.sendall(data)
