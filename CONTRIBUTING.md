<!-- -*- mode:gfm -*- github-flavored markdown -->

# Contributing

## Commit Messages

The commit messages use the
[AngularJS](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines)
conventions, which the `packaging/format-release-message` script formats for
the GitHub release message.

## Making a Release

To make a release, update the `__version__` variable in
`src/certbot_dns_joker/__init__.py` with the new version and commit.  Then tag
the code with the same version and run the `publish-pypi` make target to
publish to PyPI and the `publish-github` target to make a GitHub release.
