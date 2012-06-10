# Hi Googlers! If you're looking in here for patches, nifty.
# You (and everyone else) are welcome to use any of my Chromium patches under the terms of the GPLv2 or later.
# You (and everyone else) are welcome to use any of my V8-specific patches under the terms of the BSD license.
# You (and everyone else) may NOT use my patches under any other terms.
# I hate to be a party-pooper here, but I really don't want to help Google make a proprietary browser.
# There are enough of those already.
# All copyrightable work in these spec files and patches is Copyright 2010 Tom Callaway

# For the 1.2 branch, we use 0s here
# For 1.3+, we use the three digit versions


%define libname %mklibname v8
%define develname %mklibname v8 -d



%ifarch x86_64
%define archrel x64.release
%endif

%ifarch %ix86
%define archrel ia32.release
%endif

%define soname_ver 3.10.8

%global somajor 3
%global sominor 10
%global sobuild 8.13
%global sover %{somajor}.%{sominor}.%{sobuild}
%{!?python_sitelib: %global python_sitelib %(%{__python} \
    -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:	    v8
Version:    %{somajor}.%{sominor}.%{sobuild}
Release:    3
Summary:    JavaScript Engine
Group:      System/Libraries
License:    BSD
URL:        http://code.google.com/p/v8
Source0:    http://commondatastorage.googleapis.com/chromium-browser-official/%{name}-%{somajor}.%{sominor}.%{sobuild}.tar.bz2
ExclusiveArch:    %{ix86} x86_64 arm
BuildRequires:    scons
BuildRequires:    readline-devel
BuildRequires:    icu-devel >= 49
Obsoletes:		  v8 < %{version}-%{release}

%description
V8 is Google's open source JavaScript engine. V8 is written in C++ and is used 
in Google Chrome, the open source browser from Google. V8 implements ECMAScript 
as specified in ECMA-262, 3rd edition.

%files
%doc AUTHORS ChangeLog LICENSE
%{_bindir}/d8


%package -n %libname
Group:      System/Libraries
Summary:    libraries for v8
Requires:   %{name} = %{version}-%{release}

%description -n %libname
Library for V8 Google's open source JavaScript engine.


%files -n %libname
%{_libdir}/*.so.*

#--------------------------------------------------------------------

%package -n %develname
Group:      System/Libraries 
Summary:    Development headers and libraries for v8
Requires:   %{libname} = %{version}-%{release}
Requires:   %{name} = %{version}-%{release}
Provides:   %{name}-devel = %{version}-%{release}
Obsoletes:	%{name}-devel < %{version}-%{release}

%description -n %develname
Development headers and libraries for v8.

%files -n %develname
%{_includedir}/*.h
%{_includedir}/v8/extensions/
%{_libdir}/*.so
%{python_sitelib}/j*.py*

#--------------------------------------------------------------------

%prep
%setup -q -n %{name}-%{version}

# clear spurious executable bits
find . \( -name \*.cc -o -name \*.h -o -name \*.py \) -a -executable \
  |while read FILE ; do
    echo $FILE
    chmod -x $FILE
  done


%build
	
	
make -j3 GYP_GENERATORS=make  V=1 werror=no \
	library=shared \
	snapshots=on \
	soname_version=%{sover} \
	visibility=default \
	%{archrel}	


%install
mkdir -p %{buildroot}%{_includedir}
mkdir -p %{buildroot}%{_libdir}
install -p include/*.h %{buildroot}%{_includedir}
install -p out/%{archrel}/lib.target//libv8.so.%{sover} %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_bindir}
install -p -m0755 out/%{archrel}/d8 %{buildroot}%{_bindir}

chmod -x %{buildroot}%{_includedir}/v8*.h

mkdir -p %{buildroot}%{_includedir}/v8/extensions/experimental/
install -p src/extensions/*.h %{buildroot}%{_includedir}/v8/extensions/

chmod -x %{buildroot}%{_includedir}/v8/extensions/*.h

pushd %{buildroot}%{_libdir}
ln -sf libv8.so.%{sover} libv8.so
ln -sf libv8.so.%{sover} libv8.so.%{somajor}
ln -sf libv8.so.%{sover} libv8.so.%{somajor}.%{sominor}
popd






# install Python JS minifier scripts for nodejs
install -d %{buildroot}%{python_sitelib}
install -p -m0744 tools/jsmin.py %{buildroot}%{python_sitelib}/
chmod -R -x %{buildroot}%{python_sitelib}/*.py*
