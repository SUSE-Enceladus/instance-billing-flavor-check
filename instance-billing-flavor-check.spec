#
# spec file for package instance-billing-type-check
#
# Copyright (c) 2022 SUSE LINUX GmbH, Nuernberg, Germany.
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
Summary:        Cloud Billing Flavour Check
Name:           python-instance-billing-flavor-check
Version:        0.0.1
Release:        0
License:        GPL3.0-only
Group:          Productivity/Networking/Web/Servers
URL:            https://github.com/SUSE-Enceladus/instance-billing-flavor-check
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
Requires:       python3
Requires:       python3-lxml
Requires:       python3-requests
BuildRequires:  %{python_module setuptools}
BuildRequires:  python-rpm-macros
BuildRequires:  fdupes

%python_subpackages

%description
Check if instance is PAYG or BYOS

%prep
%setup -q

%build
# Build Python 3 version
%python_build

%install
%python_install
%python_clone -a %{buildroot}%{_bindir}/instance-flavor-check
%python_expand %fdupes %{buildroot}%{$python_sitelib}

%post
%python_install_alternative instance-flavor-check

%files %{python_files}
%doc README.md
%license LICENSE
%python_alternative %{_bindir}/instance-flavor-check
%{python_sitelib}/instance_billing_flavor_check*
