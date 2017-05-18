#!/bin/bash

echo "Installiere Thesispool..."
echo

# root check
if [[ $(id -u) -ne 0 ]]
then 
	echo "Please run as root";
	exit 1; 
fi

# install packages
apt-get install -y python3 apache2 python3-setuptools python3-pip libsasl2-dev ibapache2-mod-wsgi-py3 libldap2-dev libssl-dev
# update pip
pip3 install -U pip
pip3 install pyldap

#install django and the LDAP backend
pip3 install django django_auth_ldap 

# used for pdf sending
pip3 install django_sendfile
pip3 install python-dateutil

# make db and folder above it owned by www-data
# collectstatic
# apt-get install libmysqlclient-dev
# apt-get install mysqlclient

# for pdf sending
# sudo apt-get install libapache2-mod-xsendfile
# a2enmod xsendfile
# certificate ca-cert in /etc/ssl/certs/ca-certificats einfügen