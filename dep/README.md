# DEP scripts

## Machine scripts
These scripts are items you may use with DEP bootstrapping tools (such as InstallApplications) in the context of the machine. Some of these may require root level access.

## Tools
### Naggy
Naggy is a wrapper around dep nag to ensure that a user will receive the dep nag, regardless of the state of the machine. This is mainly intended to workaround what I consider an Apple bug:
* [/usr/libexec/mdmclient dep nag does not nag if user has doNotDisturb enabled](https://openradar.appspot.com/radar?id=5053331198181376)

## User scripts
These scripts are items you may use with DEP bootstrapping tools (such as InstallApplications) in the context of the currently logged in user.
