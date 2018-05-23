#!/bin/bash

hash zip 2>/dev/null || { echo >&2 "ZIP is not installed. try running apt-get install zip or your equiv."; exit 1; }
hash wget 2>/dev/null || { echo >&2 "wget is not installed. try running apt-get install wget or your equiv."; exit 1; }
hash awk 2>/dev/null || { echo >&2 "awk is not installed. try running apt-get install awk or your equiv."; exit 1; }

incBuild=true
while true; do
    read -p "Y/N: Increment build number? " resp
    case $resp in
       [yY]* ) incBuild=true
           break;;

        [nN]* ) incBuild=false
            break;;
    esac
done

downloadLatest=true
while true; do
    read -p "Y/N: Download K8S_App_Shell_OS? " resp
    case $resp in
       [yY]* ) downloadLatest=true
           break;;

        [nN]* ) downloadLatest=false
            break;;
    esac
done

cd K8\ Shell\ Driver

if $downloadLatest; then
    echo
    echo "Downloading Latest Version of Code"
    echo

    wget https://raw.githubusercontent.com/mpw07458/K8S-Deploy-Shell/master/pure-play/drivers/K8S_App_Shell/src/K8S_App_Shell_OS.py?token=AhVDVkas40HYGFb_bNW7pQOhAizpIy1iks5bDhCawA%3D%3D -O K8S_App_Shell_OS.py -q
fi

if $incBuild; then
    echo
    echo "Incrementing build number..."
    echo
    cv=`cat drivermetadata.xml | grep Version | sed 's/Version=/\n/g' | tail -n -1 | sed 's/"//g' | sed 's/>//g' | sed 's/\n//g' | sed 's/\r//g'`
    nlbn="$(echo $cv | rev | cut -d. -f1 | rev)"
    nbn=`echo $nlbn | awk '{$1++; print $0}'`
    nb=${cv%.*}"."${nbn}
    sed -i drivermetadata.xml -e "s/$cv/$nb/g"
    echo $nb > version.txt
    echo $nb > ../k8_shellPackage/version.txt
fi

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
