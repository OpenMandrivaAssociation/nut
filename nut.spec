%define build_hal 0
%{?_without_hal:        %global build_hal 0}
%{?_with_hal:           %global build_hal 1}

%define	major 0
%define libname	%mklibname upsclient %{major}

%define nutuser ups

Summary:	Network UPS Tools Client Utilities
Name:		nut
Version:	2.2.0
Release:	%mkrel 4
Epoch:		1
License:	GPL
Group:		System/Configuration/Hardware
URL:		http://random.networkupstools.org
Source0:	http://random.networkupstools.org/source/2.0/%{name}-%{version}.tar.gz
Source1:	http://random.networkupstools.org/source/2.0/%{name}-%{version}.tar.gz.sig
Source2:	upsd.init
Source3:	upsmon.init
Patch0:		nut-upsset.conf.diff
Patch1:		nut-mdv_conf.diff
Requires(pre):	chkconfig coreutils rpm-helper >= 0.8
BuildRequires:	autoconf2.5
BuildRequires:	freetype2-devel
BuildRequires:	libgd-devel >= 2.0.5
BuildRequires:	libjpeg-devel
BuildRequires:	libpng-devel
BuildRequires:	libtool
BuildRequires:	libusb-devel
BuildRequires:	net-snmp-devel
BuildRequires:	pkgconfig
BuildRequires:	xpm-devel
BuildRequires:	openssl-devel
%if %{build_hal}
BuildRequires:	dbus-glib-devel
BuildRequires:	dbus-devel
BuildRequires:	libhal-devel >= 0.5.8
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
These programs are part of a developing project to monitor the assortment of
UPSes that are found out there in the field. Many models have serial ports of
some kind that allow some form of state checking. This capability has been
harnessed where possible to allow for safe shutdowns, live status tracking on
web pages, and more.

This package includes the client utilities that are required to monitor a UPS
that the client host is powered from - either connected directly via a serial
port (in which case the nut-server package needs to be installed on this
machine) or across the network (where another host on the network monitors the
UPS via serial cable and runs the main nut package to allow clients to see the
information).

%package -n	%{libname}
Summary:	Network UPS Tools Client Utilities library
Group:          System/Libraries

%description -n	%{libname}
These programs are part of a developing project to monitor the assortment of
UPSes that are found out there in the field. Many models have serial ports of
some kind that allow some form of state checking. This capability has been
harnessed where possible to allow for safe shutdowns, live status tracking on
web pages, and more.

This package contains the shared libraries for NUT client applications.

%package	server
Summary:	Network UPS Tools server
Group:		System/Servers
Requires:	nut = %{epoch}:%{version}-%{release}
Requires(pre):	nut = %{epoch}:%{version}-%{release}
Requires(pre):	rpm-helper >= 0.8

%description	server
These programs are part of a developing project to monitor the assortment of
UPSes that are found out there in the field. Many models have serial ports of
some kind that allow some form of state checking. This capability has been
harnessed where possible to allow for safe shutdowns, live status tracking on
web pages, and more.

This package is the main NUT upsd daemon and the associated per-UPS-model
drivers which talk to the UPSes. You also need to install the base NUT package.

%package	cgi
Summary:	CGI utils for NUT
Group:		Monitoring
Requires:	apache
Requires(pre):	rpm-helper >= 0.8
Conflicts:	apcupsd

%description	cgi
These programs are part of a developing project to monitor the assortment of
UPSes that are found out there in the field. Many models have serial ports of
some kind that allow some form of state checking. This capability has been
harnessed where possible to allow for safe shutdowns, live status tracking on
web pages, and more.

This package adds the web CGI programs. These can be installed on a separate
machine to the rest of the NUT package.

%package	devel
Summary:	Development for NUT Client
Group:		Development/C
Requires(pre):	rpm-helper >= 0.8

%description	devel
These programs are part of a developing project to monitor the assortment of
UPSes that are found out there in the field. Many models have serial ports of
some kind that allow some form of state checking. This capability has been
harnessed where possible to allow for safe shutdowns, live status tracking on
web pages, and more.

This package contains the development header files and libraries
necessary to develop NUT client applications.

%prep

%setup -q
%patch0 -p0
%patch1 -p1

