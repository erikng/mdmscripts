#!/usr/bin/python

# This example script uses the caffeine command to ensure the machine never
# goes to sleep. You should be very careful with this script if you call it
# from another script as it will more than likely pause your entire workflow
# until the caffeination is over. InstallApplications can handle this by
# passing the "donotwait" key in the json payload.

# Written by Erik Gomez
import subprocess


def main():
    caffeinationtime = '600'  # amount in seconds
    caffeinatecmd = ['/usr/bin/caffeinate', '-dimut', caffeinationtime]
    try:
        caffeine = subprocess.Popen(caffeinatecmd)
    except:  # noqa
        print 'Could not caffeinate machine.'
        pass


if __name__ == '__main__':
    main()
