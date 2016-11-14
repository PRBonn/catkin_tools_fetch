# A "fetch" verb for catkin_tools

[![Build Status](https://travis-ci.org/niosus/catkin_tools_fetch.svg?branch=master)](https://travis-ci.org/niosus/catkin_tools_fetch)

Defines a new verb `fetch` for
[catkin_tools](https://github.com/catkin/catkin_tools). This verb is
responsible to download external dependencies of the projects in a `catkin`
workspace. For now only git is supported. The tool is under heavy development.

## How to install ##
This package installs a new verb. You need to have `catkin_tools` installed.
Currently the easiest way to install this verb is:

```
pip install -U https://github.com/niosus/catkin_tools_fetch/archive/master.zip
```
if this complaints, run a command with `sudo`:

```
sudo pip install https://github.com/niosus/catkin_tools_fetch/archive/master.zip
```

## How to use ##
Should be used from a catkin workspace as follows:

```
catkin fetch --default_url YOUR_DEFAULT_URL
```

This command will look inside the `src/` folder of the current catkin workspace
and will analyze the dependencies of `package.xml` files for each project in
this workspace. It will then try to clone the packages looking for them under
url: `YOUR_DEFAULT_URL/PACKAGE_NAME>`.

Additionaly, one can explicitly define a url for a dependency in `package.xml`
file under `<export>` tag. For example:

```xml
<export>
    <git_url target="PACKAGE_NAME" url="PACKAGE_URL" />
</export>
```
