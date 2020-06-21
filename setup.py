from distutils.version import StrictVersion
import codecs
import os
import re
import sys

from setuptools import __version__ as setuptools_version
from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = []

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)

########################################################################

NAME = 'certbot-dns-joker'
PACKAGES = find_packages(where='src')
META_PATH = 'src/certbot_dns_joker/__init__.py'
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Plugins',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Security',
    'Topic :: System :: Installation/Setup',
    'Topic :: System :: Networking',
    'Topic :: System :: Systems Administration',
    'Topic :: Utilities',
]
# Remember to update local-oldest-requirements.txt when changing the minimum
# acme/certbot version.
INSTALL_REQUIRES = [
    'acme>=0.31.0',
    'certbot>=1.1.0',
    'requests',
    'setuptools',
    'zope.interface',
]
TESTS_REQUIRE = [
    'requests-mock',
    'pytest',
]
setuptools_known_environment_markers = (StrictVersion(setuptools_version) >= StrictVersion('36.2'))
if setuptools_known_environment_markers:
    TESTS_REQUIRE.append('mock ; python_version < "3.3"')
elif 'bdist_wheel' in sys.argv[1:]:
    raise RuntimeError('Error, you are trying to build certbot wheels using an old version '
                       'of setuptools. Version 36.2+ of setuptools is required.')
elif sys.version_info < (3,3):
    TESTS_REQUIRE.append('mock')

DOCS_EXTRAS = [
    'Sphinx>=1.0',  # autodoc_member_order = 'bysource', autodoc_default_flags
    'sphinx_rtd_theme',
]

########################################################################

HERE = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()

META_FILE = read(META_PATH)

def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))

setup(
    name=NAME,
    version=find_meta('version'),
    description=find_meta('description'),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url=find_meta('url'),
    project_urls={
        'Issue Tracker': find_meta('issue_tracker'),
    },
    author=find_meta('author'),
    author_email=find_meta('email'),
    license=find_meta('license'),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    classifiers=CLASSIFIERS,
    packages=PACKAGES,
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_require={
        'docs': DOCS_EXTRAS,
    },
    entry_points={
        'certbot.plugins': [
            'dns-joker = certbot_dns_joker.dns_joker:Authenticator',
        ],
    },
    tests_require=TESTS_REQUIRE,
    test_suite='certbot_dns_joker',
    cmdclass={"test": PyTest},
)
