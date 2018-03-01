#!/usr/bin/python

# Naggy - python wrapper for DEP Nag
# Written by Erik Gomez
from SystemConfiguration import SCDynamicStoreCopyConsoleUser
import os
import platform
import plistlib
import subprocess
import time


naggyAgentLaunchAgent = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.github.naggyagent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python</string>
        <string>/Library/Application Support/naggy/naggyagent.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""

naggyAgentScript = """#!/usr/bin/python
import os
import subprocess
from Foundation import (CFPreferencesAppSynchronize,
                        CFPreferencesCopyAppValue,
                        CFPreferencesCopyValue,
                        CFPreferencesSetValue,
                        CFPreferencesSynchronize,
                        kCFPreferencesCurrentHost,
                        kCFPreferencesCurrentUser)


def touch(path):
    try:
        touchFile = ['/usr/bin/touch', path]
        proc = subprocess.Popen(touchFile, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        touchFileOutput, err = proc.communicate()
        os.chmod(path, 0777)
        return touchFileOutput
    except Exception:
        return None


def main():
    # Thanks Apple
    # https://openradar.appspot.com/radar?id=5053331198181376
    bundleID = 'com.apple.notificationcenterui'
    doNotDisturb = CFPreferencesCopyAppValue('doNotDisturb', bundleID)
    doNotDisturbByHost = CFPreferencesCopyValue('doNotDisturb', bundleID,
                                                kCFPreferencesCurrentUser,
                                                kCFPreferencesCurrentHost)
    if doNotDisturb:
        CFPreferencesSetValue('doNotDisturb', False, bundleID,
                              kCFPreferencesCurrentUser,
                              kCFPreferencesCurrentHost)
        CFPreferencesSynchronize(bundleID,
                                 kCFPreferencesCurrentUser,
                                 kCFPreferencesCurrentHost)
    if doNotDisturbByHost:
        CFPreferencesSetValue('doNotDisturb', False, bundleID,
                              kCFPreferencesCurrentUser,
                              kCFPreferencesCurrentHost)
        CFPreferencesAppSynchronize(bundleID)
    if doNotDisturb or doNotDisturbByHost:
        touch('/Users/Shared/.dndon')
        subprocess.call(['/usr/bin/killall', 'NotificationCenter'])
    else:
        touch('/Users/Shared/.dndoff')


if __name__ == '__main__':
    main()

"""


def cleanUp(naggyPath, naggyLaunchAgentPath, naggyLaunchAgentIdentifier,
            userId, DNDOnPath, DNDOffPath):
    # Attempt to remove the LaunchAgent
    NaggyLog('Attempting to remove LaunchAgent: ' + naggyLaunchAgentPath)
    try:
        os.remove(naggyLaunchAgentPath)
    except:  # noqa
        pass

    # Attempt to remove the DND triggers
    if os.path.isfile(DNDOnPath):
        NaggyLog('Attempting to remove DND On trigger: ' + DNDOnPath)
        try:
            os.remove(DNDOnPath)
        except:  # noqa
            pass
    elif os.path.isfile(DNDOffPath):
        NaggyLog('Attempting to remove DND Off trigger: ' + DNDOffPath)
        try:
            os.remove(DNDOffPath)
        except:  # noqa
            pass

    # Attempt to remove the launchagent from the user's list
    NaggyLog('Targeting user id for LaunchAgent removal: ' + userId)
    NaggyLog('Attempting to remove LaunchAgent: ' + naggyLaunchAgentIdentifier)
    launchCTL('/bin/launchctl', 'asuser', userId,
              '/bin/launchctl', 'remove', naggyLaunchAgentIdentifier)

    # Attempt to kill InstallApplications' path
    NaggyLog('Attempting to remove Naggy directory: ' + naggyPath)
    try:
        shutil.rmtree(naggyPath)
    except:  # noqa
        pass


def getConsoleUser():
    CFUser = SCDynamicStoreCopyConsoleUser(None, None, None)
    return CFUser


def launchCTL(*arg):
    # Use *arg to pass unlimited variables to command.
    cmd = arg
    run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = run.communicate()
    return output


def checkDEPEnrolledStatus(depProfileUuid):
    enrollment = False
    cmd = ['/usr/bin/profiles', '-L', '-o', 'stdout-xml']
    run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = run.communicate()
    try:
        plist = plistlib.readPlistFromString(output)
    except:  # noqa
        plist = {'_computerlevel': []}
    for x in plist['_computerlevel']:
        try:
            profileUuid = x['ProfileUUID']
        except KeyError:
            profileUuid = ''
        if profileUuid == depProfileUuid:
            return True
    return enrollment


