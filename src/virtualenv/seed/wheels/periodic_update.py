"""Periodically update bundled versions."""
from __future__ import annotations
import json
import logging
import os
import ssl
import sys
from datetime import datetime, timedelta, timezone
from itertools import groupby
from pathlib import Path
from shutil import copy2
from subprocess import DEVNULL, Popen
from textwrap import dedent
from threading import Thread
from urllib.error import URLError
from urllib.request import urlopen
from virtualenv.app_data import AppDataDiskFolder
from virtualenv.seed.wheels.embed import BUNDLE_SUPPORT
from virtualenv.seed.wheels.util import Wheel
from virtualenv.util.subprocess import CREATE_NO_WINDOW
GRACE_PERIOD_CI = timedelta(hours=1)
GRACE_PERIOD_MINOR = timedelta(days=28)
UPDATE_PERIOD = timedelta(days=14)
UPDATE_ABORTED_DELAY = timedelta(hours=1)
DATETIME_FMT = '%Y-%m-%dT%H:%M:%S.%fZ'

class NewVersion:

    def __init__(self, filename, found_date, release_date, source) -> None:
        self.filename = filename
        self.found_date = found_date
        self.release_date = release_date
        self.source = source

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(filename={self.filename}), found_date={self.found_date}, release_date={self.release_date}, source={self.source})'

    def __eq__(self, other):
        return type(self) == type(other) and all((getattr(self, k) == getattr(other, k) for k in ['filename', 'release_date', 'found_date', 'source']))

    def __ne__(self, other):
        return not self == other

class UpdateLog:

    def __init__(self, started, completed, versions, periodic) -> None:
        self.started = started
        self.completed = completed
        self.versions = versions
        self.periodic = periodic
_PYPI_CACHE = {}

def dump_datetime(dt):
    """Convert datetime to string."""
    return None if dt is None else dt.strftime(DATETIME_FMT)

def load_datetime(raw):
    """Convert string to datetime."""
    return None if raw is None else datetime.strptime(raw, DATETIME_FMT).replace(tzinfo=timezone.utc)

def release_date_for_wheel_path(path):
    """Get the release date for a wheel from PyPI."""
    wheel = Wheel.from_path(path)
    if wheel.name not in _PYPI_CACHE:
        url = f'https://pypi.org/pypi/{wheel.name}/json'
        try:
            with urlopen(url, timeout=10, context=ssl._create_unverified_context()) as file_handler:
                _PYPI_CACHE[wheel.name] = json.load(file_handler)
        except (URLError, json.JSONDecodeError):
            return None
    data = _PYPI_CACHE[wheel.name]
    if wheel.version in data.get('releases', {}):
        for release in data['releases'][wheel.version]:
            if release['filename'] == wheel.filename:
                return datetime.strptime(release['upload_time'], '%Y-%m-%dT%H:%M:%S')
    return None

def add_wheel_to_update_log(versions, wheel, source):
    """Add a wheel to the update log."""
    release_date = release_date_for_wheel_path(wheel)
    if release_date is not None:
        found_date = datetime.now(tz=timezone.utc)
        versions.append(NewVersion(wheel.name, found_date, release_date, source))

def trigger_update(distribution, for_py_version):
    """Trigger an update of the bundled wheels."""
    env = os.environ.copy()
    env['VIRTUALENV_OVERRIDE_APP_DATA'] = str(AppDataDiskFolder().path)
    env['VIRTUALENV_PERIODIC_UPDATE_VERSIONS'] = ','.join(for_py_version)
    cmd = [sys.executable, '-m', 'virtualenv', '--upgrade-embed-wheels']
    process = Popen(cmd, env=env, stdout=DEVNULL, stderr=DEVNULL, creationflags=CREATE_NO_WINDOW)
    process.communicate()

def do_update(distribution, for_py_version):
    """Perform the update of bundled wheels."""
    pass

def manual_upgrade(distribution, for_py_version):
    """Manually trigger an upgrade of the bundled wheels."""
    trigger_update(distribution, for_py_version)

def periodic_update(distribution, for_py_version):
    """Periodically update the bundled wheels."""
    app_data = AppDataDiskFolder()
    embed_update_log = app_data.embed_update_log(distribution)
    if not embed_update_log.exists():
        trigger_update(distribution, for_py_version)
        return
    with embed_update_log.open() as file_handler:
        try:
            data = json.load(file_handler)
        except json.JSONDecodeError:
            data = {}
    completed = load_datetime(data.get('completed'))
    if completed is None:
        started = load_datetime(data.get('started'))
        if started is None or datetime.now(tz=timezone.utc) - started > UPDATE_ABORTED_DELAY:
            trigger_update(distribution, for_py_version)
        return
    if datetime.now(tz=timezone.utc) - completed > UPDATE_PERIOD:
        trigger_update(distribution, for_py_version)

__all__ = ['NewVersion', 'UpdateLog', 'add_wheel_to_update_log', 'do_update', 'dump_datetime', 'load_datetime', 'manual_upgrade', 'periodic_update', 'release_date_for_wheel_path', 'trigger_update']