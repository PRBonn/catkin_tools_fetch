"""Module that contains flake8 tests."""
import os
import subprocess


def test_flake8():
    """Test source code for pyFlakes and PEP8 conformance."""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(this_dir, '..', 'catkin_tools_fetch')
    cmd = ['flake8', source_dir, '--count', '--max-line-length=120']
    # work around for https://gitlab.com/pycqa/flake8/issues/179
    cmd.extend(['--jobs', '1'])
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, _ = p.communicate()
    print(stdout)
    assert p.returncode == 0, \
        "Command '{0}' returned non-zero exit code '{1}'".format(
            ' '.join(cmd), p.returncode)
