#!/usr/bin/python

# This script blesses the booted volume on 10.13 APFS volumes for virtual
# machines. This is due to either a bug in macOS or virtual machine tools
# like VMware Fusion that causes the device to become unable to boot after
# enabling FileVault.

# This script makes many assumptions about the boot volume and has been tested
# with common vfuse configurations. Your mileage may vary.

# Written by Erik Gomez.
# sysctl function written by Michael Lynn.

from ctypes import CDLL, c_uint, byref, create_string_buffer
from ctypes.util import find_library
import platform
import plistlib
import subprocess


def getOSVersion():
    """Return OS version."""
    return platform.mac_ver()[0]


def sysctl(name, is_string=True):
    '''Wrapper for sysctl so we don't have to use subprocess'''
    size = c_uint(0)
    # Find out how big our buffer will be
    libc = CDLL(find_library('c'))
    libc.sysctlbyname(name, None, byref(size), None, 0)
    # Make the buffer
    buf = create_string_buffer(size.value)
    # Re-run, but provide the buffer
    libc.sysctlbyname(name, buf, byref(size), None, 0)
    if is_string:
        return buf.value
    else:
        return buf.raw


def isVirtualMachine():
    '''Returns True if this is a VM, False otherwise'''
    cpu_features = sysctl('machdep.cpu.features').split()
    return 'VMM' in cpu_features


def getMachineType():
    '''Return the machine type: physical, vmware, virtualbox, parallels or
    unknown_virtual'''
    if not isVirtualMachine():
        return 'physical'

    # this is a virtual machine; see if we can tell which vendor
    try:
        proc = subprocess.Popen(['/usr/sbin/system_profiler', '-xml',
                                 'SPEthernetDataType', 'SPHardwareDataType'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = proc.communicate()[0]
        plist = plistlib.readPlistFromString(output)
        br_version = plist[1]['_items'][0]['boot_rom_version']
        if 'VMW' in br_version:
            return 'vmware'
        elif 'VirtualBox' in br_version:
            return 'virtualbox'
        else:
            ethernet_vid = plist[0]['_items'][0]['spethernet_vendor-id']
            if '0x1ab8' in ethernet_vid:
                return 'parallels'

    except (IOError, KeyError, OSError):
        pass

    return 'physical'


def bless(path):
    try:
        blesscmd = ['/usr/sbin/bless', '--folder', path, '--setBoot']
        proc = subprocess.Popen(blesscmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, err = proc.communicate()
        return output
    except Exception:
        return None


def fileSystemType(path):
    filetype = ''
    try:
        diskutilcmd = ['/usr/sbin/diskutil', 'info', '-plist', path]
        proc = subprocess.Popen(diskutilcmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, _ = proc.communicate()
    except (IOError, OSError):
        output = None
    if output:
        outplist = plistlib.readPlistFromString(output.strip())
        filetype = outplist.get('FilesystemType', '')
    return filetype


def main():
    if ('10.13' in getOSVersion() and 'apfs' in fileSystemType('/') and
            getMachineType() is not 'physical'):
        bless('/Volumes/Macintosh HD/System/Library/CoreServices')


if __name__ == '__main__':
    main()
