%global pypi_name certbot-dns-joker

# build docs on Fedora but not on RHEL (not all sphinx packages available)
%if 0%{?fedora}
%bcond_without docs
%else
%bcond_with docs
%endif

Name:           python-%{pypi_name}
Version:        2.1.0
Release:        1%{?dist}
Summary:        Joker DNS Authenticator plugin for Certbot

License:        Apache-2.0
URL:            https://github.com/dhull/certbot-dns-joker
#Source0:        %{pypi_source}
Source0:        certbot-dns-joker-%{version}.tar.gz
#Source1:        %{pypi_source}.asc
# Key mentioned in https://certbot.eff.org/docs/install.html#certbot-auto
# Keyring generation steps as follows:
#   gpg2 --keyserver pool.sks-keyservers.net --recv-key A2CFB51FA275A7286234E7B24D17C995CD9775F2
#   gpg2 --export --export-options export-minimal A2CFB51FA275A7286234E7B24D17C995CD9775F2 > gpg-A2CFB51FA275A7286234E7B24D17C995CD9775F2.gpg
#Source2:        gpg-A2CFB51FA275A7286234E7B24D17C995CD9775F2.gpg

BuildArch:      noarch

BuildRequires:  python3-acme >= 2.1.0
BuildRequires:  python3-certbot >= 2.1.0
BuildRequires:  python3-devel
BuildRequires:  python3-requests
BuildRequires:  python3-setuptools >= 53.0.0

%if %{with docs}
# Required for documentation
BuildRequires:  python3-sphinx
BuildRequires:  python3-sphinx_rtd_theme
%endif

# Used to verify OpenPGP signature
#BuildRequires:  gnupg2

%description
Joker DNS Authenticator plugin for Certbot

%package -n     python3-%{pypi_name}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{pypi_name}}

# Provide the name users expect as a certbot plugin
%if 0%{?fedora}
Provides:      %{pypi_name} = %{version}-%{release}
%endif

%description -n python3-%{pypi_name}
Joker DNS Authenticator plugin for Certbot

%package -n python-%{pypi_name}-doc
Summary:        certbot-dns-joker documentation
%description -n python-%{pypi_name}-doc
Documentation for certbot-dns-joker

%prep
#%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
%autosetup -n %{pypi_name}-%{version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%build
%py3_build
%if %{with docs}
# generate html docs
sphinx-build-3 docs html
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}
%endif

%install
echo "before py3_install"
%py3_install
echo "after py3_install"
pwd && ls -l

%check
%{__python3} setup.py test

%files -n python3-%{pypi_name}
%license LICENSE.txt
%doc README.md
%doc CHANGELOG.md
%{python3_sitelib}/certbot_dns_joker
%{python3_sitelib}/certbot_dns_joker-%{version}-py%{python3_version}.egg-info

%if %{with docs}
%files -n python-%{pypi_name}-doc
%doc html
%endif

%changelog
* Tue Feb 14 2023 David Hull <github@davidhull.org> 2.1.0
- Update for certbot-2.1.0.

* Mon Oct 31 2022 David Hull <github@davidhull.org> 1.2.0
- Update packaging from python-certbot-dns-dnsimple-1.30.0-1.el9.src.rpm.
- Rebuild for el9.

* Tue Jun 23 2020 David Hull <github@davidhull.org> 1.1.0
- Allow getting certificates for subdomains.

* Sun Jun 21 2020 David Hull <github@davidhull.org> - 1.0.0
- Initial version, packaging derived from python-certbot-dns-dnsimple.