# instead of a patch
perl -pi -e "s|/cgi-bin/nut|/cgi-bin|g" data/html/*.html*

cp %{SOURCE2} upsd.init
cp %{SOURCE3} upsmon.init

%build
# this takes care of rpath
libtoolize --copy --force; aclocal -I m4; autoconf; automake --foreign --add-missing --copy

%serverbuild

%configure2_5x \
    --enable-shared \
    --sysconfdir=%{_sysconfdir}/ups \
    --with-serial \
    --with-usb \
    --with-snmp \
%if %{build_hal}
    --with-hal \
%endif
    --with-cgi \
    --with-lib \
    --with-ssl \
    --with-ipv6 \
    --with-gd-libs \
    --with-statepath=/var/state/ups \
    --with-drvpath=/sbin \
    --with-cgipath=/var/www/cgi-bin \
    --with-htmlpath=/var/www/nut \
    --with-pidpath=/var/run/nut \
    --with-port=3493 \
    --with-user=%{nutuser} \
    --with-group=%{nutuser} \
    --with-pkgconfig-dir=%{_libdir}/pkgconfig \
    --with-hotplug-dir=%{_sysconfdir}/hotplug \
    --with-udev-dir=%{_sysconfdir}/udev

%make

%install
rm -rf %{buildroot}

%makeinstall_std

install -d %{buildroot}/var/state/ups
install -d %{buildroot}/var/run/nut

# install SYSV init stuff
install -d %{buildroot}%{_initrddir}
install -m0755 upsd.init %{buildroot}%{_initrddir}/upsd
install -m0755 upsmon.init %{buildroot}%{_initrddir}/upsmon

# move the *.sample config files to their real locations
# we don't need to worry about overwriting anything since
# they are marked as %config files within the package
for file in %{buildroot}%{_sysconfdir}/ups/*.sample
do
    mv $file %{buildroot}%{_sysconfdir}/ups/`basename $file .sample`
done

mv %{buildroot}%{_sysconfdir}/ups/upsmon.conf %{buildroot}%{_sysconfdir}/ups/upsmon.conf.sample
perl -pi -e 's/# RUN_AS_USER nutmon/RUN_AS_USER %{nutuser}/g' %{buildroot}%{_sysconfdir}/ups/upsmon.conf.sample

cp -af data/driver.list docs/

# udev usb ups stuff
mv %{buildroot}%{_sysconfdir}/udev/rules.d/52_nut-usbups.rules %{buildroot}%{_sysconfdir}/udev/rules.d/70-nut-usbups.rules

# fix access config files
install -d %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d
cat > %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/%{name}-cgi.conf << EOF

<Files upsset.cgi>
    Order deny,allow
    Deny from all
    Allow from 127.0.0.1
    ErrorDocument 403 "Access denied per %{_sysconfdir}/httpd/conf/webapps.d/%{name}-cgi.conf"
</Files>

Alias /nut /var/www/nut

<Directory "/var/www/nut">
    Order deny,allow
    Deny from all
    Allow from 127.0.0.1
    ErrorDocument 403 "Access denied per %{_sysconfdir}/httpd/conf/webapps.d/%{name}-cgi.conf"
</Directory>

EOF

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%pre
# Create an UPS user.
%_pre_useradd %{nutuser} /var/state/ups /bin/false
%_pre_groupadd ups %{nutuser}
%_pre_groupadd tty %{nutuser}
%_pre_groupadd usb %{nutuser}
%_pre_groupadd uucp %{nutuser}

%preun
# only do this if it is not an upgrade
%_preun_service upsmon

%post
%_post_service upsmon

%postun
# Only do this if it is not an upgrade
if [ ! -f %_sbindir/upsd ]; then
   %_postun_userdel %{nutuser}
fi

%pre	server
# Create an UPS user. We do not use the buggy macro %_pre_groupadd anymore.
%_pre_useradd %{nutuser} /var/state/ups /bin/false
%_pre_groupadd ups %{nutuser}
%_pre_groupadd tty %{nutuser}
%_pre_groupadd usb %{nutuser}

%preun	server
%_preun_service upsd || :

%post	server
%_post_service upsd || :

%postun	server
# Only do this if it is not an upgrade
if [ ! -f %_sbindir/upsmon ]; then
   %_postun_userdel %{nutuser}
fi

%post cgi
%_post_webapp

%postun cgi
%_postun_webapp

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog MAINTAINERS NEWS README UPGRADING docs
%attr(0755,root,root) %dir %{_sysconfdir}/ups
%attr(0744,root,root) %{_initrddir}/upsmon
%attr(0640,root,%{nutuser}) %config(noreplace) %{_sysconfdir}/ups/upssched.conf
%attr(0640,root,%{nutuser}) %{_sysconfdir}/ups/upsmon.conf.sample
%attr(0750,%{nutuser},%{nutuser}) %dir /var/state/ups
%attr(0755,%{nutuser},%{nutuser}) %dir /var/run/nut
%{_bindir}/upsc
%{_bindir}/upscmd
%{_bindir}/upslog
%{_bindir}/upsrw
%{_bindir}/upssched-cmd
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

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/*.so.*

%files server
%defattr(-,root,root)
%{_sbindir}/upsd
%attr(0744,root,root) %{_initrddir}/upsd
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ups/ups.conf
%attr(0640,root,%{nutuser}) %config(noreplace) %{_sysconfdir}/ups/upsd.users
%attr(0640,root,%{nutuser}) %config(noreplace) %{_sysconfdir}/ups/upsd.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/udev/rules.d/70-nut-usbups.rules
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/hotplug/usb/libhid.usermap
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/hotplug/usb/libhidups
/sbin/al175
/sbin/apcsmart
/sbin/bcmxcp
/sbin/bcmxcp_usb
/sbin/belkin
/sbin/belkinunv
/sbin/bestfcom
/sbin/bestuferrups
/sbin/bestups
/sbin/cpsups
/sbin/cyberpower
/sbin/dummy-ups
/sbin/energizerups
/sbin/etapro
/sbin/everups
/sbin/gamatronic
/sbin/genericups
%if %{build_hal}
/sbin/hald-addon-bcmxcp_usb
/sbin/hald-addon-megatec_usb
/sbin/hald-addon-tripplite_usb
/sbin/hald-addon-usbhid-ups
%endif
/sbin/isbmex
/sbin/liebert
/sbin/masterguard
/sbin/megatec
/sbin/megatec_usb
/sbin/metasys
/sbin/mge-shut
/sbin/mge-utalk
/sbin/newmge-shut
/sbin/nitram
/sbin/oneac
/sbin/optiups
/sbin/powercom
/sbin/powerpanel
/sbin/rhino
/sbin/safenet
/sbin/skel
/sbin/snmp-ups
/sbin/solis
/sbin/tripplite
/sbin/tripplitesu
/sbin/tripplite_usb
/sbin/upscode2
/sbin/upsdrvctl
/sbin/usbhid-ups
/sbin/victronups
%{_datadir}/cmdvartab
%{_datadir}/driver.list
%{_mandir}/man5/ups.conf.5*
%{_mandir}/man5/upsd.conf.5*
%{_mandir}/man5/upsd.users.5*
%{_mandir}/man8/al175.8*
%{_mandir}/man8/apcsmart.8*
%{_mandir}/man8/bcmxcp.8*
%{_mandir}/man8/bcmxcp_usb.8*
%{_mandir}/man8/belkin.8*
%{_mandir}/man8/belkinunv.8*
%{_mandir}/man8/bestfcom.8*
%{_mandir}/man8/bestuferrups.8*
%{_mandir}/man8/bestups.8*
%{_mandir}/man8/cpsups.8*
%{_mandir}/man8/cyberpower.8*
%{_mandir}/man8/dummy-ups.8*
%{_mandir}/man8/energizerups.8*
%{_mandir}/man8/etapro.8*
%{_mandir}/man8/everups.8*
%{_mandir}/man8/gamatronic.8*
%{_mandir}/man8/genericups.8*
%{_mandir}/man8/isbmex.8*
%{_mandir}/man8/liebert.8*
%{_mandir}/man8/masterguard.8*
%{_mandir}/man8/megatec.8*
%{_mandir}/man8/megatec_usb.8*
%{_mandir}/man8/metasys.8*
%{_mandir}/man8/mge-shut.8*
%{_mandir}/man8/mge-utalk.8*
%{_mandir}/man8/nitram.8*
%{_mandir}/man8/nutupsdrv.8*
%{_mandir}/man8/oneac.8*
%{_mandir}/man8/optiups.8*
%{_mandir}/man8/powercom.8*
%{_mandir}/man8/powerpanel.8*
%{_mandir}/man8/rhino.8*
%{_mandir}/man8/safenet.8*
%{_mandir}/man8/snmp-ups.8*
%{_mandir}/man8/solis.8*
%{_mandir}/man8/tripplite.8*
%{_mandir}/man8/tripplitesu.8*
%{_mandir}/man8/tripplite_usb.8*
%{_mandir}/man8/upscode2.8*
%{_mandir}/man8/upsd.8*
%{_mandir}/man8/upsdrvctl.8*
%{_mandir}/man8/usbhid-ups.8*
%{_mandir}/man8/victronups.8*

%if %{build_hal}
/sbin/hald-addon-bcmxcp_usb
/sbin/hald-addon-megatec_usb
/sbin/hald-addon-tripplite_usb
/sbin/hald-addon-usbhid-ups
%endif

%files cgi
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ups/hosts.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ups/upsset.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ups/upsstats.html
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ups/upsstats-single.html
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}-cgi.conf
/var/www/cgi-bin/upsimage.cgi
/var/www/cgi-bin/upsset.cgi
/var/www/cgi-bin/upsstats.cgi
%dir %attr(0755,root,root) /var/www/nut
%attr(0644,root,root) /var/www/nut/bottom.html
%attr(0644,root,root) /var/www/nut/header.html
%attr(0644,root,root) /var/www/nut/index.html
%attr(0644,root,root) /var/www/nut/nut-banner.png
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
%{_libdir}/*.la
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/pkgconfig/*.pc
%{_mandir}/man3/upscli_*.3*
%{_mandir}/man3/upsclient.3*
