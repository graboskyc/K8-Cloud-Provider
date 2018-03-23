#!/bin/bash

hash zip 2>/dev/null || { echo >&2 "ZIP is not installed. try running apt-get install zip or your equiv."; exit 1; }
hash wget 2>/dev/null || { echo >&2 "wget is not installed. try running apt-get install wget or your equiv."; exit 1; }

echo
echo "Downloading Latest Version of Code"
echo

cd K8\ Shell\ Driver
wget https://raw.githubusercontent.com/mpw07458/K8S-Deploy/master/pure-play/drivers/K8S_App_Shell/src/K8S_App_Shell_OS.py -O K8S_App_Shell_OS.py -q

echo
echo "Creating python driver"
echo
zip -r ./K8\ Shell\ Driver.zip ./ > /dev/null

if [[ ! -d ../k8_shellPackage/Resource\ Drivers\ -\ Python ]]; then
    mkdir ../k8_shellPackage/Resource\ Drivers\ -\ Python
fi

mv K8\ Shell\ Driver.zip ../k8_shellPackage/Resource\ Drivers\ -\ Python/

echo
echo "Creating importable package"
echo
cd ..
cd k8_shellPackage
zip -r ./K8ShellPkg.zip ./ > /dev/null
mv K8ShellPkg.zip ../

echo
echo "COMPLETE!"
echo