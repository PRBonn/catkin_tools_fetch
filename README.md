# "fetch" and "update" your dependencies with catkin_tools

[![PyPI][pypi-img]][pypi-link]
[![Build Status][travis-img]][travis-link]
[![Codacy Badge][codacy-img]][codacy-link]
[![Codacy coverage][codacy-coverage-img]][codacy-coverage-link]

Defines new verb `dependencies` (or in short `deps`)
and its sub-verbs `fetch` and `update` for
[catkin_tools](https://github.com/catkin/catkin_tools).
This verb is responsible for downloading external dependencies
of the projects in a `catkin` workspace and keeping them up to date.
For now only `git` is supported. The tool is under heavy development.
Please use PyPI or download a tag for a stable version.

## How to install ##
This package installs a new verb for `catkin_tools`.
The easiest way to install this verb is from `PyPI`:
```
[sudo] pip install catkin_tools_fetch
```

## How to use ##
Both available subverbs should be used after `dependencies` verb (or its
shorter version `deps`) from within of a catkin workspace. Below are short
showcases on usage of the verbs. Optional arguments are shown in brackets.
### `fetch` ###
```bash
# Longer version:
catkin dependencies fetch [--default_urls URL1,URL2,URL3] [TARGET_PKG]
# Equivalent shorter version:
catkin deps fetch [--default_urls URL1,URL2,URL3] [TARGET_PKG]
```

### `update` ###
```bash
# Longer version:
catkin dependencies update [TARGET_PKG]
# Equivalent shorter version:
catkin deps update [TARGET_PKG]
```

## How `fetch` works ##
This command will look inside the `src/` folder of the current catkin workspace
and will analyze the dependencies of each `package.xml` file for each project
in this workspace (or, if `TARGET_PKG` is provided, only of this package). Then
`fetch` will try to clone the dependencies looking for them under urls:
```
[URL1/DEP_NAME, URL1/DEP_NAME, URL1/DEP_NAME]
```

The verb `fetch` is smart enough to recognize `ssh` and `https` access, thus
these expansions for a given `DEP_NAME` are valid:
```
git@path     --> git@path/DEP_NAME.git
https://path --> https://path/DEP_NAME.git
```
Beware, though, that for ssh access your machine has to have proper ssh keys
installed.

Additionaly, one can explicitly define needed urls for dependencies in
`package.xml` of your `TARGET_PKG` file under `<export>` tag. For example:
```xml
<export>
    <!-- Define a url for all packages with no explicit url defined. -->
    <git_url target="all" url="SOME_GENERAL_URL" />
    <!-- Define an explicit url for package DEP_NAME. -->
    <git_url target="DEP_NAME" url="git@some_path/DEP_NAME.git" branch="BRANCH_NAME" />
</export>
```

There are some options here:
- If the `target` is set to `"all"`, then `SOME_GENERAL_URL` is treated as one
  of the default urls to search all packages in.
- If the `target` package `"DEP_NAME"` matches one of the dependencies,
  this has precedence over any of the default urls and the package will be
  searched in the full path to the package defined in the `url` field.
  Additionaly, branch `"BRANCH_NAME"` will be checked out after cloning.

Any of these can be skipped. The default urls will be used instead.

## How `update` works ##
The `update` subverb will try to pull any changes from the server to any
package in the workspace (or `TARGET_PKG` if specified) if there is no change
locally. If there are local uncommited changes `update` will do nothing for
those packages. There is no need to provide any urls here as every package
knows its git remote.

## Misc ##
You can always use `--help` flag to find out more about each command and arguments.

[codacy-img]: https://img.shields.io/codacy/grade/9c050cd8852046ae863c940b8409f9ea.svg?style=flat-square
[codacy-coverage-img]: https://img.shields.io/codacy/coverage/9c050cd8852046ae863c940b8409f9ea.svg?style=flat-square
[codacy-link]: https://www.codacy.com/app/zabugr/catkin_tools_fetch?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=niosus/catkin_tools_fetch&amp;utm_campaign=Badge_Grade
[codacy-coverage-link]: https://www.codacy.com/app/zabugr/catkin_tools_fetch?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=niosus/catkin_tools_fetch&amp;utm_campaign=Badge_Coverage
[travis-img]: https://img.shields.io/travis/Photogrammetry-Robotics-Bonn/catkin_tools_fetch/master.svg?style=flat-square
[travis-link]: https://travis-ci.org/Photogrammetry-Robotics-Bonn/catkin_tools_fetch

[pypi-img]: https://img.shields.io/pypi/v/catkin_tools_fetch.svg?style=flat-square
[pypi-link]: https://pypi.python.org/pypi/catkin_tools_fetch

