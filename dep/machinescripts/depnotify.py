#!/usr/bin/python

# A simple python function for writing to DEPNotify's log file.
# In order to pass more complex strings, you must use r"TEXT". r tells python
# to pass the literal string vs an interpreted string.

# Written by Erik Gomez


def deplog(text):
    depnotify = "/private/var/tmp/depnotify.log"
    with open(depnotify, "a+") as log:
        log.write(text + "\n")


def main():
    deplog(r"Command: MainTitle: We're testing literal strings!")
    deplog(r"Command: MainText: We're testing new lines!\n\n"
           r"email@domain.com\n#InstallApplications on Macadmin slack")

    deplog("Status: Testing normal DEP strings.")
    deplog("Command: Quit")
    deplog("Command: Logout: Please logout now to start the disk encryption "
           "process.")


if __name__ == '__main__':
    main()
