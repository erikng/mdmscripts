#!/usr/bin/python

# This script uses managedsoftwareupdate binary to run an auto run, which
# mimics the launch daemon. This ensures a machine is fully compliant after
# your DEP run. You should be very careful with this script if you call it from
# another script as it will more than likely pause your entire workflow until
# the munki run is over. InstallApplications can handle this by passing the
# "donotwait" key in the json payload.

# You _must_ pass preexec_fn=os.setpgrp in the subprocess, otherwise when
# your original script exits, it will kill the munki run. This is because
# preexec_fn=os.setpgrp changes the SIGINT of this child process (this script)
# would usually receive, thereby allowing it to continue to process even if the
# original parent has sent a SIGINT to it's own child processes.

import os
import subprocess


def main():
    munkicheck = ['/usr/local/munki/managedsoftwareupdate', '--auto']
    try:

        munki = subprocess.Popen(munkicheck, preexec_fn=os.setpgrp)
    except:  # noqa
        pass


if __name__ == '__main__':
    main()
