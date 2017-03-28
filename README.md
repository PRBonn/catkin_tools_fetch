# A "fetch" verb for catkin_tools

[![PyPI][pypi-img]][pypi-link]
[![Build Status][travis-img]][travis-link]
[![Codacy Badge][codacy-img]][codacy-link]
[![Codacy coverage][codacy-coverage-img]][codacy-coverage-link]

Defines a new verb `fetch` for
[catkin_tools](https://github.com/catkin/catkin_tools). This verb is
responsible for downloading external dependencies of the projects in a `catkin`
workspace. For now only `git` is supported. The tool is under heavy
development. Please use PyPI or download a tag for stable version.

## How to install ##
This package installs a new verb. You need to have `catkin_tools` installed.
Currently the easiest way to install this verb is from `PyPI`:
```
[sudo] pip install catkin_tools_fetch
```

## How to use ##
Should be used from a catkin workspace as follows:
```
catkin dependencies fetch --default_url YOUR_DEFAULT_URL
```

or
```
catkin deps fetch --default_url YOUR_DEFAULT_URL
```

This command will look inside the `src/` folder of the current catkin workspace
and will analyze the dependencies of `package.xml` files for each project in
this workspace. It will then try to clone the packages looking for them under
url: `YOUR_DEFAULT_URL/PACKAGE_NAME>`.

Additionaly, one can explicitly define a url or a branch for a dependency in
`package.xml` file under `<export>` tag. For example:

```xml
<export>
    <git_url target="PACKAGE_NAME" url="PACKAGE_URL" branch="BRANCH_NAME" />
</export>
```

Here `PACKAGE_NAME` is the name of your package and `PACKAGE_URL` is the full
url to your package in git and `BRANCH_NAME` is the branch you want to
checkout.

Any of these can be skipped. The default will be used instead.

[codacy-img]: https://img.shields.io/codacy/grade/9c050cd8852046ae863c940b8409f9ea.svg?style=flat-square
[codacy-coverage-img]: https://img.shields.io/codacy/coverage/9c050cd8852046ae863c940b8409f9ea.svg?style=flat-square
[codacy-link]: https://www.codacy.com/app/zabugr/catkin_tools_fetch?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=niosus/catkin_tools_fetch&amp;utm_campaign=Badge_Grade
[codacy-coverage-link]: https://www.codacy.com/app/zabugr/catkin_tools_fetch?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=niosus/catkin_tools_fetch&amp;utm_campaign=Badge_Coverage
[travis-img]: https://img.shields.io/travis/niosus/catkin_tools_fetch/master.svg?style=flat-square
[travis-link]: https://travis-ci.org/niosus/catkin_tools_fetch

[pypi-img]: https://img.shields.io/pypi/v/catkin_tools_fetch.svg?style=flat-square
[pypi-link]: https://pypi.python.org/pypi/catkin_tools_fetch

