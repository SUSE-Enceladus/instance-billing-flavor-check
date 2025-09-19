#
# spec file for package python-instance-billing-type-check
#
# Copyright (c) 2023 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

%if 0%{?suse_version} >= 1600
%define pythons %{primary_python}
%else
%define pythons python3
%endif

Summary:        Cloud Billing Flavor Check
Name:           python-instance-billing-flavor-check
Version:        1.0.1
Release:        0
License:        GPL-3.0
Group:          Productivity/Networking/Web/Utilities
URL:            https://github.com/SUSE-Enceladus/instance-billing-flavor-check
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
Requires:       %{pythons}
Requires:       %{pythons}-lxml
Requires:       %{pythons}-requests
Requires:       cloud-regionsrv-client >= 10.2.0
BuildRequires:  %{pythons}-setuptools
%if 0%{?suse_version} >= 1600
BuildRequires:  %{pythons}-pip
BuildRequires:  %{pythons}-wheel
%endif
BuildRequires:  python-rpm-macros

%description
Check if instance is PAYG or BYOS

%prep
%setup -q

%build
%if 0%{?suse_version} >= 1600
%pyproject_wheel
%else
%{pythons} setup.py build
%endif


%install
%if 0%{?suse_version} >= 1600
%pyproject_install
%else
%{pythons} setup.py install --prefix=%{_prefix}  --root=%{buildroot}
%endif

%files
%doc README.md
%license LICENSE
%{_bindir}/instance-flavor-check
%{python_sitelib}/instance_billing_flavor_check*

%changelog
