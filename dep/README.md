# DEP scripts
Most of these scripts are designed to be ran either by LaunchAgents or LaunchDaemons. While you may be able to run them as `postinstalls` inside of packages, many of them will more than likely fail due to the complexity of running scripts within an installer environment.

These scripts should be thought of as "building blocks" or a "pick your own adventure" game. You chose what you need and when you need it.

[InstallApplications](https://github.com/erikng/installapplications) is the recommended tool to run these scripts (except for Naggy) and have been battle tested.

## Machine scripts
These scripts are items you may use with DEP bootstrapping tools (such as InstallApplications) in the context of the machine. Some of these may require root level access.

## Tools
### Naggy
Naggy is a wrapper around dep nag to ensure that a user will receive the dep nag, regardless of the state of the machine. This is mainly intended to workaround what I consider an Apple bug:
* [/usr/libexec/mdmclient dep nag does not nag if user has doNotDisturb enabled](https://openradar.appspot.com/radar?id=5053331198181376)

## User scripts
These scripts are items you may use with DEP bootstrapping tools (such as InstallApplications) in the context of the currently logged in user.
