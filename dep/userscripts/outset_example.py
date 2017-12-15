#!/usr/bin/python

# This example script uses a subprocess function, with an option to pass
# unlimited arguments. This allows you to essentially pass any command line
# tool arguments. While this shouldn't be used to for any tool you want its
# output from, it works for almost any tool. In this example we use outset.

# Written by Erik Gomez
import subprocess


def cheapsubprocess(*arg):
    # Use *arg to pass unlimited variables to command.
    cmd = arg
    run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = run.communicate()
    return output


def main():
    cheapsubprocess('/usr/local/outset/outset', '--login-once')


if __name__ == '__main__':
    main()
