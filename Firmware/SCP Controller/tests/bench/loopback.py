#!/usr/bin/env python3
"""Talks to the pico2-loopback build's test console over its USB serial port.

  loopback.py [--port /dev/cu.usbmodemNNNN] COMMAND [COMMAND ...]

Each COMMAND (quote it if it has spaces: "soak 2 3600") is sent as a line, and
everything the console answers is printed, up to its "END" line. The exit
status is 1 if an answer has "RESULT FAIL" in it, or never ends.

Python's standard library only: termios on the port's file descriptor."""
import argparse
import glob
import os
import select
import sys
import termios
import time


def open_port(path):
    fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    attrs = termios.tcgetattr(fd)
    attrs[0] = 0                                    # iflag: raw
    attrs[1] = 0                                    # oflag
    attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
    attrs[3] = 0                                    # lflag: no echo, no canonical mode
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    termios.tcflush(fd, termios.TCIOFLUSH)
    return fd


def read_until_end(fd, timeout):
    buf = b''
    deadline = time.time() + timeout
    while time.time() < deadline:
        r, _, _ = select.select([fd], [], [], 0.5)
        if r:
            try:
                chunk = os.read(fd, 4096)
            except BlockingIOError:
                continue
            buf += chunk
            text = chunk.decode(errors='replace').replace('\r\n', '\n')
            sys.stdout.write(text)
            sys.stdout.flush()
            if b'END\r\n' in buf:
                return buf.decode(errors='replace')
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port')
    ap.add_argument('--timeout', type=float, default=7200)
    ap.add_argument('commands', nargs='+')
    a = ap.parse_args()
    port = a.port or (sorted(glob.glob('/dev/cu.usbmodem*')) or [None])[0]
    if not port:
        sys.exit('no /dev/cu.usbmodem* port: is the Pico 2 plugged in and running the loopback build?')
    fd = open_port(port)
    time.sleep(0.3)
    # The banner on connecting, then a blank line to clear any half line.
    os.write(fd, b'\r')
    read_until_end(fd, 1)
    status = 0
    for cmd in a.commands:
        print(f'> {cmd}')
        os.write(fd, cmd.encode() + b'\r')
        answer = read_until_end(fd, a.timeout)
        if answer is None:
            print(f'\nno END after "{cmd}"')
            status = 1
            break
        if 'RESULT FAIL' in answer:
            status = 1
    os.close(fd)
    return status


if __name__ == '__main__':
    sys.exit(main())
