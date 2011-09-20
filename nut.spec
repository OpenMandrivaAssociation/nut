%define build_hal 1
%{?_without_hal: %global build_hal 0}
%{?_with_hal: %global build_hal 1}

%define build_neonxml 1
%{?_without_neonxml: %global build_neonxml 0}
%{?_with_neonxml: %global build_neonxml 1}

%define build_doc 0
%{?_without_doc: %global build_doc 0}
%{?_with_doc: %global build_doc 1}

%define	major 1
%define libname	%mklibname upsclient %{major}

%define nutuser ups

%if %mdkversion <= 200700
%define build_neonxml 0
%define build_hal 0
%endif

Summary:	Network UPS Tools Client Utilities
Name:		nut
Version:	2.6.2
Release:	%mkrel 1
Epoch:		1
License:	GPLv2
Group:		System/Configuration/Hardware
URL:		http://www.networkupstools.org/
Source0:	http://www.networkupstools.org/source/2.6/%{name}-%{version}.tar.gz
Source1:	http://www.networkupstools.org/source/2.6/%{name}-%{version}.tar.gz.sig
Source2:	upsd.init
Source3:	upsmon.init
Patch0:		nut-upsset.conf.diff
Patch1:		nut-mdv_conf.diff
Requires(pre):	rpm-helper
Requires(post):	rpm-helper
Requires(postun): rpm-helper
Requires(preun): rpm-helper
BuildRequires:	autoconf2.5
BuildRequires:	freetype2-devel
BuildRequires:	genders-devel
BuildRequires:	libgd-devel >= 2.0.5
BuildRequires:	libjpeg-devel
BuildRequires:	libpng-devel
BuildRequires:	libtool
BuildRequires:	libusb-devel
BuildRequires:	net-snmp-devel
BuildRequires:	openssl-devel
BuildRequires:	pkgconfig
BuildRequires:	powerman-devel
BuildRequires:	tcp_wrappers-devel
BuildRequires:	xpm-devel
%if %{build_neonxml}
BuildRequires:	neon-devel >= 0.25.0
%endif
%if %{build_hal}
BuildRequires:	dbus-glib-devel
BuildRequires:	dbus-devel
BuildRequires:	libhal-devel >= 0.5.8
%endif
%if %{build_doc}
BuildRequires:	dblatex
BuildRequires:	asciidoc >= 8.6.3
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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
Requires:	nut >= %{epoch}:%{version}-%{release}
Requires(pre):	nut >= %{epoch}:%{version}-%{release}
Requires(pre):	rpm-helper >= 0.8
Requires:	tcp_wrappers

%description	server
These programs are part of a developing project to monitor the assortment of
UPSes that are found out there in the field. Many models have serial ports of
some kind that allow some form of state checking. This capability has been
harnessed where possible to allow for safe shutdowns, live status tracking on
web pages, and more.

This package is the main NUT upsd daemon and the associated per-UPS-model
drivers which talk to the UPSes. You also need to install the base NUT package.

%if %{build_hal}
%package	drivers-hal
Summary:	Network UPS Tools HAL drivers
Group:		System/Servers
Requires:	nut-server >= %{epoch}:%{version}-%{release}
Requires(pre):	nut-server >= %{epoch}:%{version}-%{release}

%description	drivers-hal
This package contains the NUT HAL drivers.
%endif

%package	cgi
Summary:	CGI utils for NUT
Group:		Monitoring
Requires:	apache
%if %mdkversion < 201010
Requires(post):   rpm-helper
Requires(postun):   rpm-helper
%endif
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
Requires:	%{libname} >= %{epoch}:%{version}

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
%patch0 -p0 -b .upsset.conf
%patch1 -p1 -b .mdv_conf

