#!/Library/ManagedFrameworks/Python/Python3.framework/Versions/Current/bin/python3
'''WS1 Custom Command API using InstallEnterpriseApplication'''
# Written by Erik Gomez
# Requires Macadmins Python 3
# https://github.com/macadmins/python
# Requires AirWatch 9.1 or higher and a macOS device enrolled in WS1.
#
# Example Usage:
#
# ./installenterpriseapplication.py \
# --baseurl 'https://cn1234.awmdm.com' \
# --manifesturl 'https://domain.tld/manifest.plist' \
# --tenantcode 'YW5fZXhhbXBsZQ==' \
# --targetserial "CXXXXXXXXXXX"
#

import argparse
import getpass
import json
import plistlib
import subprocess
import sys
import requests
from requests.auth import HTTPBasicAuth


def get_hardware_info():
    # pylint: disable=broad-except
    '''Uses system profiler to get hardware info for this machine'''
    cmd = ['/usr/sbin/system_profiler', 'SPHardwareDataType', '-xml']
    proc = subprocess.Popen(
        cmd,
        shell=False,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output = proc.communicate()[0]
    try:
        plist = plistlib.loads(output)
        # system_profiler xml is an array
        sp_dict = plist[0]
        items = sp_dict['_items']
        sp_hardware_dict = items[0]
        return sp_hardware_dict
    except BaseException:
        return {}
    # pylint: enable=broad-except


def get_deviceid(baseurl, headers, serial, username, password):
    # pylint: disable=broad-except
    '''Gets the deviceid from WS1'''
    url = '%s/api/mdm/devices' % baseurl
    query = {'searchby': 'Serialnumber', 'id': serial}
    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(username, password),
            headers=headers,
            params=query
        )
        data = json.loads(response.text)
        return data['Id']['Value']
    except BaseException:
        return None
    # pylint: enable=broad-except

# pylint: disable=too-many-arguments
def custom_mdm_command(baseurl, headers, deviceid, command, username, password):
    # pylint: disable=broad-except
    '''Sends a custom mdm command to a specific device'''
    url = '%s/api/mdm/devices/%s/commands?command=CustomMDMCommand' % (baseurl,
                                                                       deviceid)
    try:
        response = requests.post(
            url,
            auth=HTTPBasicAuth(username, password),
            headers=headers,
            data=command
        )
        if response.status_code == 202:
            msg = 'Command successfully sent to device.'
        else:
            msg = response.code
        return msg
    except BaseException:
        return None
    # pylint: enable=broad-except
    # pylint: enable=too-many-arguments


def main():
    '''Main script'''
    parser = argparse.ArgumentParser(
        description='A CLI tool for running InstallEnterpriseApplication',
        epilog='For further help, please contact me.'
    )
    parser.add_argument(
        '-b',
        '--baseurl',
        help='Base URL to WS1 console.'
    )
    parser.add_argument(
        '-m',
        '--manifesturl',
        help='URL path to application manifest.plist.'
    )
    parser.add_argument(
        '-t',
        '--tenantcode',
        help='WS1 tenant code for API usage.'
    )
    parser.add_argument(
        '-s',
        '--targetserial',
        help='Target macOS serial. If not used, will use local serial.'
    )
    args = parser.parse_known_args()[0]

    username = input('Enter username: ')
    password = getpass.getpass()
    baseurl = args.baseurl
    manifesturl = args.manifesturl
    tenantcode = args.tenantcode

    if not baseurl and not manifesturl and not tenantcode:
        parser.print_help()
        sys.exit(1)

    if args.targetserial:
        serial = args.targetserial
    else:
        serial = get_hardware_info().get('serial_number', None)

    if not serial:
        print('Could not retrieve targeted serial number.')
        sys.exit(1)

    command = json.dumps(
        {
            'CommandXml':
            '<dict>'
                '<key>RequestType</key>'
                '<string>InstallEnterpriseApplication</string>'
                '<key>ManifestURL</key>'
                '<string>' + manifesturl + '</string>'
                '<key>PinningRevocationCheckRequired</key>'
                '<false/>'
            '</dict>'
        }
    )

    headers = {
        'aw-tenant-code': tenantcode,
        'content-type': 'application/json',
        'accept': 'application/json',
    }

    # Use AirWatch API to get the deviceid of the serial number
    deviceid = get_deviceid(baseurl, headers, serial, username, password)

    # Send the InstallEnterpriseApplication command with the application
    # manifest.plist
    if deviceid:
        print(custom_mdm_command(
            baseurl, headers, deviceid, command, username, password))
    else:
        print('Could not retrieve targeted serial number device id from MDM.')
        sys.exit(1)


if __name__ == '__main__':
    main()
