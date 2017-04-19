#!/usr/bin/python

# python ./aw_api_installapplication.py \
# --authorization 'dXNlcm5hbWU6cGFzc3dvcmQ=' \
# --baseurl 'https://cn.awmdm.com'
# --manifesturl 'https://s3.amazonaws.com/appmanifest.plist' \
# --tenantcode 'YWlyd2F0Y2h0ZW5hbnRjb2Rl' \
# --machineserial "CXXXXXXXXXXX"

# Written by Erik Gomez
# Requires requests python library
# http://docs.python-requests.org/en/master/

from Foundation import NSBundle
import json
import objc
import optparse
import requests
import sys


def get_serial():
    # Credit to Michael Lynn
    IOKit_bundle = NSBundle.bundleWithIdentifier_("com.apple.framework.IOKit")
    functions = [
        ("IOServiceGetMatchingService", b"II@"),
        ("IOServiceMatching", b"@*"),
        ("IORegistryEntryCreateCFProperty", b"@I@@I")
    ]
    objc.loadBundleFunctions(IOKit_bundle, globals(), functions)

    kIOMasterPortDefault = 0
    kIOPlatformSerialNumberKey = 'IOPlatformSerialNumber'
    kCFAllocatorDefault = None

    platformExpert = IOServiceGetMatchingService(
        kIOMasterPortDefault,
        IOServiceMatching("IOPlatformExpertDevice")
    )
    serial = IORegistryEntryCreateCFProperty(
        platformExpert,
        kIOPlatformSerialNumberKey,
        kCFAllocatorDefault,
        0
    )
    return serial


def get_deviceid(baseurl, headers, serial):
    url = "%s/api/mdm/devices" % baseurl
    query = {"searchby": "Serialnumber", "id": serial}
    try:
        response = requests.request("GET", url, headers=headers, params=query)
        data = json.loads(response.text)
        return data['Id']['Value']
    except KeyError, error:
        return None


def magic(baseurl, awid, headers, command):
    url = "%s/api/mdm/devices/%s/commands?command=CustomMDMCommand" % (baseurl,
                                                                       awid)
    try:
        response = requests.request("POST", url, headers=headers, data=command)
        if response.status_code == 202:
            return 'Command successfully sent to device.'
        else:
            return response.code
    except KeyError, error:
        return 'Unknown'


def main():
    usage = '%prog [options]'
    o = optparse.OptionParser(usage=usage)
    o.add_option('--authorization', help=(
        'Required: Base64 encoded username and password.'))
    o.add_option('--baseurl', help=(
        'Required: Base URL to AirWatch Console.'))
    o.add_option('--manifesturl', help=(
        'Required: URL path to appmanifest.plist.'))
    o.add_option('--tenantcode', help=(
        'Required: AW Tenant Code.'))
    o.add_option('--machineserial', help=(
        'Optional: Target macOS serial. If not used, will use local serial.'))
    opts, args = o.parse_args()

    if not opts.baseurl and not opts.manifesturl and not opts.tenantcode:
        o.print_help()
        sys.exit(1)

    if opts.machineserial:
        serial = opts.machineserial
    else:
        serial = get_serial()

    authorization = opts.authorization
    baseurl = opts.baseurl
    manifesturl = opts.manifesturl
    tenantcode = opts.tenantcode

    command = json.dumps(
        {
            'CommandXml':
            '<dict>'
                '<key>RequestType</key>'
                '<string>InstallApplication</string>'
                '<key>ManifestURL</key>'
                '<string>' + manifesturl + '</string>'
            '</dict>'
        }
    )

    headers = {
        'Authorization': 'Basic ' + authorization,
        'aw-tenant-code': tenantcode,
        'content-type': 'application/json',
        'accept': 'application/json',
    }

    # Use AirWatch API to get the deviceid of the serial number
    awid = get_deviceid(baseurl, headers, serial)

    # Send the InstallApplication command with the appmanifest.plist
    print magic(baseurl, awid, headers, command)


if __name__ == '__main__':
    main()
