#!/bin/bash

centos_install_epel(){
	# CentOS has epel release in the extras repo
	sudo yum -y install epel-release
	import_epel_key
}

rhel_install_epel(){
	case ${RELEASE} in
		6*) sudo yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm;;
		7*) sudo yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm;;
	esac
	import_epel_key
}

import_epel_key(){
	case ${RELEASE} in
		6*) sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-6;;
		7*) sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7;;
	esac
}

centos_install_ius(){
	case ${RELEASE} in
		6*) sudo yum -y install https://centos6.iuscommunity.org/ius-release.rpm;;
		7*) sudo yum -y install https://centos7.iuscommunity.org/ius-release.rpm;;
	esac
	import_ius_key
}

rhel_install_ius(){
	case ${RELEASE} in
		6*) yum -y install https://rhel6.iuscommunity.org/ius-release.rpm;;
		7*) yum -y install https://rhel7.iuscommunity.org/ius-release.rpm;;
	esac
	import_ius_key
}

import_ius_key(){
	sudo rpm --import /etc/pki/rpm-gpg/IUS-COMMUNITY-GPG-KEY
}

if [[ -e /etc/redhat-release ]]; then
	RELEASE_RPM=$(rpm -qf /etc/redhat-release)
	RELEASE=$(rpm -q --qf '%{VERSION}' ${RELEASE_RPM})
	case ${RELEASE_RPM} in
		centos*)
			echo "detected CentOS ${RELEASE}"
			centos_install_epel
			centos_install_ius
			;;
		redhat*)
			echo "detected RHEL ${RELEASE}"
			rhel_install_epel
			rhel_install_ius
			;;
		*)
			echo "unknown EL clone"
			exit 1
			;;
	esac

else
	echo "not an EL distro"
	exit 1
fi

echo "Updating yum..."

sudo yum -y update

echo "Installing python3 from ius repository"

sudo yum -y python35u

echo "Installed python3 sucessfully if not error..."

