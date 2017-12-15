#!/usr/bin/python

# A simple yo notification with an action.
# Written by Erik Gomez
import subprocess


def yo_bash(title, informtext, action, actionpath, buttontext):
    try:
        cmd = ['/Applications/Utilities/Yo.app/Contents/MacOS/yo', '-t',
               title, '-n', informtext, '-b', action, '-B', actionpath,
               '-o', buttontext]
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = proc.communicate()
        return output
    except Exception:
        return None


def main():
    yo_bash('Important Software Updates',
            'You may have some additional updates to install.',
            'Go to Updates', '/usr/bin/open munki://updates', 'Not now')


if __name__ == '__main__':
    main()
