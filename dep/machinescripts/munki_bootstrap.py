#!/usr/bin/python

# This script is used to bootstrap munki from a root process.
# Rather than rely on mobileconfigs (that may come from other systems), some
# basic defaults are created.

# To speed up the DEP run, an --id run is used in conjunction with
# --munkipkgsonly. This ensures apple updates (which may require a reboot)
# aren't processed.

# An --applesuspkgsonly function is provided, though it's recommended you run
# the munki_auto_trigger.py script (found in this repo) at the end of your
# DEP run.

# To speed up install time and reduce the number of https calls, we are
# pre-installing the icons (not with this script), moving them to a temporary
# place and reverting them once munki is done.

# Finally a fake null value is sent to munki's preference for LastCheckDate.
# Using this in conjuction with the yo_action_example.py script will cause
# Managed Software Center to immediately check for an update when it's first
# opened.

# Written by Erik Gomez. Foundation classes and plist functions written by
# Greg Neagle and adapted for use.

from distutils.dir_util import copy_tree
from Foundation import (CFPreferencesSetValue, kCFPreferencesAnyUser,
                        kCFPreferencesCurrentHost, NSData,
                        NSPropertyListSerialization,
                        NSPropertyListMutableContainers)

import os
import shutil
import subprocess


class FoundationPlistException(Exception):
    """Basic exception for plist errors"""
    pass


class NSPropertyListSerializationException(FoundationPlistException):
    """Read/parse error for plists"""
    pass


class NSPropertyListWriteException(FoundationPlistException):
    """Write error for plists"""
    pass


def readPlist(filepath):
    # Credit to Greg Neagle
    plistData = NSData.dataWithContentsOfFile_(filepath)
    dataObject, dummy_plistFormat, error = (
        NSPropertyListSerialization.
        propertyListFromData_mutabilityOption_format_errorDescription_(
            plistData, NSPropertyListMutableContainers, None, None))
    if dataObject is None:
        if error:
            error = error.encode('ascii', 'ignore')
        else:
            error = "Unknown error"
        errmsg = "%s in file %s" % (error, filepath)
        raise NSPropertyListSerializationException(errmsg)
    else:
        return dataObject


def munkirun(id):
    cmd = ['/usr/local/munki/managedsoftwareupdate', '--id', id,
           '--munkipkgsonly']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output, err = proc.communicate()
    return output


def munkiinstall():
    cmd = ['/usr/local/munki/managedsoftwareupdate', '--installonly']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output, err = proc.communicate()
    return output


def munkiappleupdates():
    cmd = ['/usr/local/munki/managedsoftwareupdate', '--applesuspkgsonly']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output, err = proc.communicate()
    return output


def main():
    # Variables
    munkiurl = 'https://somewhere.tld'
    backupmanifest = 'somemanifest'
    try:
        if os.path.isdir('/Library/Managed Installs/icons'):
            copy_tree('/Library/Managed Installs/icons',
                      '/private/var/munkiicons')
    except:  # noqa
        pass

    # Set basic munki preferences
    CFPreferencesSetValue(
        'InstallAppleSoftwareUpdates', True,
        '/Library/Preferences/ManagedInstalls',
        kCFPreferencesAnyUser, kCFPreferencesCurrentHost)

    CFPreferencesSetValue(
        'SoftwareRepoURL', munkurl,
        '/Library/Preferences/ManagedInstalls',
        kCFPreferencesAnyUser, kCFPreferencesCurrentHost)

    CFPreferencesSetValue(
        'ClientIdentifier', backupmanifest,
        '/Library/Preferences/ManagedInstalls',
        kCFPreferencesAnyUser, kCFPreferencesCurrentHost)

    # Run Munki with manifest you want to use
    munkirun('dep')

    # Install downloaded packages
    munkiinstall()

    # Revert Munki icons
    try:
        if os.path.isdir('/private/var/munkiicons'):
            copy_tree('/private/var/munkiicons',
                      '/Library/Managed Installs/icons')
            shutil.rmtree('/private/var/munkiicons')
    except:  # noqa
        pass

    CFPreferencesSetValue(
        'LastCheckDate', '',
        '/Library/Preferences/ManagedInstalls',
        kCFPreferencesAnyUser, kCFPreferencesCurrentHost)


if __name__ == '__main__':
    main()
