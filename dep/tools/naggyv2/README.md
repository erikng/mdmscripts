# Naggy v2
It does things. For now read the code

## Building this package
You will need to use [munki-pkg](https://github.com/munki/munki-pkg) to build this package

### Notes
Because of the way git works, naggy will not contain the `Logs` folder required for the postinstall to complete.

In order to create a properly working package, you will need to run the following command:
`munkipkg --sync /path/to/cloned_repo/dep/tools/naggyv2`

## Screenshots

### DEP
![Screenshot DEP](/dep/tools/naggyv2/images/ss_dep.png?raw=true)

### Manual
![Screenshot Manual](/dep/tools/naggyv2/images/ss_manual.png?raw=true)

### UAMDM
![Screenshot UAMDM](/dep/tools/naggyv2/images/ss_uamdm.png?raw=true)
