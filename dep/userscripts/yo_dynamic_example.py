#!/usr/bin/python
# -*- coding: utf-8 -*-

# A simple example on how to dynamically send a yo notification based on the
# 501 User's firstname. If you want to use emojis in your yo notifications, you
# must ensure that you use utf-8 encoding on the script and append it after the
# shebang.

# Written by Erik Gomez

import os
import subprocess


def yo_single_button(title, informtext, buttontext):
    try:
        cmd = ['/Applications/Utilities/Yo.app/Contents/MacOS/yo', '-t',
               title, '-n', informtext, '-o', buttontext]
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = proc.communicate()
        return output
    except Exception:
        return None


def getuid501_firstname():
    yostring = 'Hello friend!'
    try:
        userlist = os.listdir('/Users')
        for user in userlist:
            cmd = ['/usr/bin/dscl', '.', 'read', '/Users/' + user, 'UniqueID']
            run = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = run.communicate()
            # dscl returns a new line for each value.
            # We are looking for the following:
            # UniqueID: 501
            #
            # If we find UniqueID, we know that we can strip any new lines,
            # split the string across the space and return only the integer
            if "UniqueID" in output:
                uid = output.rstrip('\n').split(' ')[1]
                if int(uid) == 501:
                    cmd = ['/usr/bin/dscl', '.', 'read', '/Users/' + user,
                           'RealName']
                    run = subprocess.Popen(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    output, err = run.communicate()
                    # dscl returns a new line for each value.
                    # We are looking for the following:
                    # RealName:
                    # First Last
                    # shortname
                    # If we find RealName, we can just split the returned
                    # values by spaces as you get something like this:
                    # ['RealName:\n', 'First', 'Last\n', 'shortname\n']
                    if "RealName" in output:
                        firstname = output.split(' ')[1]
                        yostring = 'Hello ' + str(firstname) + '!'
                        return yostring
                    else:
                        return yostring
    except AttributeError, OSError:
        return yostring
    return yostring


def main():
    username = getuid501_firstname()
    yo_single_button(username, 'Your computer will be ready shortly.', '👍')


if __name__ == '__main__':
    main()
