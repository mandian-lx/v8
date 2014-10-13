%define major 3
%define libname %mklibname %{name}_ %major
%define libpreparser %mklibname %{name}preparser %major
%define develname %mklibname %name -d

%define somajor 3
%define sominor 20
%define sobuild 17.15
%define sover %{somajor}.%{sominor}.%{sobuild}

%ifarch %{ix86}
%define target ia32
%endif
%ifarch x86_64
%define target x64
%endif
%ifarch %arm
%define target arm
%endif

Name:		v8
Version:	%{sover}
Release:	10
Summary:	JavaScript Engine
Group:		System/Libraries
License:	BSD
URL:		http://code.google.com/p/v8
Source0:	http://commondatastorage.googleapis.com/chromium-browser-official/%{name}-%{somajor}.%{sominor}.%{sobuild}.tar.bz2
ExclusiveArch:	%{ix86} x86_64 %arm
BuildRequires:	readline-devel
BuildRequires:	icu-devel

%description
V8 is Google's open source JavaScript engine.
V8 is written in C++ and is used 
in Google Chrome, the open source browser from Google.
V8 implements ECMAScript as specified in ECMA-262, 3rd edition.

%files
%doc AUTHORS ChangeLog LICENSE
%{_bindir}/d8

#--------------------------------------------------------------------

%package -n %libname
Summary:    JavaScript Engine
Group:      System/Libraries
Conflicts:  %name < 3.12.8 

%description -n %libname
V8 is Google's open source JavaScript engine.
V8 is written in C++ and is used 
in Google Chrome, the open source browser from Google.

%files -n %libname
%{_libdir}/lib%{name}.so.%{major}*

#--------------------------------------------------------------------

%package  -n %develname
Group:      System/Libraries 
Summary:    Development headers and libraries for v8
Requires:   %{libname} = %{version}-%{release}
Obsoletes:  %name-devel < %version-%release
Provides:   %name-devel = %version-%release

%description -n %develname
Development headers and libraries for v8.

%files -n %develname
%{_includedir}/*.h
%{_includedir}/v8
%{_libdir}/*.so

#--------------------------------------------------------------------

%prep
%setup -qn %{name}-%{version}
# Make sure no bundled libraries are used.
find third_party -type f \! -iname '*.gyp*' -delete

%build
%setup_compile_flags
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"
export LINK="%{__cxx}"


# configure sources
%__python2 build/gyp_v8 --depth=. -Dcomponent=shared_library \
		-Dsoname_version=%{somajor} \
		-Dv8_target_arch=%{target} \
%ifarch armv7hl
		-Dv8_use_arm_eabi_hardfloat=true \
%endif	
%ifarch armv7l
		-Dv8_use_arm_eabi_hardfloat=false \
%endif
%ifarch %arm
		-Darmv7=1 \
		-Darm_neon=1 \
%endif
		-Dconsole=readline \
		-Duse_system_icu=1 \
		-Dv8_enable_i18n_support=1 \
		-Dwerror= \
		--generator-output=out -f make

%make -C out builddir=$(pwd)/out/%{target}.release V=1 BUILDTYPE=Release mksnapshot.%{target}
%make -C out builddir=$(pwd)/out/%{target}.release V=1 BUILDTYPE=Release

%install
mkdir -p %{buildroot}%{_includedir}
mkdir -p %{buildroot}%{_libdir}
install -p include/*.h %{buildroot}%{_includedir}

mkdir -p %{buildroot}%{_includedir}/v8/x64
install -p src/*.h %{buildroot}%{_includedir}/v8
install -p src/x64/*.h %{buildroot}%{_includedir}/v8/x64

install -p out/%{target}.release/lib.target/libv8.so* %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_bindir}
install -p -m0755 out/%{target}.release/d8 %{buildroot}%{_bindir}

pushd %{buildroot}%{_libdir}
mv libv8.so.%{somajor} libv8.so.%{version}
ln -sf libv8.so.%{version} libv8.so.%{somajor}.%{sominor}
ln -sf libv8.so.%{version} libv8.so.%{somajor}
ln -sf libv8.so.%{version} libv8.so
popd

chmod -x %{buildroot}%{_includedir}/v8/*.h
