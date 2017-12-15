#!/usr/bin/python

# This kills system preferences and is useful for when you are using dep nag
# with a tool like DEPNotify. System Preferences will more than likely be up
# and in the way.

# Written by Erik Gomez
import os
import signal
import subprocess


def get_PID(processname):
    try:
        cmd = ['/usr/bin/pgrep', '-l', processname]
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = proc.communicate()
        return output.split(' ')[0]
    except Exception:
        return None


def main():
    # Kill System Preferences as it's probably open
    prefspid = get_PID('System Preferences')
    if prefspid:
        os.kill(int(prefspid), signal.SIGKILL)


if __name__ == '__main__':
    main()
