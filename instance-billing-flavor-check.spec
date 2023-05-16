Summary:   Cloud Billing Flavour Check
Name:      instance-billing-type-check
Version:   %%VERSION
Release:   0
License:   GPL3.0-only
Group:     Productivity/Networking/Web/Servers
URL:       https://github.com/SUSE-Enceladus/instance-billing-flavor-check
Source0:   %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-roo
Requires:  python3

%description
Check if instance is PAYG or BYOS

%prep
%setup -q

%build
python3 setup.py build

%install
python3 setup.py install --prefix=%{_prefix}  --root=%{buildroot}
mkdir -p %{buildroot}%{python3_sitelib}/instance_flavor_check

cp -r lib/*.py %{buildroot}%{python3_sitelib}/instance_flavor_check/
cp instance-flavor-check %{buildroot}%{_sbindir}/instance-flavor-check

%files
%defattr(-,root,root,-)
%doc README.md
%license LICENSE
%{_sbindir}/instance-flavor-check
%{python3_sitelib}/instance_flavor_check/*.py


%changelog
* Tue May 16 2023 Jesus Bermudez Velazquez <jesusbv@suse.com> - flavor-check
- Initial build.

