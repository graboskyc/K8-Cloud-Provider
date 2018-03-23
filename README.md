# K8-Cloud-Provider
This is a proof of concept skunkworks project to make a cloud provider for Kubernetes for CloudShell

## Assumptions
* CloudShell version 8.3 EA
* Kubernetes installed and pre-configured

## How to
* Run the shell script `package.sh` from the directory it is located in. It will spit out K8ShellPkg.zip
* Log into CloudShell web interface
* If running Chrome, drag and drop the zip file into the web portal. If not running Chrome, click on your username in the top right and choose "Import Package" and point to the zip file

## About
* The code that makes this work is based on another python script by [Mike Williams](https://github.com/mpw07458/K8S-Deploy/blob/master/pure-play/drivers/K8S_App_Shell/src/K8S_App_Shell_OS.py)
* CloudShell Cloud Provider Shell is not officially supported until 9.0 
* Currently *this code does nothing* and in time will actually deploy containers. While the above python script may work, it is not fully implemented in the shell yet.