%global pypi_name certbot-dns-joker

%if 0%{?rhel} && 0%{?rhel} <= 7
%bcond_with python3
%else
%bcond_without python3
%endif

%if 0%{?fedora} || (0%{?rhel} && 0%{?rhel} >= 8)
%bcond_with python2
%else
%bcond_without python2
%endif

Name:           python-%{pypi_name}
Version:        1.0.0.dev0
Release:        1%{?dist}
Summary:        Joker DNS Authenticator plugin for Certbot

License:        ASL 2.0
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

%if %{with python2}
BuildRequires:  python2-acme >= 0.31.0
BuildRequires:  python2-certbot >= 1.1.0
BuildRequires:  python2-devel
BuildRequires:  python2-requests
BuildRequires:  python2-setuptools
BuildRequires:  python2-zope-interface

%if 0%{?rhel} && 0%{?rhel} <= 7
# EL7 has unversioned names for these packages
BuildRequires:  pytest
%else
BuildRequires:  python2-pytest
%endif
%endif

%if %{with python3}
BuildRequires:  python3-acme >= 0.31.0
BuildRequires:  python3-certbot >= 1.1.0
BuildRequires:  python3-devel
BuildRequires:  python3-requests
BuildRequires:  python3-setuptools
BuildRequires:  python3-zope-interface

# Required for testing
# Since these are listed in setup.py they end up being required at runtime by certbot.
#BuildRequires:  python3-pytest
#BuildRequires:  python3-mock
#BuildRequires:  python3-requests-mock

# Required for documentation
BuildRequires:  python3-sphinx
BuildRequires:  python3-sphinx_rtd_theme
%endif

# Used to verify OpenPGP signature
#BuildRequires:  gnupg2

%description
Joker DNS Authenticator plugin for Certbot

%if %{with python2}
%package -n     python2-%{pypi_name}
Summary:        %{summary}
%{?python_provide:%python_provide python2-%{pypi_name}}

Requires:       python2-acme >= 0.31.0
Requires:       python2-certbot >= 1.1.0
Requires:       python2-requests
Requires:       python2-mock
#Requires:       python2-requests-mock
Requires:       python2-setuptools
Requires:       python2-zope-interface

# Provide the name users expect as a certbot plugin
%if 0%{?rhel} && 0%{?rhel} <= 7
Provides:      %{pypi_name} = %{version}-%{release}
%endif

%description -n python2-%{pypi_name}
Joker DNS Authenticator plugin for Certbot
%endif

%if %{with python3}
%package -n     python3-%{pypi_name}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{pypi_name}}

Requires:       python3-acme >= 0.31.0
Requires:       python3-certbot >= 1.1.0
Requires:       python3-requests
Requires:       python3-setuptools
Requires:       python3-zope-interface

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
%endif

%prep
#%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
%autosetup -n %{pypi_name}-%{version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%build
%if %{with python2}
%py2_build
%endif

%if %{with python3}
%py3_build
# generate html docs
sphinx-build-3 docs html
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}
%endif

%install
%if %{with python2}
%py2_install
%endif

%if %{with python3}
%py3_install
%endif


%check
%if %{with python2}
%{__python2} setup.py test
%endif

%if %{with python3}
%{__python3} setup.py test
%endif

%if %{with python2}
%files -n python2-%{pypi_name}
%license LICENSE.txt
%doc README.md
%{python2_sitelib}/certbot_dns_joker
%{python2_sitelib}/certbot_dns_joker-%{version}-py?.?.egg-info
%endif

%if %{with python3}
%files -n python3-%{pypi_name}
%license LICENSE.txt
%doc README.md
%doc CHANGELOG.md
%{python3_sitelib}/certbot_dns_joker
%{python3_sitelib}/certbot_dns_joker-%{version}-py?.?.egg-info

%files -n python-%{pypi_name}-doc
%doc html
%endif

%changelog
* Tue Jun 23 2020 David Hull <github@davidhull.org> 1.1.0
- Allow getting certificates for subdomains.

* Sun Jun 21 2020 David Hull <github@davidhull.org> - 1.0.0
- Initial version, packaging derived from python-certbot-dns-dnsimple.
