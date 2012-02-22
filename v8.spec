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



%global somajor 3
%global sominor 8
%global sobuild 9.8
%global sover %{somajor}.%{sominor}.%{sobuild}
%{!?python_sitelib: %global python_sitelib %(%{__python} \
    -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:       v8
Version:    %{somajor}.%{sominor}.%{sobuild}
Release:    2
Summary:    JavaScript Engine
Group:      System/Libraries
License:    BSD
URL:        http://code.google.com/p/v8
Source0:    v8-%{version}.tar.bz2
ExclusiveArch:    %{ix86} x86_64 arm
BuildRequires:    scons
BuildRequires:    readline-devel
BuildRequires:    icu-devel

%description
V8 is Google's open source JavaScript engine. V8 is written in C++ and is used 
in Google Chrome, the open source browser from Google. V8 implements ECMAScript 
as specified in ECMA-262, 3rd edition.

%files
%doc AUTHORS ChangeLog LICENSE
%{_bindir}/d8


%package -n %libname
Group:      System/Libraries
Summary:    Development headers and libraries for v8
Requires:   %{name} = %{version}-%{release}

%description -n %libname
Library for V8 Google's open source JavaScript engine.


%files -n %libname
%{_libdir}/*.so.*

#--------------------------------------------------------------------

%package -n %develname
Group:      System/Libraries 
Summary:    Development headers and libraries for v8
Requires:   %{name} = %{version}-%{release}
Provides:   v8-devel = %{version}-%{release}

%description -n %develname
Development headers and libraries for v8.

%files -n %develname
%{_includedir}/*.h
#%dir %{_includedir}/v8
%{_includedir}/v8/extensions/
%{_libdir}/*.so
%{python_sitelib}/j*.py*

#--------------------------------------------------------------------

%prep
%setup -q -n %{name}-%{version}

# -fno-strict-aliasing is needed with gcc 4.4 to get past some ugly code
PARSED_OPT_FLAGS=`echo \'$RPM_OPT_FLAGS -fPIC -fno-strict-aliasing -Wno-unused-parameter -Wno-unused-but-set-variable\'| sed "s/ /',/g" | sed "s/',/', '/g"`
sed -i "s|'-O3',|$PARSED_OPT_FLAGS,|g" SConstruct

# clear spurious executable bits
find . \( -name \*.cc -o -name \*.h -o -name \*.py \) -a -executable \
  |while read FILE ; do
    echo $FILE
    chmod -x $FILE
  done


%build
export GCC_VERSION="44"
scons library=shared snapshots=on \
%ifarch x86_64
arch=x64 \
%endif
visibility=default \
env=CCFLAGS:"-fPIC"

export ICU_LINK_FLAGS=`pkg-config --libs-only-l icu-i18n`

# When will people learn to create versioned shared libraries by default?
# first, lets get rid of the old .so file
rm -rf libv8.so libv8preparser.so
# Now, lets make it right.
g++ $RPM_OPT_FLAGS -fPIC -o libv8preparser.so.%{sover} -shared -Wl,-soname,libv8preparser.so.%{somajor} \
        obj/release/allocation.os \
        obj/release/hashmap.os \
        obj/release/preparse-data.os \
        obj/release/preparser-api.os \
        obj/release/preparser.os \
        obj/release/scanner.os \
        obj/release/token.os \
        obj/release/unicode.os

# "obj/release/preparser-api.os" should not be included in the libv8.so file.
export RELEASE_BUILD_OBJS=`echo obj/release/*.os | sed 's|obj/release/preparser-api.os||g'`

# We need to do this so d8 can link against it.
ln -sf libv8.so.%{sover} libv8.so
ln -sf libv8preparser.so.%{sover} libv8preparser.so

# This will fail to link d8 because it doesn't use the icu libs.
scons d8 \
%ifarch x86_64
arch=x64 \
%endif
library=shared snapshots=on console=readline visibility=default || :

# Sigh. I f*****g hate scons.
rm -rf d8

g++ $RPM_OPT_FLAGS -o d8 obj/release/d8.os -lpthread -lreadline -lpthread -L. -lv8 $ICU_LINK_FLAGS

%install
mkdir -p %{buildroot}%{_includedir}
mkdir -p %{buildroot}%{_libdir}
install -p include/*.h %{buildroot}%{_includedir}
install -p libv8.so.%{sover} %{buildroot}%{_libdir}
install -p libv8preparser.so.%{sover} %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_bindir}
install -p -m0755 d8 %{buildroot}%{_bindir}

pushd %{buildroot}%{_libdir}
ln -sf libv8.so.%{sover} libv8.so
ln -sf libv8.so.%{sover} libv8.so.%{somajor}
ln -sf libv8.so.%{sover} libv8.so.%{somajor}.%{sominor}
ln -sf libv8preparser.so.%{sover} libv8preparser.so
ln -sf libv8preparser.so.%{sover} libv8preparser.so.%{somajor}
ln -sf libv8preparser.so.%{sover} libv8preparser.so.%{somajor}.%{sominor}
popd

chmod -x %{buildroot}%{_includedir}/v8*.h

mkdir -p %{buildroot}%{_includedir}/v8/extensions/experimental/
install -p src/extensions/*.h %{buildroot}%{_includedir}/v8/extensions/
#install -p src/extensions/experimental/*.h %{buildroot}%{_includedir}/v8/extensions/experimental/

chmod -x %{buildroot}%{_includedir}/v8/extensions/*.h
#chmod -x %{buildroot}%{_includedir}/v8/extensions/experimental/*.h

# install Python JS minifier scripts for nodejs
install -d %{buildroot}%{python_sitelib}
install -p -m0744 tools/jsmin.py %{buildroot}%{python_sitelib}/
chmod -R -x %{buildroot}%{python_sitelib}/*.py*
