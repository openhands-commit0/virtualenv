"""Bootstrap."""
from __future__ import annotations
import logging
import sys
from operator import eq, lt
from pathlib import Path
from subprocess import PIPE, CalledProcessError, Popen
from .bundle import from_bundle
from .periodic_update import add_wheel_to_update_log
from .util import Version, Wheel, discover_wheels

def pip_wheel_env_run(cmd, env=None):
    """Run pip wheel with the given command and environment."""
    if env is None:
        env = {}
    env = env.copy()
    env['PIP_USE_WHEEL'] = '1'
    env['PIP_USER'] = '0'
    env['PIP_NO_INPUT'] = '1'
    process = Popen(cmd, env=env, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    out, err = process.communicate()
    if process.returncode != 0:
        raise CalledProcessError(process.returncode, cmd, out, err)
    return out, err

def download_wheel(distribution, version, for_py_version, embed_filename, app_data, env, search_dirs):
    """Download a wheel from PyPI."""
    cmd = [
        sys.executable,
        '-m',
        'pip',
        'wheel',
        '--disable-pip-version-check',
        '--no-deps',
        '--no-cache-dir',
        '--python-version',
        for_py_version,
        f'{distribution}=={version}',
    ]
    for search_dir in search_dirs:
        cmd.extend(['--find-links', str(search_dir)])
    out, _ = pip_wheel_env_run(cmd, env)
    wheel_file = None
    for line in out.splitlines():
        if line.startswith('Saved '):
            wheel_file = Path(line.split(' ')[-1])
            break
    if wheel_file is None or not wheel_file.exists():
        return None
    return wheel_file

def get_wheel(distribution, version, for_py_version, search_dirs, download, app_data, do_periodic_update, env):
    """Get a wheel with the given distribution-version-for_py_version trio, by using the extra search dir + download."""
    # First try to find the wheel in the search directories
    for search_dir in search_dirs:
        wheels = discover_wheels(search_dir, distribution)
        for wheel in wheels:
            if wheel.version == version:
                return wheel.path

    # If not found and download is allowed, try to download it
    if download:
        embed_filename = f'{distribution}-{version}-py{for_py_version}-none-any.whl'
        wheel_path = download_wheel(distribution, version, for_py_version, embed_filename, app_data, env, search_dirs)
        if wheel_path is not None:
            if do_periodic_update:
                add_wheel_to_update_log(app_data.embed_update_log(distribution), Wheel(wheel_path), 'download')
            return wheel_path

    # If still not found, try to get it from the bundle
    bundle_wheel = from_bundle(distribution, version, for_py_version)
    if bundle_wheel is not None:
        return bundle_wheel

    return None

def find_compatible_in_house(distribution, version, wheels):
    """Find a compatible wheel from a list of wheels."""
    if not wheels:
        return None

    # Try to find an exact version match
    for wheel in wheels:
        if wheel.version == version:
            return wheel

    # If no exact match, try to find a compatible version
    # For now, we'll just return the latest version
    return max(wheels, key=lambda w: w.version)

__all__ = ['download_wheel', 'find_compatible_in_house', 'get_wheel', 'pip_wheel_env_run']