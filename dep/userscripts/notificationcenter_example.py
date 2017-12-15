#!/usr/bin/python

# A simple example on how to dynamically send a NotificationCenter notification
# which is similar in vain to Yo, but is written in pure python. You can spoof
# any application icon, so if Apple ever deems this an issue, it could break.

# Written by Erik Gomez, but most of this code was originally written by Greg
# Neagle and Michael Lynn.
from Foundation import (NSBundle, NSUserNotificationCenter, NSUserNotification)
import time


def set_fake_bundleid(bundleid):
    bundle = NSBundle.mainBundle()
    info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
    # override the bundleid with the one we want
    info['CFBundleIdentifier'] = bundleid


def notify(title, bundleid=None):
    if bundleid:
        # fake our bundleid
        set_fake_bundleid(bundleid)

    # create a new user notification
    notification = NSUserNotification.alloc().init()
    notification.setTitle_(title)
    notification.setHasActionButton_(False)
    notification.setSoundName_(None)

    # get the default User Notification Center
    nc = NSUserNotificationCenter.defaultUserNotificationCenter()

    # Wait just a bit
    time.sleep(1)

    # Kill all old notifications so we can only show new notifications
    nc.removeAllDeliveredNotifications()

    # deliver the notification
    nc.deliverNotification_(notification)


def main():
    # Pass your text on the first argument and the bundleid you want to spoof
    # on the second.
    notify(u'Device Enrollment Beginning...', bundleid='com.apple.appstore')


if __name__ == '__main__':
    main()
