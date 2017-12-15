#!/usr/bin/python

# Naggy - python wrapper for DEP Nag
# Written by Erik Gomez
import multiprocessing
import os
import platform
import plistlib
import subprocess
import sys
import time


def checkAndDisableDND():
    # Thanks Apple
    # https://openradar.appspot.com/radar?id=5053331198181376
    import os
    import pwd
    import subprocess
    from Foundation import (CFPreferencesSetValue,
                            kCFPreferencesCurrentUser,
                            kCFPreferencesCurrentHost,
                            CFPreferencesSynchronize,
                            CFPreferencesCopyAppValue)
    from SystemConfiguration import SCDynamicStoreCopyConsoleUser
    cfuser = SCDynamicStoreCopyConsoleUser(None, None, None)
    consoleUser = cfuser[0]
    userUID = pwd.getpwnam(consoleUser).pw_uid
    os.setuid(userUID)
    bundleID = 'com.apple.notificationcenterui'
    doNotDisturb = CFPreferencesCopyAppValue('doNotDisturb', bundleID)
    if doNotDisturb:
        CFPreferencesSetValue('doNotDisturb', False,
                              'com.apple.notificationcenterui',
                              kCFPreferencesCurrentUser,
                              kCFPreferencesCurrentHost)
        CFPreferencesSynchronize(bundleID,
                                 kCFPreferencesCurrentUser,
                                 kCFPreferencesCurrentHost)
        subprocess.call(['/usr/bin/killall', 'NotificationCenter'])
        exit(2)
    exit(0)


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


def nagNagLog(text):
    logPath = '/private/var/log/nagnag.log'
    formatStr = '%b %d %Y %H:%M:%S %z: '
    with open(logPath, 'a+') as log:
        log.write(time.strftime(formatStr) + text + '\n')


def triggerNag():
    cmd = ['/usr/libexec/mdmclient', 'dep', 'nag']
    run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = run.communicate()
    return output


def main():
    depProfileUuid = 'YOURUUIDHERE'
    needToNag = False
    OSVersion = getOSVersion()
    nagNagLog('OS Version: %s' % OSVersion)
    if '10.13' in OSVersion:
        if checkDEPEnrolledStatusHighSierra():
            nagNagLog('Device is already enrolled in DEP.')
            sys.exit(0)
        else:
            nagNagLog('Device is not enrolled in DEP.')
            if hasDEPActivationRecord():
                nagNagLog('DEP Activation record found.')
                needToNag = True
    else:
        if checkDEPEnrolledStatus(depProfileUuid):
            nagNagLog('Device is already enrolled in DEP.')
            sys.exit(0)
        else:
            nagNagLog('Device is not enrolled in DEP.')
            if hasDEPActivationRecord():
                nagNagLog('DEP Activation record found.')
                needToNag = True
    if needToNag:
        # Check for and disable DND
        dndCheck = multiprocessing.Process(target=checkAndDisableDND)
        dndCheck.start()
        dndCheck.join()
        dndExitCode = dndCheck.exitcode
        if dndExitCode is 2:
            nagNagLog('doNotDisturb is enabled - disabling.')
        elif dndExitCode is 0:
            nagNagLog('doNotDisturb is disabled.')
        nagNagLog('Triggering DEP Nag.')
        triggerNag()


if __name__ == '__main__':
    main()
