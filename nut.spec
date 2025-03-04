%define build_doc 0
%{?_without_doc:	%global build_doc 0}
%{?_with_doc:	%global build_doc 1}

%define nutuser	ups
%define	scanmajor	1
%define upsmajor	4
%define clientmajor	0
%define libname	%mklibname nutscan %{scanmajor}
%define libups	%mklibname upsclient %{upsmajor}
%define libclient %mklibname nutclient %{clientmajor}

Summary:	Network UPS Tools Client Utilities
Name:		nut
Epoch:		1
Version:	2.7.2
Release:	8
License:	GPLv2
Group:		System/Configuration/Hardware
Url:		https://www.networkupstools.org/
Source0:	http://www.networkupstools.org/source/2.7/%{name}-%{version}.tar.gz
Patch0:	nut-upsset.conf.diff
Patch1:	nut-mdv_conf.diff
%if %{build_doc}
BuildRequires:	dblatex
BuildRequires:	asciidoc >= 8.6.3
%endif
BuildRequires:	libtool
BuildRequires:	libtool-devel
BuildRequires:	gd-devel >= 2.0.5
BuildRequires:	genders-devel
BuildRequires:	jpeg-devel
BuildRequires:	net-snmp-devel
BuildRequires:	tcp_wrappers-devel
BuildRequires:	pkgconfig(freetype2)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(libpowerman)
BuildRequires:	pkgconfig(libusb)
BuildRequires:	pkgconfig(neon)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(systemd)
BuildRequires:	pkgconfig(xpm)
BuildRequires:	systemd-units
Requires(pre,post,postun,preun):	rpm-helper

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
Group:		System/Libraries
Conflicts:	%{_lib}upsclient1 < 1:2.6.4-3

%description -n	%{libname}
This package contains a shared libraries for NUT client applications.

%package -n	%{libups}
Summary:	Network UPS Tools Client Utilities library
Group:		System/Libraries

%description -n	%{libups}
This package contains a shared libraries for NUT client applications.

%package -n     %{libclient}
Summary:        Network UPS Tools Client Utilities library
Group:          System/Libraries

%description -n %{libclient}
This package contains a shared libraries for NUT client applications.


%package	server
Summary:	Network UPS Tools server
Group:		System/Servers
Requires:	nut >= %{EVRD}
Requires(pre):	nut >= %{EVRD}
Requires(pre):	rpm-helper >= 0.8
Requires:	tcp_wrappers

%description	server
This package is the main NUT upsd daemon and the associated per-UPS-model
drivers which talk to the UPSes. You also need to install the base NUT package.

%package	cgi
Summary:	CGI utils for NUT
Group:		Monitoring
Requires:	apache
Conflicts:	apcupsd

%description	cgi
This package adds the web CGI programs. These can be installed on a separate
machine to the rest of the NUT package.

%package	devel 
Summary:	Development for NUT Client
Group:		Development/C
Requires:	%{libname} >= %{EVRD}
Requires:	%{libups} >= %{EVRD}
Requires:	%{libclient} >= %{EVRD}

%description	devel
This package contains the development header files and libraries
necessary to develop NUT client applications.

%prep
%setup -q
%patch0 -p0 -b .upsset.conf
%patch1 -p1 -b .mdv_conf