# instead of a patch
perl -pi -e "s|/cgi-bin/nut|/cgi-bin|g" data/html/*.html*

cp %{SOURCE2} upsd.init
cp %{SOURCE3} upsmon.init

%build
# this takes care of rpath
#libtoolize --copy --force; aclocal -I m4; autoconf; automake --foreign --add-missing --copy

%serverbuild

%configure2_5x \
    --enable-static \
    --enable-shared \
    --sysconfdir=%{_sysconfdir}/ups \
    --with-serial \
    --with-usb \
    --with-snmp \
%if %{build_hal}
    --with-hal \
%endif
    --with-cgi \
    --with-dev \
    --with-ssl \
%if %{build_neonxml}
    --with-neon \
%endif
%if %{build_doc}
    --with-doc \
%endif
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
mv %{buildroot}%{_sysconfdir}/udev/rules.d/52-nut-usbups.rules %{buildroot}%{_sysconfdir}/udev/rules.d/70-nut-usbups.rules

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

# install missing (forgotten?) headers
install -m0644 tools/nut-scanner/*.h %{buildroot}%{_includedir}/

# cleanup
rm -f %{buildroot}%{_sysconfdir}/ups/nut.conf

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%pre
# Create an UPS user
%_pre_useradd %{nutuser} /var/state/ups /bin/false
%{_sbindir}/usermod -G dialout,tty,usb %{nutuser}

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
%{_sbindir}/usermod -G dialout,tty,usb %{nutuser}

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
%if %mdkversion < 201010
%_post_webapp
%endif

%postun cgi
%if %mdkversion < 201010
%_postun_webapp
%endif

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
%{_bindir}/nut-scanner
%{_bindir}/upsc
%{_bindir}/upscmd
%{_bindir}/upslog
%{_bindir}/upsrw
%{_bindir}/upssched-cmd
%{_sbindir}/upsmon
%{_sbindir}/upssched
%{_mandir}/man5/upsmon.conf.5*
%{_mandir}/man5/upssched.conf.5*
%{_mandir}/man8/nut-scanner.8*
%{_mandir}/man8/upsc.8*
%{_mandir}/man8/upscmd.8*
%{_mandir}/man8/upslog.8*
%{_mandir}/man8/upsmon.8*
%{_mandir}/man8/upsrw.8*
%{_mandir}/man8/upssched.8*
%{_mandir}/man8/upsset.cgi.8*

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/*.so.%{major}*

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
/sbin/apcsmart
/sbin/apcsmart-old
/sbin/bcmxcp
/sbin/bcmxcp_usb
/sbin/belkin
/sbin/belkinunv
/sbin/bestfcom
/sbin/bestfortress
/sbin/bestuferrups
/sbin/bestups
/sbin/blazer_ser
/sbin/blazer_usb
/sbin/clone
/sbin/clone-outlet
/sbin/dummy-ups
/sbin/etapro
/sbin/everups
/sbin/gamatronic
/sbin/genericups
/sbin/isbmex
/sbin/ivtscd
/sbin/liebert
/sbin/liebert-esp2
/sbin/masterguard
/sbin/metasys
/sbin/mge-shut
/sbin/mge-utalk
/sbin/microdowell
/sbin/newmge-shut
/sbin/oneac
/sbin/optiups
/sbin/powercom
/sbin/powerman-pdu
/sbin/powerpanel
/sbin/rhino
/sbin/richcomm_usb
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
%if %{build_neonxml}
/sbin/netxml-ups
%endif
%{_datadir}/cmdvartab
%{_datadir}/driver.list
%{_mandir}/man5/nut.conf.5*
%{_mandir}/man5/ups.conf.5*
%{_mandir}/man5/upsd.conf.5*
%{_mandir}/man5/upsd.users.5*
%{_mandir}/man8/apcsmart.8*
%{_mandir}/man8/apcsmart-old.8*
%{_mandir}/man8/bcmxcp.8*
%{_mandir}/man8/bcmxcp_usb.8*
%{_mandir}/man8/belkin.8*
%{_mandir}/man8/belkinunv.8*
%{_mandir}/man8/bestfcom.8*
%{_mandir}/man8/bestfortress.8*
%{_mandir}/man8/bestuferrups.8*
%{_mandir}/man8/bestups.8*
%{_mandir}/man8/blazer.8*
%{_mandir}/man8/clone.8*
%{_mandir}/man8/dummy-ups.8*
%{_mandir}/man8/etapro.8*
%{_mandir}/man8/everups.8*
%{_mandir}/man8/gamatronic.8*
%{_mandir}/man8/genericups.8*
%{_mandir}/man8/isbmex.8*
%{_mandir}/man8/ivtscd.8*
%{_mandir}/man8/liebert.8*
%{_mandir}/man8/liebert-esp2.8*
%{_mandir}/man8/masterguard.8*
%{_mandir}/man8/metasys.8*
%{_mandir}/man8/mge-shut.8*
%{_mandir}/man8/mge-utalk.8*
%{_mandir}/man8/microdowell.8*
%{_mandir}/man8/nutupsdrv.8*
%{_mandir}/man8/oneac.8*
%{_mandir}/man8/optiups.8*
%{_mandir}/man8/powercom.8*
%{_mandir}/man8/powerman-pdu.8*
%{_mandir}/man8/powerpanel.8*
%{_mandir}/man8/rhino.8*
%{_mandir}/man8/richcomm_usb.8*
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
%if %{build_neonxml}
%{_mandir}/man8/netxml-ups.8*
%endif

%if %{build_hal}
%files drivers-hal
%defattr(-,root,root)
%{_libdir}/hal/hald-addon-bcmxcp_usb
%{_libdir}/hal/hald-addon-blazer_usb
%{_libdir}/hal/hald-addon-tripplite_usb
%{_libdir}/hal/hald-addon-usbhid-ups
%{_datadir}/hal/fdi/information/20thirdparty/20-ups-nut-device.fdi
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
%{_includedir}/*.h
%{_libdir}/*.so
%{_libdir}/*.*a
%{_libdir}/pkgconfig/*.pc
%{_mandir}/man3/upscli_*.3*
%{_mandir}/man3/upsclient.3*
%{_mandir}/man3/nutscan_add_device_to_device.3*
%{_mandir}/man3/nutscan_add_option_to_device.3*
%{_mandir}/man3/nutscan_cidr_to_ip.3*
%{_mandir}/man3/nutscan_display_parsable.3*
%{_mandir}/man3/nutscan_display_ups_conf.3*
%{_mandir}/man3/nutscan_free_device.3*
%{_mandir}/man3/nutscan_new_device.3*
%{_mandir}/man3/nutscan_scan_avahi.3*
%{_mandir}/man3/nutscan_scan_ipmi.3*
%{_mandir}/man3/nutscan_scan_nut.3*
%{_mandir}/man3/nutscan_scan_snmp.3*
%{_mandir}/man3/nutscan_scan_usb.3*
%{_mandir}/man3/nutscan_scan_xml_http.3*