def checkDEPEnrolledStatusHighSierra():
    # Only for 10.13 and higher
    enrollment = False
    enrolled = 'An enrollment profile is currently installed on this system'
    notEnrolled = 'There is no enrollment profile installed on this system'
    cmd = ['/usr/bin/profiles', 'status', '-type', 'enrollment']
    run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = run.communicate()
    status = output.split('\n')[0]
    if enrolled in status:
        return True
    elif notEnrolled in status:
        return False
    return enrollment


def getOSVersion():
    """Return OS version."""
    return platform.mac_ver()[0]


def hasDEPActivationRecord():
    # We can't use -o stdout-xml due to another Apple bug :)
    plistPath = '/var/tmp/DEPRecord.plist'
    cmd = ['/usr/bin/profiles', '-e', '-o', plistPath]
    run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = run.communicate()
    if err:
        return False
    try:
        plist = plistlib.readPlist(plistPath)
    except:  # noqa
        plist = {}
    if not plist:
        return False
    else:
        return True


def NaggyLog(text):
    logPath = '/private/var/log/naggy.log'
    formatStr = '%b %d %Y %H:%M:%S %z: '
    with open(logPath, 'a+') as log:
        log.write(time.strftime(formatStr) + text + '\n')


def triggerNag():
    cmd = ['/usr/libexec/mdmclient', 'dep', 'nag']
    run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = run.communicate()
    return output


def main():
    global naggyAgentLaunchAgent
    global naggyAgentScript
    currentUserUid = getConsoleUser()
    userId = str(getConsoleUser()[1])
    depProfileUuid = 'YOURUUIDHERE'
    needToNag = False
    OSVersion = getOSVersion()
    NaggyLog('OS Version: %s' % OSVersion)
    if '10.13' in OSVersion:
        if checkDEPEnrolledStatusHighSierra():
            NaggyLog('Device is already enrolled in DEP.')
            exit(0)
        else:
            NaggyLog('Device is not enrolled in DEP.')
            if hasDEPActivationRecord():
                NaggyLog('DEP Activation record found.')
                needToNag = True
    else:
        if checkDEPEnrolledStatus(depProfileUuid):
            NaggyLog('Device is already enrolled in DEP.')
            exit(0)
        else:
            NaggyLog('Device is not enrolled in DEP.')
            if hasDEPActivationRecord():
                NaggyLog('DEP Activation record found.')
                needToNag = True
    if needToNag:
        if (currentUserUid[0] is None or currentUserUid[0] == u'loginwindow'
                or currentUserUid[0] == u'_mbsetupuser'):
            pass
        else:
            naggyLaunchAgentIdentifier = 'com.github.naggyagent'
            naggyLaunchAgentPlist = 'com.github.naggyagent.plist'
            naggyPath = os.path.join('/Library', 'Application Support',
                                     'naggy')
            naggyAgentPath = os.path.join(naggyPath, 'naggyagent.py')
            naggyLaunchAgentPath = os.path.join('/Library', 'LaunchAgents',
                                                naggyLaunchAgentPlist)
            DNDOnPath = '/Users/Shared/.dndon'
            DNDOffPath = '/Users/Shared/.dndoff'

            if not os.path.isdir(naggyPath):
                os.makedirs(naggyPath)
            with open(naggyAgentPath, 'wb') as na:
                na.write(naggyAgentScript)
            with open(naggyLaunchAgentPath, 'wb') as la:
                la.write(naggyAgentLaunchAgent)

            launchCTL('/bin/launchctl', 'asuser', userId,
                      '/bin/launchctl', 'load', naggyLaunchAgentPath)

            while not os.path.isfile(DNDOnPath) and not os.path.isfile(DNDOffPath):  # noqa
                NaggyLog('Waiting for DND trigger file...')
                time.sleep(3)
            if os.path.isfile(DNDOnPath):
                NaggyLog('doNotDisturb is enabled - disabling.')
            elif os.path.isfile(DNDOffPath):
                NaggyLog('doNotDisturb is disabled.')
            triggerNag()
            cleanUp(naggyPath, naggyLaunchAgentPath,
                    naggyLaunchAgentIdentifier, userId, DNDOnPath, DNDOffPath)


if __name__ == '__main__':
    main()
