%define nutuser ups
%define STATEPATH /var/state/ups
%define CGIPATH /var/www/cgi-bin
%define HTMLPATH /var/www/nut
%define DRVPATH /sbin
%define CONFPATH %{_sysconfdir}/ups

Summary:	Network UPS Tools Client Utilities
Name:		nut
Version:	2.0.5
Release:	%mkrel 3
Epoch:		1
License:	GPL
Group:		System/Configuration/Hardware
URL:		http://random.networkupstools.org
Source0:	http://random.networkupstools.org/source/2.0/%{name}-%{version}.tar.gz
Source1:	http://random.networkupstools.org/source/2.0/%{name}-%{version}.tar.gz.sig
Source2:	upsd
Source3:	upsmon
Patch0:		nut-2.0.1-lib64.patch
Patch2:		nut-2.0.4-upsset.conf.diff
Patch3:		nut-2.0.4-mdv_conf.diff
Requires(pre):	chkconfig fileutils rpm-helper >= 0.8
BuildRequires:	autoconf2.5
BuildRequires:	libtool
BuildRequires:	freetype2-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libpng-devel
BuildRequires:	libgd-devel >= 2.0.5
BuildRequires:	libusb-devel
BuildRequires:	net-snmp-devel
BuildRequires:	xpm-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
These programs are part of a developing project to monitor the assortment 
of UPSes that are found out there in the field. Many models have serial 
ports of some kind that allow some form of state checking. This
capability has been harnessed where possible to allow for safe shutdowns, 
live status tracking on web pages, and more.

This package includes the client utilities that are required to monitor a
UPS that the client host is powered from - either connected directly via
a serial port (in which case the nut-server package needs to be installed on
this machine) or across the network (where another host on the network
monitors the UPS via serial cable and runs the main nut package to allow
clients to see the information).

%package	server
Summary:	Network UPS Tools server
Group:		System/Servers
Requires:	nut = %{epoch}:%{version}-%{release}
Requires(pre):	rpm-helper >= 0.8

%description	server
These programs are part of a developing project to monitor the assortment 
of UPSes that are found out there in the field. Many models have serial 
serial ports of some kind that allow some form of state checking. This
capability has been harnessed where possible to allow for safe shutdowns, 
live status tracking on web pages, and more.

This package is the main NUT upsd daemon and the associated per-UPS-model
drivers which talk to the UPSes.  You also need to install the base NUT
package.

%package	cgi
Summary:	CGI utils for NUT
Group:		Monitoring
Requires:	apache
Requires(pre):	rpm-helper >= 0.8
Conflicts:	apcupsd

%description	cgi
These programs are part of a developing project to monitor the assortment 
of UPSes that are found out there in the field. Many models have serial 
serial ports of some kind that allow some form of state checking. This
capability has been harnessed where possible to allow for safe shutdowns, 
live status tracking on web pages, and more.

This package adds the web CGI programs.   These can be installed on a
separate machine to the rest of the NUT package.

%package	devel
Summary:	Development for NUT Client
Group:		Monitoring
Requires(pre):	rpm-helper >= 0.8

%description	devel
This package contains the development header files and libraries
necessary to develop NUT client applications.

%prep

%setup -q
%patch0 -p1 -b .lib64
env WANT_AUTOCONF_2_5=1 autoconf
%patch2 -p0
%patch3 -p1

