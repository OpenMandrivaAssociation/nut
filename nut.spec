%define build_hal 0
%{?_without_hal: %global build_hal 0}
%{?_with_hal: %global build_hal 1}

%define build_doc 0
%{?_without_doc: %global build_doc 0}
%{?_with_doc: %global build_doc 1}

%define	major 1
%define libname	%mklibname upsclient %{major}

%define nutuser ups

Summary:	Network UPS Tools Client Utilities
Name:		nut
Version:	2.6.4
Release:	2
Epoch:		1
License:	GPLv2
Group:		System/Configuration/Hardware
URL:		http://www.networkupstools.org/
Source0:	http://www.networkupstools.org/source/2.6/%{name}-%{version}.tar.gz
Source1:	http://www.networkupstools.org/source/2.6/%{name}-%{version}.tar.gz.sig
Patch0:		nut-upsset.conf.diff
Patch1:		nut-mdv_conf.diff
Requires(pre):	rpm-helper
Requires(post):	rpm-helper
Requires(postun): rpm-helper
Requires(preun): rpm-helper
BuildRequires:	autoconf automake libtool
BuildRequires:	pkgconfig(freetype2)
BuildRequires:	genders-devel
BuildRequires:	libgd-devel >= 2.0.5
BuildRequires:	jpeg-devel
BuildRequires:	pkgconfig(libpng)
BuildRequires:	libusb-devel
BuildRequires:	net-snmp-devel
BuildRequires:	pkgconfig(openssl)
BuildRequires:	powerman-devel
BuildRequires:	tcp_wrappers-devel
BuildRequires:	xpm-devel
BuildRequires:  libtool-devel
BuildRequires:	neon-devel >= 0.25.0
%if %{build_hal}
BuildRequires:	dbus-glib-devel
BuildRequires:	dbus-devel
BuildRequires:	libhal-devel >= 0.5.8
%else
Obsoletes:		%{name}-drivers-hal < %{EVRD}
%endif
%if %{build_doc}
BuildRequires:	dblatex
BuildRequires:	asciidoc >= 8.6.3
%endif
BuildRequires:	libsystemd-daemon-devel
BuildRequires:	systemd-units

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
rm -f %{buildroot}%{_libdir}/*.*a
rm -f %{buildroot}%{_mandir}/man8/nut-recorder.8*

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

%files
%doc AUTHORS COPYING ChangeLog MAINTAINERS NEWS README UPGRADING docs
/lib/systemd/system-shutdown/nutshutdown
/lib/systemd/system/nut-driver.service
/lib/systemd/system/nut-monitor.service
%attr(0755,root,root) %dir %{_sysconfdir}/ups
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

%files -n %{libname}
%{_libdir}/*.so.%{major}*

%files server
/lib/systemd/system/nut-server.service
%{_sbindir}/upsd
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
%{_mandir}/man8/netxml-ups.8*

%if %{build_hal}
%files drivers-hal
%{_libdir}/hal/hald-addon-bcmxcp_usb
%{_libdir}/hal/hald-addon-blazer_usb
%{_libdir}/hal/hald-addon-tripplite_usb
%{_libdir}/hal/hald-addon-usbhid-ups
%{_datadir}/hal/fdi/information/20thirdparty/20-ups-nut-device.fdi
%endif

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


%changelog
* Tue Jun 05 2012 Oden Eriksson <oeriksson@mandriva.com> 1:2.6.4-1
+ Revision: 802595
- drop sysv scripts
- various fixes
- fix deps
- 2.6.4

* Tue Jan 24 2012 Glen Ogilvie <nelg@mandriva.org> 1:2.6.3-2
+ Revision: 767799
- minor fix.. type in BuildRequires
- Release: 2.6.3

* Tue Sep 20 2011 Oden Eriksson <oeriksson@mandriva.com> 1:2.6.2-1
+ Revision: 700494
- cleanup devel files
- added systemd stuff
- 2.6.2

* Mon Jul 18 2011 Oden Eriksson <oeriksson@mandriva.com> 1:2.6.1-2
+ Revision: 690298
- rebuilt against new net-snmp libs

* Mon Jun 06 2011 Oden Eriksson <oeriksson@mandriva.com> 1:2.6.1-1
+ Revision: 682912
- 2.6.1

* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 1:2.6.0-2
+ Revision: 666635
- mass rebuild

* Wed Jan 26 2011 Oden Eriksson <oeriksson@mandriva.com> 1:2.6.0-1
+ Revision: 632998
- 2.6.0

* Wed May 05 2010 Christophe Fergeau <cfergeau@mandriva.com> 1:2.4.3-3mdv2011.0
+ Revision: 542500
- patch3: upstream patch to fix deprecated syntax in udev rule

* Fri Apr 09 2010 Ahmad Samir <ahmadsamir@mandriva.org> 1:2.4.3-2mdv2010.1
+ Revision: 533279
- rebuild for openssl-1.0.0

* Sat Mar 06 2010 Oden Eriksson <oeriksson@mandriva.com> 1:2.4.3-1mdv2010.1
+ Revision: 515275
- 2.4.3
- drop upstream added patches
- rediff one patch
- patch some borked m4 (from 2.4.1)

* Fri Feb 26 2010 Oden Eriksson <oeriksson@mandriva.com> 1:2.4.1-8mdv2010.1
+ Revision: 511599
- rebuilt against openssl-0.9.8m

* Wed Feb 17 2010 Guillaume Rousse <guillomovitch@mandriva.org> 1:2.4.1-7mdv2010.1
+ Revision: 507251
- rely on filetrigger for reloading apache configuration begining with 2010.1, rpm-helper macros otherwise

  + Oden Eriksson <oeriksson@mandriva.com>
    - fix url

* Sun Jan 24 2010 Andrey Borzenkov <arvidjaar@mandriva.org> 1:2.4.1-6mdv2010.1
+ Revision: 495436
- patch2: replace obsolete udev keywords (mdv #57227)

* Thu Oct 15 2009 Oden Eriksson <oeriksson@mandriva.com> 1:2.4.1-5mdv2010.0
+ Revision: 457614
- rebuilt against new net-snmp libs

* Fri Oct 02 2009 Oden Eriksson <oeriksson@mandriva.com> 1:2.4.1-4mdv2010.0
+ Revision: 452738
- fix #53021 (wrong tty group at shutdown)

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 1:2.4.1-3mdv2010.0
+ Revision: 426261
- rebuild

* Wed Mar 11 2009 Oden Eriksson <oeriksson@mandriva.com> 1:2.4.1-2mdv2009.1
+ Revision: 353754
- bump release due to unknown build system problems
- 2.4.1

* Thu Jan 29 2009 Oden Eriksson <oeriksson@mandriva.com> 1:2.4.0-1mdv2009.1
+ Revision: 335059
- 2.4.0
- drop obsolete patches
- fix deps

* Fri Jan 09 2009 Frederic Crozat <fcrozat@mandriva.com> 1:2.2.2-7mdv2009.1
+ Revision: 327599
- use dialout group instead of uucp group

* Thu Dec 18 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.2.2-6mdv2009.1
+ Revision: 315543
- added P3 to fix build with -Werror=format-security (thanks fcrozat)

* Fri Sep 12 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.2.2-5mdv2009.0
+ Revision: 284161
- add hal support with a twist (nut-drivers-hal)

* Thu Aug 07 2008 Thierry Vignaud <tv@mandriva.org> 1:2.2.2-4mdv2009.0
+ Revision: 265200
- rebuild early 2009.0 package (before pixel changes)

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Sat May 24 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.2.2-3mdv2009.0
+ Revision: 210918
- fix build
- rebuild

* Wed May 14 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.2.2-2mdv2009.0
+ Revision: 207144
- make it backportable to CS4
- fix deps

* Tue May 13 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.2.2-1mdv2009.0
+ Revision: 206570
- 2.2.2

* Sun Feb 24 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.2.1-2mdv2008.1
+ Revision: 174415
- fix deps

* Sun Feb 24 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.2.1-1mdv2008.1
+ Revision: 174310
- added lsb tags into the init scripts
- 2.2.1
- rediffed P1

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Thu Dec 13 2007 Oden Eriksson <oeriksson@mandriva.com> 1:2.2.0-4mdv2008.1
+ Revision: 119519
- fix #36125 (Nut's UPSmon init script PID lock directory)

* Thu Aug 23 2007 Thierry Vignaud <tv@mandriva.org> 1:2.2.0-3mdv2008.0
+ Revision: 70384
- fileutils, sh-utils & textutils have been obsoleted by coreutils a long time ago

* Wed Aug 08 2007 Oden Eriksson <oeriksson@mandriva.com> 1:2.2.0-2mdv2008.0
+ Revision: 60175
- disable hal support for now, it's too experimental and
  conflicts with other drivers

* Sat Jul 07 2007 Oden Eriksson <oeriksson@mandriva.com> 1:2.2.0-1mdv2008.0
+ Revision: 49428
- fix deps (dbus-glib-devel, dbus-devel)
- fix deps (openssl-devel)
- 2.2.0
- remove obsolete patch (nut-2.0.1-lib64.patch)
- rediffed patches (nut-upsset.conf.diff and nut-mdv_conf.diff)
- cleanup the spec file a bit for new autofoo


* Fri Mar 09 2007 Oden Eriksson <oeriksson@mandriva.com> 2.0.5-3mdv2007.1
+ Revision: 138754
- use -fstack-protector-all on later gcc only

* Thu Mar 08 2007 Oden Eriksson <oeriksson@mandriva.com> 1:2.0.5-2mdv2007.1
+ Revision: 137655
- pass -fstack-protector-all to the CFLAGS

* Thu Feb 08 2007 Oden Eriksson <oeriksson@mandriva.com> 1:2.0.5-1mdv2007.1
+ Revision: 118111
- 2.0.5
- drop the bouissou2 patch, too difficult to apply
- added the html files

* Thu Nov 30 2006 Oden Eriksson <oeriksson@mandriva.com> 1:2.0.4-3mdv2007.1
+ Revision: 89344
- set correct owner of the /var/run/upsmon.pid file
- add some working but commented defaults for upsmon and upssched

* Wed Nov 29 2006 Oden Eriksson <oeriksson@mandriva.com> 1:2.0.4-2mdv2007.1
+ Revision: 88572
- added P1 to make upsset.cgi work
- add the uucp group membership (for /dev/ttyS0)
- fix apache config

* Tue Nov 28 2006 Oden Eriksson <oeriksson@mandriva.com> 1:2.0.4-1mdv2007.1
+ Revision: 88044
- Import nut

* Tue Nov 28 2006 Oden Eriksson <oeriksson@mandriva.com> 1:2.0.4-1mdv2007.1
- 2.0.4
- rediffed party upstread (in 2.0.2) patch (P0)
- added the udev rules file (thanks blino)

* Wed Aug 30 2006 Lenny Cartier <lenny@mandriva.com> 1:2.0.1-6mdv2007.0
- mkrel

* Wed Jan 04 2006 Oden Eriksson <oeriksson@mandriva.com> 2.0.1-5mdk
- rebuilt against new net-snmp with new major (10)

* Wed Dec 21 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.1-4mdk
- rebuilt against net-snmp that has new major (9)

* Sun Nov 13 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.1-3mdk
- rebuilt against openssl-0.9.8a

* Tue Mar 22 2005 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 2.0.1-2mdk
- lib64 fixes (again)

* Mon Feb 28 2005 Arnaud de Lorbeau <adelorbeau@mandrakesoft.com> 1:2.0.1-1mdk
- 2.0.1
- adapt patchs from Michel Bouissou

* Thu Feb 10 2005 Arnaud de Lorbeau <adelorbeau@mandrakesoft.com> 1:2.0.0-4mdk
- upsd poweroff script clean: remove the sleep and let the halt script continue
- add upsd service status option
- add Michel Bouissou's patch

* Sat Oct 23 2004 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 2.0.0-3mdk
- lib64 fixes

* Wed Oct 06 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 2.0.0-2mdk
- workaround buggy parrallel build
- package again driver list
- patch 2: fix compiling

* Fri Mar 26 2004 Arnaud de Lorbeau <adelorbeau@mandrakesoft.com> 2.0.0-1mdk
- 2.0.0

* Wed Mar 24 2004 Arnaud de Lorbeau <adelorbeau@mandrakesoft.com> 1.4.2-1mdk
- 1.4.2 final (with no changements from previous pre2 release)

* Tue Mar 16 2004 Arnaud de Lorbeau <adelorbeau@mandrakesoft.com> 1.4.2-0.pre2.1mdk
- New release with security and kernel 2.6 fixs
- Change URL