# instead of a patch
sed -i -e "s|/cgi-bin/nut|/cgi-bin|g" data/html/*.html*

%build
%serverbuild
%configure2_5x \
	--enable-static \
	--enable-shared \
	--sysconfdir=%{_sysconfdir}/ups \
	--with-serial \
	--with-usb \
	--with-snmp \
	--with-cgi \
	--with-dev \
	--with-ssl \
	--with-neon \
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
	--with-systemdsystemunitdir=%{_unitdir} \
	--with-pkgconfig-dir=%{_libdir}/pkgconfig \
	--with-hotplug-dir=%{_sysconfdir}/hotplug \
	--with-udev-dir=%{_sysconfdir}/udev

%make

%install
%makeinstall_std

install -d %{buildroot}/var/state/ups
install -d %{buildroot}/var/run/nut

# move the *.sample config files to their real locations
# we don't need to worry about overwriting anything since
# they are marked as %config files within the package
for file in %{buildroot}%{_sysconfdir}/ups/*.sample
do
    mv $file %{buildroot}%{_sysconfdir}/ups/`basename $file .sample`
done

perl -pi -e 's/# RUN_AS_USER nutmon/RUN_AS_USER %{nutuser}/g' %{buildroot}%{_sysconfdir}/ups/upsmon.conf

cp -af data/driver.list docs/

# udev usb ups stuff
mv %{buildroot}%{_sysconfdir}/udev/rules.d/52-nut-usbups.rules %{buildroot}%{_sysconfdir}/udev/rules.d/70-nut-usbups.rules

# fix access config files
install -d %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d
cat > %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/%{name}-cgi.conf << EOF

<Files upsset.cgi>
    Require all denied
    Require local granted
    ErrorDocument 403 "Access denied per %{_sysconfdir}/httpd/conf/webapps.d/%{name}-cgi.conf"
</Files>

Alias /nut /var/www/nut

<Directory "/var/www/nut">
    Require all denied
    Require local granted
    ErrorDocument 403 "Access denied per %{_sysconfdir}/httpd/conf/webapps.d/%{name}-cgi.conf"
</Directory>

EOF

# fix systemd location
mkdir -p %{buildroot}%{_unitdir}
mv %{buildroot}%{_libdir}/systemd/system/* %{buildroot}%{_unitdir}
mkdir -p %{buildroot}/lib/systemd/system-shutdown
mv %{buildroot}%{_libdir}/systemd/system-shutdown/* %{buildroot}/lib/systemd/system-shutdown

# install missing (forgotten?) headers
install -m0644 tools/nut-scanner/*.h %{buildroot}%{_includedir}/

# cleanup
rm -f %{buildroot}%{_sysconfdir}/ups/nut.conf
rm -f %{buildroot}%{_libdir}/*.*a
rm -f %{buildroot}%{_mandir}/man8/nut-recorder.8*

%pre
# Create an UPS user
%_pre_useradd %{nutuser} /var/state/ups /bin/false
%{_sbindir}/usermod -G dialout,tty,usb %{nutuser}

%preun
# only do this if it is not an upgrade
%_preun_service nut-monitor

%post
%_post_service nut-monitor

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
%_preun_service nut-server || :

%post	server
%_post_service nut-server || :

%postun	server
# Only do this if it is not an upgrade
if [ ! -f %_sbindir/upsmon ]; then
   %_postun_userdel %{nutuser}
fi

%files
%doc AUTHORS COPYING ChangeLog MAINTAINERS NEWS README UPGRADING docs
/lib/systemd/system-shutdown/nutshutdown
/lib/systemd/system/nut-driver.service
/lib/systemd/system/nut-monitor.service
%attr(0755,root,root) %dir %{_sysconfdir}/ups
%attr(0640,root,%{nutuser}) %config(noreplace) %{_sysconfdir}/ups/upssched.conf
%attr(0640,root,%{nutuser}) %{_sysconfdir}/ups/upsmon.conf
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

%files -n %{libname}
%{_libdir}/libnutscan.so.%{scanmajor}*

%files -n %{libups}
%{_libdir}/libupsclient.so.%{upsmajor}*

%files -n %{libclient}
%{_libdir}/libnutclient.so.%{clientmajor}*

%files server
/lib/systemd/system/nut-server.service
%{_sbindir}/upsd
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ups/ups.conf
%attr(0640,root,%{nutuser}) %config(noreplace) %{_sysconfdir}/ups/upsd.users
%attr(0640,root,%{nutuser}) %config(noreplace) %{_sysconfdir}/ups/upsd.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/udev/rules.d/70-nut-usbups.rules
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/hotplug/usb/libhid.usermap
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/hotplug/usb/libhidups
/sbin/al175
/sbin/apcupsd-ups
/sbin/nutdrv_atcl_usb
/sbin/nutdrv_qx
/sbin/oldmge-shut
/sbin/riello_ser
/sbin/riello_usb
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
%{_sbindir}/upsdrvctl
/sbin/usbhid-ups
/sbin/victronups
/sbin/netxml-ups
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
%{_mandir}/man8/netxml-ups.8*
%{_mandir}/man8/al175.8*
%{_mandir}/man8/apcupsd-ups.8*
%{_mandir}/man8/blazer_ser.8*
%{_mandir}/man8/blazer_usb.8*
%{_mandir}/man8/nutdrv_atcl_usb.8*
%{_mandir}/man8/nutdrv_qx.8*
%{_mandir}/man8/riello_ser.8*
%{_mandir}/man8/riello_usb.8*

%files cgi
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
%{_includedir}/*.h
%{_libdir}/*.so
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
%{_mandir}/man3/nutscan.3*
%{_mandir}/man3/nutscan_init.3*
%{_mandir}/man3/libnutclient.3.*
%{_mandir}/man3/libnutclient_commands.3.*
%{_mandir}/man3/libnutclient_devices.3.*
%{_mandir}/man3/libnutclient_general.3.*
%{_mandir}/man3/libnutclient_misc.3.*
%{_mandir}/man3/libnutclient_tcp.3.*
%{_mandir}/man3/libnutclient_variables.3.*
%{_mandir}/man3/nutclient_authenticate.3.*
%{_mandir}/man3/nutclient_destroy.3.*
%{_mandir}/man3/nutclient_device_forced_shutdown.3.*
%{_mandir}/man3/nutclient_device_login.3.*
%{_mandir}/man3/nutclient_device_master.3.*
%{_mandir}/man3/nutclient_execute_device_command.3.*
%{_mandir}/man3/nutclient_get_device_command_description.3.*
%{_mandir}/man3/nutclient_get_device_commands.3.*
%{_mandir}/man3/nutclient_get_device_description.3.*
%{_mandir}/man3/nutclient_get_device_num_logins.3.*
%{_mandir}/man3/nutclient_get_device_rw_variables.3.*
%{_mandir}/man3/nutclient_get_device_variable_description.3.*
%{_mandir}/man3/nutclient_get_device_variable_values.3.*
%{_mandir}/man3/nutclient_get_device_variables.3.*
%{_mandir}/man3/nutclient_get_devices.3.*
%{_mandir}/man3/nutclient_has_device.3.*
%{_mandir}/man3/nutclient_has_device_command.3.*
%{_mandir}/man3/nutclient_has_device_variable.3.*
%{_mandir}/man3/nutclient_logout.3.*
%{_mandir}/man3/nutclient_set_device_variable_value.3.*
%{_mandir}/man3/nutclient_set_device_variable_values.3.*
%{_mandir}/man3/nutclient_tcp_create_client.3.*
%{_mandir}/man3/nutclient_tcp_disconnect.3.*
%{_mandir}/man3/nutclient_tcp_get_timeout.3.*
%{_mandir}/man3/nutclient_tcp_is_connected.3.*
%{_mandir}/man3/nutclient_tcp_reconnect.3.*
%{_mandir}/man3/nutclient_tcp_set_timeout.3.*
%{_mandir}/man3/nutscan_get_serial_ports_list.3.*
%{_mandir}/man3/nutscan_scan_eaton_serial.3.*