# instead of a patch
perl -pi -e "s|/cgi-bin/nut|/cgi-bin|g" data/html/*.html*

%build
%serverbuild

%if %mdkversion >= 200710
export CFLAGS="%{optflags} -fstack-protector-all"
export CXXFLAGS="%{optflags} -fstack-protector-all"
export FFLAGS="%{optflags} -fstack-protector-all"
%endif

%configure2_5x \
	--with-cgi \
	--with-statepath=%{STATEPATH} \
	--with-drvpath=%{DRVPATH} \
	--with-cgipath=%{CGIPATH} \
	--with-htmlpath=%{HTMLPATH} \
	--with-gd-libs \
	--with-user=%{nutuser} \
	--with-group=%{nutuser} \
	--enable-shared \
	--sysconfdir=%{CONFPATH}

# workaround buggy parrallel build:
make all usb snmp

%install
rm -rf %{buildroot}

# Build basic directories here - if they exist already then the
# installer doesn't try to create and chown them (the chown is
# a killer if we are building as non-root
install -d %{buildroot}%{CONFPATH}
install -d %{buildroot}%{STATEPATH}
install -d %{buildroot}%{DRVPATH}
install -d %{buildroot}%{CGIPATH}
install -d %{buildroot}%{_mandir}
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_sbindir}
make DESTDIR=%{buildroot} install
make DESTDIR=%{buildroot} install-conf
make DESTDIR=%{buildroot} install-cgi-conf
#make DESTDIR=%{buildroot} install-all-drivers
make DESTDIR=%{buildroot} install-lib
make DESTDIR=%{buildroot} install-cgi
make DESTDIR=%{buildroot} install-usb
make DESTDIR=%{buildroot} install-snmp

# install SYSV init stuff
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{DRVPATH}
install %SOURCE2 %{buildroot}/%{_initrddir}
install %SOURCE3 %{buildroot}/%{_initrddir}
#install drivers/dummycons %{buildroot}/%{DRVPATH}

# move the *.sample config files to their real locations
# we don't need to worry about overwriting anything since
# they are marked as %config files within the package
for file in %{buildroot}%{CONFPATH}/*.sample
do
    mv $file %{buildroot}%{CONFPATH}/`basename $file .sample`
done

mv %{buildroot}%{CONFPATH}/upsmon.conf %{buildroot}%{CONFPATH}/upsmon.conf.sample
perl -pi -e 's/# RUN_AS_USER nutmon/RUN_AS_USER %{nutuser}/g' %{buildroot}%{CONFPATH}/upsmon.conf.sample

cp -af data/driver.list docs/

# udev usb ups stuff
install -d %{buildroot}%{_sysconfdir}/udev/rules.d
install -m0644 scripts/hotplug-ng/nut-usbups.rules %{buildroot}%{_sysconfdir}/udev/rules.d/70-nut-usbups.rules

# fix access config files
install -d %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d
cat > %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/%{name}-cgi.conf << EOF

<Files upsset.cgi>
    Order deny,allow
    Deny from all
    Allow from 127.0.0.1
    ErrorDocument 403 "Access denied per %{_sysconfdir}/httpd/conf/webapps.d/%{name}-cgi.conf"
</Files>

Alias /nut %{HTMLPATH}

<Directory "%{HTMLPATH}">
    Order deny,allow
    Deny from all
    Allow from 127.0.0.1
    ErrorDocument 403 "Access denied per %{_sysconfdir}/httpd/conf/webapps.d/%{name}-cgi.conf"
</Directory>

EOF

%pre
# Create an UPS user.
%_pre_useradd ups %{STATEPATH} /bin/false
%_pre_groupadd ups ups
%_pre_groupadd tty ups
%_pre_groupadd usb ups
%_pre_groupadd uucp ups

%preun
# only do this if it is not an upgrade
%_preun_service upsmon

%post
%_post_service upsmon

%postun
# Only do this if it is not an upgrade
if [ ! -f %_sbindir/upsd ]; then
   %_postun_userdel ups
fi

%pre	server
# Create an UPS user. We do not use the buggy macro %_pre_groupadd anymore.
%_pre_useradd ups %{STATEPATH} /bin/false
%_pre_groupadd ups ups
%_pre_groupadd tty ups
%_pre_groupadd usb ups

%preun	server
%_preun_service upsd || :

%post	server
%_post_service upsd || :

%postun	server
# Only do this if it is not an upgrade
if [ ! -f %_sbindir/upsmon ]; then
   %_postun_userdel ups
fi

%post cgi
%_post_webapp

%postun cgi
%_postun_webapp

%clean
rm -rf %{buildroot}

%files	server
%defattr(-,root,root)
%{DRVPATH}/*
%{_sbindir}/upsd
%attr(0744,root,root) %{_initrddir}/upsd
%attr(0755,root,root) %dir %{CONFPATH}
%attr(0644,root,root) %config(noreplace) %{CONFPATH}/ups.conf
%attr(0640,root,ups) %config(noreplace) %{CONFPATH}/upsd.users
%attr(0640,root,ups) %config(noreplace) %{CONFPATH}/upsd.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/udev/rules.d/70-nut-usbups.rules
%{_datadir}/cmdvartab
%{_datadir}/driver.list
%{_mandir}/man5/ups.conf.5*
%{_mandir}/man5/upsd.conf.5*
%{_mandir}/man5/upsd.users.5*
%{_mandir}/man8/belkin.8*
%{_mandir}/man8/belkinunv.8*
%{_mandir}/man8/bestups.8*
%{_mandir}/man8/bestuferrups.8*
%{_mandir}/man8/cyberpower.8*
%{_mandir}/man8/cpsups.8*
%{_mandir}/man8/everups.8*
%{_mandir}/man8/etapro.8*
%{_mandir}/man8/fentonups.8*
%{_mandir}/man8/genericups.8*
%{_mandir}/man8/isbmex.8*
%{_mandir}/man8/liebert.8*
%{_mandir}/man8/masterguard.8*
%{_mandir}/man8/mge-utalk.8*
%{_mandir}/man8/apcsmart.8*
%{_mandir}/man8/nutupsdrv.8*
%{_mandir}/man8/oneac.8*
%{_mandir}/man8/powercom.8*
%{_mandir}/man8/sms.8*
%{_mandir}/man8/snmp-ups.8*
%{_mandir}/man8/tripplite.8*
%{_mandir}/man8/tripplitesu.8*
%{_mandir}/man8/victronups.8*
%{_mandir}/man8/upsd.8*
%{_mandir}/man8/upsdrvctl.8*
%{_mandir}/man8/mge-shut.8*
%{_mandir}/man8/energizerups.8*
%{_mandir}/man8/safenet.8*
%{_mandir}/man8/hidups.8*
%{_mandir}/man8/newhidups.8*
%{_mandir}/man8/ippon.8*
%{_mandir}/man8/bestfcom.8*
%{_mandir}/man8/metasys.8*
%{_mandir}/man8/mustek.8*
%{_mandir}/man8/bcmxcp.8*
%{_mandir}/man8/bcmxcp_usb.8*
%{_mandir}/man8/solis.8*
%{_mandir}/man8/tripplite_usb.8*
%{_mandir}/man8/upscode2.8*
%{_mandir}/man8/al175.8*
%{_mandir}/man8/dummy-ups.8*
%{_mandir}/man8/megatec.8*
%{_mandir}/man8/nitram.8*
%{_mandir}/man8/optiups.8*
%{_mandir}/man8/powerpanel.8*

%files
%defattr(-,root,root)
%doc ChangeLog COPYING CREDITS INSTALL MAINTAINERS NEWS README UPGRADING docs
%attr(0755,root,root) %dir %{CONFPATH}
%attr(0744,root,root) %{_initrddir}/upsmon
%attr(0640,root,ups) %config(noreplace) %{CONFPATH}/upssched.conf
%attr(0640,root,ups) %{CONFPATH}/upsmon.conf.sample
%attr(0750,ups,ups) %dir %{STATEPATH}
%{_bindir}/upsc
%{_bindir}/upscmd
%{_bindir}/upsrw
%{_bindir}/upslog
%{_sbindir}/upsmon
%{_sbindir}/upssched
%{_mandir}/man5/upsmon.conf.5*
%{_mandir}/man5/upssched.conf.5*
%{_mandir}/man8/upsc.8*
%{_mandir}/man8/upscmd.8*
%{_mandir}/man8/upsrw.8*
%{_mandir}/man8/upslog.8*
%{_mandir}/man8/upsmon.8*
%{_mandir}/man8/upssched.8*
%{_mandir}/man8/upsset.cgi.8*

%files cgi
%defattr(-,root,root)
%dir %attr(0755,root,root) %{CONFPATH}
# The apache user will have to read this 3 files
%attr(0644,root,root) %config(noreplace) %{CONFPATH}/hosts.conf
%attr(0644,root,root) %config(noreplace) %{CONFPATH}/upsset.conf
%attr(0644,root,root) %config(noreplace) %{CONFPATH}/upsstats.html
%attr(0644,root,root) %config(noreplace) %{CONFPATH}/upsstats-single.html
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}-cgi.conf
%{CGIPATH}/upsimage.cgi
%{CGIPATH}/upsset.cgi
%{CGIPATH}/upsstats.cgi
%dir %attr(0755,root,root) %{HTMLPATH}
%attr(0644,root,root) %{HTMLPATH}/bottom.html
%attr(0644,root,root) %{HTMLPATH}/header.html
%attr(0644,root,root) %{HTMLPATH}/index.html
%attr(0644,root,root) %{HTMLPATH}/nut-banner.png
%{_mandir}/man5/hosts.conf.5*
%{_mandir}/man5/upsstats.html.5*
%{_mandir}/man5/upsset.conf.5*
%{_mandir}/man8/upsimage.cgi.8*
%{_mandir}/man8/upsset.cgi.8*
%{_mandir}/man8/upsstats.cgi.8*

%files devel
%defattr(-,root,root)
%{_bindir}/libupsclient-config
%{_includedir}/*.h
%{_libdir}/libupsclient.a
%{_libdir}/pkgconfig/libupsclient.pc
%{_mandir}/man3/upscli_*.3*


