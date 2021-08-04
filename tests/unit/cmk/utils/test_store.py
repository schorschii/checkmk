#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
import ast
import enum
import pickle
import threading
import queue
import os
import stat
from multiprocessing.pool import ThreadPool
from typing import List

import errno
from pathlib import Path

from six import ensure_binary
import pytest
from tests.testlib import import_module, wait_until

import cmk.utils.store as store
from cmk.utils.exceptions import MKGeneralException


@pytest.mark.parametrize("path_type", [str, Path])
def test_mkdir(tmp_path, path_type):
    test_dir = tmp_path / "abc"
    store.mkdir(path_type(test_dir))
    store.mkdir(path_type(test_dir))


@pytest.mark.parametrize("path_type", [str, Path])
def test_mkdir_mode(tmp_path, path_type):
    test_dir = tmp_path / "bla"
    store.mkdir(path_type(test_dir), mode=0o750)
    assert stat.S_IMODE(os.stat(str(test_dir)).st_mode) == 0o750


@pytest.mark.parametrize("path_type", [str, Path])
def test_mkdir_parent_not_exists(tmp_path, path_type):
    test_dir = tmp_path / "not-existing/xyz"
    with pytest.raises(OSError, match="No such file or directory"):
        store.mkdir(path_type(test_dir))


@pytest.mark.parametrize("path_type", [str, Path])
def test_makedirs(tmp_path, path_type):
    test_dir = tmp_path / "not-existing/xyz"
    store.makedirs(path_type(test_dir))
    store.makedirs(path_type(test_dir))


@pytest.mark.parametrize("path_type", [str, Path])
def test_makedirs_mode(tmp_path, path_type):
    test_dir = tmp_path / "whee/blub"
    store.makedirs(path_type(test_dir), mode=0o750)
    assert stat.S_IMODE(os.stat(str(test_dir)).st_mode) == 0o750


@pytest.mark.parametrize("path_type", [str, Path])
def test_load_data_from_file_not_existing(tmp_path, path_type):
    data = store.load_object_from_file(path_type(tmp_path / "x"), default=None)
    assert data is None

    data = store.load_object_from_file(path_type(tmp_path / "x"), default="DEFAULT")
    assert data == "DEFAULT"


@pytest.mark.parametrize("path_type", [str, Path])
def test_load_data_from_file_empty(tmp_path, path_type):
    locked_file = tmp_path / "test"
    locked_file.write_text(u"", encoding="utf-8")
    data = store.load_object_from_file(path_type(tmp_path / "x"), default="DEF")
    assert data == "DEF"


@pytest.mark.parametrize("path_type", [str, Path])
def test_load_data_not_locked(tmp_path, path_type):
    locked_file = tmp_path / "locked_file"
    locked_file.write_text(u"[1, 2]", encoding="utf-8")

    store.load_object_from_file(path_type(locked_file), default=None)
    assert store.have_lock(path_type(locked_file)) is False


@pytest.mark.parametrize("path_type", [str, Path])
def test_load_data_from_file_locking(tmp_path, path_type):
    locked_file = tmp_path / "locked_file"
    locked_file.write_text(u"[1, 2]", encoding="utf-8")

    data = store.load_object_from_file(path_type(locked_file), default=None, lock=True)
    assert data == [1, 2]
    assert store.have_lock(path_type(locked_file)) is True


@pytest.mark.parametrize("path_type", [str, Path])
def test_load_data_from_not_permitted_file(tmp_path, path_type):
    locked_file = tmp_path / "test"
    locked_file.write_text(u"[1, 2]", encoding="utf-8")
    os.chmod(str(locked_file), 0o200)

    with pytest.raises(MKGeneralException) as e:
        store.load_object_from_file(path_type(locked_file), default=None)
    assert str(locked_file) in "%s" % e
    assert "Permission denied" in "%s" % e


@pytest.mark.parametrize("path_type", [str, Path])
def test_load_data_from_file_dict(tmp_path, path_type):
    locked_file = tmp_path / "test"
    locked_file.write_bytes(ensure_binary(repr({"1": 2, "ä": u"ß"})))

    data = store.load_object_from_file(path_type(locked_file), default=None)
    assert isinstance(data, dict)
    assert data["1"] == 2
    assert isinstance(data["ä"], str)
    assert data["ä"] == u"ß"


@pytest.mark.parametrize("path_type", [str, Path])
def test_load_mk_file(tmp_path, path_type):
    locked_file = tmp_path / "test"
    locked_file.write_bytes(b"# encoding: utf-8\nabc = '\xc3\xa4bc'\n")

    config = store.load_mk_file(path_type(locked_file), default={})
    assert config["abc"] == "äbc"


@pytest.mark.parametrize("path_type", [str, Path])
def test_save_data_to_file_pretty(tmp_path, path_type):
    path = path_type(tmp_path / "test")

    data = {
        "asdasaaaaaaaaaaaaaaaaaaaad": "asbbbbbbbbbbbbbbbbbbd",
        "1asdasaaaaaaaaaaaaaaaaaaaad": "asbbbbbbbbbbbbbbbbbbd",
        "2asdasaaaaaaaaaaaaaaaaaaaad": "asbbbbbbbbbbbbbbbbbbd",
        "3asdasaaaaaaaaaaaaaaaaaaaad": "asbbbbbbbbbbbbbbbbbbd",
        "4asdasaaaaaaaaaaaaaaaaaaaad": "asbbbbbbbbbbbbbbbbbbd",
        "5asdasaaaaaaaaaaaaaaaaaaaad": "asbbbbbbbbbbbbbbbbbbd",
    }
    store.save_object_to_file(path, data, pretty=True)
    assert open(str(path)).read().count("\n") > 4
    assert store.load_object_from_file(path, default=None) == data


@pytest.mark.parametrize("path_type", [str, Path])
def test_save_data_to_file_not_pretty(tmp_path, path_type):
    path = path_type(tmp_path / "test")

    data = {
        "asdasaaaaaaaaaaaaaaaaaaaad": "asbbbbbbbbbbbbbbbbbbd",
        "1asdasaaaaaaaaaaaaaaaaaaaad": "asbbbbbbbbbbbbbbbbbbd",
        "2asdasaaaaaaaaaaaaaaaaaaaad": "asbbbbbbbbbbbbbbbbbbd",
        "3asdasaaaaaaaaaaaaaaaaaaaad": "asbbbbbbbbbbbbbbbbbbd",
        "4asdasaaaaaaaaaaaaaaaaaaaad": "asbbbbbbbbbbbbbbbbbbd",
        "5asdasaaaaaaaaaaaaaaaaaaaad": "asbbbbbbbbbbbbbbbbbbd",
    }
    store.save_object_to_file(path, data)
    assert open(str(path)).read().count("\n") == 1
    assert store.load_object_from_file(path, default=None) == data


@pytest.mark.parametrize("path_type", [str, Path])
@pytest.mark.parametrize("data", [
    None,
    [2, 3],
    [u"föö"],
    [b'foob\xc3\xa4r'],
])
def test_save_data_to_file(tmp_path, path_type, data):
    path = path_type(tmp_path / "lala")
    store.save_object_to_file(path, data)
    assert store.load_object_from_file(path, default=None) == data


@pytest.mark.parametrize("path_type", [str, Path])
@pytest.mark.parametrize("data", [
    u"föö",
])
def test_save_text_to_file(tmp_path, path_type, data):
    path = path_type(tmp_path / "lala")
    store.save_text_to_file(path, data)
    assert store.load_text_from_file(path) == data


@pytest.mark.parametrize("path_type", [str, Path])
@pytest.mark.parametrize("data", [
    None,
    b'foob\xc3\xa4r',
])
def test_save_text_to_file_bytes(tmp_path, path_type, data):
    path = path_type(tmp_path / "lala")
    with pytest.raises(TypeError) as e:
        store.save_text_to_file(path, data)
    assert "content argument must be Text, not bytes" in "%s" % e


@pytest.mark.parametrize("path_type", [str, Path])
@pytest.mark.parametrize("data", [
    b'foob\xc3\xa4r',
])
def test_save_bytes_to_file(tmp_path, path_type, data):
    path = path_type(tmp_path / "lala")
    store.save_bytes_to_file(path, data)
    assert store.load_bytes_from_file(path) == data


@pytest.mark.parametrize("path_type", [str, Path])
@pytest.mark.parametrize("data", [
    None,
    u"föö",
])
def test_save_bytes_to_file_unicode(tmp_path, path_type, data):
    path = path_type(tmp_path / "lala")
    with pytest.raises(TypeError) as e:
        store.save_bytes_to_file(path, data)
    assert "content argument must be bytes, not Text" in "%s" % e


@pytest.mark.parametrize("path_type", [str, Path])
def test_save_mk_file(tmp_path, path_type):
    path = path_type(tmp_path / "lala")
    store.save_mk_file(path, "x = 1")
    assert store.load_mk_file(path, default={}) == {"x": 1}


@pytest.mark.parametrize("path_type", [str, Path])
def test_save_to_mk_file(tmp_path, path_type):
    path = path_type(tmp_path / "huhu")
    store.save_to_mk_file(path, "x", {"a": 1})
    assert store.load_mk_file(path, default={"x": {"a": 2, "y": 1}}) == {"x": {"a": 1, "y": 1}}


@pytest.mark.parametrize("path_type", [str, Path])
def test_aquire_lock_not_existing(tmp_path, path_type):
    store.aquire_lock(path_type(tmp_path / "asd"))


@pytest.mark.parametrize("path_type", [str, Path])
def test_locked(locked_file, path_type):
    path = path_type(locked_file)

    assert store.have_lock(path) is False

    with store.locked(path):
        assert store.have_lock(path) is True

    assert store.have_lock(path) is False


@pytest.fixture(name="locked_file")
def fixture_locked_file(tmp_path):
    locked_file = tmp_path / "locked_file"
    locked_file.write_text(u"", encoding="utf-8")
    return locked_file


@pytest.mark.parametrize("path_type", [str, Path])
def test_try_locked(locked_file, path_type):
    path = path_type(locked_file)

    assert store.have_lock(path) is False

    with store.try_locked(path) as result:
        assert result is True
        assert store.have_lock(path) is True

    assert store.have_lock(path) is False


@pytest.mark.parametrize("path_type", [str, Path])
def test_try_locked_fails(locked_file, path_type, monkeypatch):
    path = path_type(locked_file)

    def _is_already_locked(path, blocking):
        raise IOError(errno.EAGAIN, "%s is already locked" % path)

    monkeypatch.setattr(store._locks, "aquire_lock", _is_already_locked)

    assert store.have_lock(path) is False

    with store.try_locked(path) as result:
        assert result is False
        assert store.have_lock(path) is False

    assert store.have_lock(path) is False


@pytest.mark.parametrize("path_type", [str, Path])
def test_aquire_lock(locked_file, path_type):
    path = path_type(locked_file)

    assert store.have_lock(path) is False
    store.aquire_lock(path)
    assert store.have_lock(path) is True


@pytest.mark.parametrize("path_type", [str, Path])
def test_aquire_lock_twice(locked_file, path_type):
    path = path_type(locked_file)

    assert store.have_lock(path) is False
    store.aquire_lock(path)
    assert store.have_lock(path) is True
    store.aquire_lock(path)
    assert store.have_lock(path) is True


@pytest.mark.parametrize("path_type", [str, Path])
def test_release_lock_not_locked(path_type):
    store.release_lock(path_type("/asdasd/aasdasd"))


@pytest.mark.parametrize("path_type", [str, Path])
def test_release_lock(locked_file, path_type):
    path = path_type(locked_file)

    assert store.have_lock(path) is False
    store.aquire_lock(path)
    assert store.have_lock(path) is True
    store.release_lock(path)
    assert store.have_lock(path) is False


@pytest.mark.parametrize("path_type", [str, Path])
def test_release_lock_already_closed(locked_file, path_type):
    path = path_type(locked_file)

    assert store.have_lock(path) is False
    store.aquire_lock(path)
    assert store.have_lock(path) is True

    os.close(store._locks._get_lock(str(path)))

    store.release_lock(path)
    assert store.have_lock(path) is False


@pytest.mark.parametrize("path_type", [str, Path])
def test_release_all_locks(tmp_path, path_type):
    locked_file1 = tmp_path / "locked_file1"
    locked_file1.write_text(u"", encoding="utf-8")
    locked_file2 = tmp_path / "locked_file2"
    locked_file2.write_text(u"", encoding="utf-8")

    path1 = path_type(locked_file1)
    path2 = path_type(locked_file2)

    assert store.have_lock(path1) is False
    store.aquire_lock(path1)
    assert store.have_lock(path1) is True

    assert store.have_lock(path2) is False
    store.aquire_lock(path2)
    assert store.have_lock(path2) is True

    store.release_all_locks()
    assert store.have_lock(path1) is False
    assert store.have_lock(path2) is False


@pytest.mark.parametrize("path_type", [str, Path])
def test_release_all_locks_already_closed(locked_file, path_type):
    path = path_type(locked_file)

    assert store.have_lock(path) is False
    store.aquire_lock(path)
    assert store.have_lock(path) is True

    os.close(store._locks._get_lock(str(path)))

    store.release_all_locks()
    assert store.have_lock(path) is False


class LockTestJob(enum.Enum):
    TERMINATE = enum.auto()
    LOCK = enum.auto()
    UNLOCK = enum.auto()


class LockTestThread(threading.Thread):
    def __init__(self, store_mod, path):
        super(LockTestThread, self).__init__()
        self.daemon = True

        self.store = store_mod
        self.path = path

        self._jobs: queue.Queue[LockTestJob] = queue.Queue()

    def run(self):
        while True:
            try:
                job = self._jobs.get(block=True, timeout=0.1)
            except queue.Empty:
                continue

            try:
                if job is LockTestJob.TERMINATE:
                    break

                if job is LockTestJob.LOCK:
                    assert self.store.have_lock(self.path) is False
                    self.store.aquire_lock(self.path)
                    assert self.store.have_lock(self.path) is True
                    continue

                if job is LockTestJob.UNLOCK:
                    assert self.store.have_lock(self.path) is True
                    self.store.release_lock(self.path)
                    assert self.store.have_lock(self.path) is False
                    continue
            finally:
                self._jobs.task_done()

    def terminate(self):
        """Send terminate command to thread from outside and wait for completion"""
        self._jobs.put(LockTestJob.TERMINATE)
        self.join()

    def lock(self):
        """Send lock command to thread from outside and wait for completion"""
        self.lock_nowait()
        self._jobs.join()

    def unlock(self):
        """Send unlock command to thread from outside and wait for completion"""
        self._jobs.put(LockTestJob.UNLOCK)
        self._jobs.join()

    def lock_nowait(self):
        """Send lock command to thread from outside without waiting for completion"""
        self._jobs.put(LockTestJob.LOCK)

    def join_jobs(self):
        self._jobs.join()


@pytest.fixture(name="t1")
def fixture_test_thread_1(locked_file):
    # HACK: We abuse modules as data containers, so we have to do this Kung Fu...
    t_store = import_module("cmk/utils/store/__init__.py")

    t = LockTestThread(t_store, locked_file)
    t.start()

    yield t

    t.store.release_all_locks()
    t.terminate()


@pytest.fixture(name="t2")
def fixture_test_thread_2(locked_file):
    # HACK: We abuse modules as data containers, so we have to do this Kung Fu...
    t_store = store

    t = LockTestThread(t_store, locked_file)
    t.start()

    yield t

    t.store.release_all_locks()
    t.terminate()


def _wait_for_waiting_lock():
    """Use /proc/locks to wait until one lock is in waiting state

    https://man7.org/linux/man-pages/man5/proc.5.html
    """
    def has_waiting_lock():
        pid = os.getpid()
        with Path("/proc/locks").open() as f:
            for line in f:
                p = line.strip().split()
                if p[1] == "->" and p[2] == "FLOCK" and p[4] == "WRITE" and p[5] == str(pid):
                    return True
        return False

    wait_until(has_waiting_lock, timeout=1, interval=0.01)


@pytest.mark.parametrize("path_type", [str, Path])
def test_blocking_context_manager_from_multiple_threads(locked_file, path_type):
    path = path_type(locked_file)

    acquired = []

    def acquire(n):
        with store.locked(path):
            acquired.append(1)
            assert len(acquired) == 1
            acquired.pop()

    pool = ThreadPool(20)
    pool.map(acquire, range(100))
    pool.close()
    pool.join()


@pytest.mark.parametrize("path_type", [str, Path])
def test_blocking_lock_from_multiple_threads(locked_file, path_type):
    path = path_type(locked_file)

    debug = False
    acquired = []
    saw_someone_wait: List[int] = []

    def acquire(n):
        assert not store.have_lock(path)
        if debug:
            print(f"{n}: Trying lock\n")
        store.aquire_lock(path, blocking=True)
        assert store.have_lock(path)

        # We check to see if the other threads are actually waiting.
        if not saw_someone_wait:
            _wait_for_waiting_lock()
            saw_someone_wait.append(1)

        if debug:
            print(f"{n}: Got lock\n")

        acquired.append(1)
        # This part is guarded by the lock, so we should never have more than one entry in here,
        # even if multiple threads try to append at the same time
        assert len(acquired) == 1

        acquired.pop()
        store.release_lock(path)
        assert not store.have_lock(path)
        if debug:
            print(f"{n}: Released lock\n")

    # We try to append 100 ints to `acquired` in 20 threads simultaneously. As it is guarded by
    # the lock, we only ever can have one entry in the list at the same time.
    pool = ThreadPool(20)
    pool.map(acquire, range(100))
    pool.close()
    pool.join()

    # After all the threads have finished, the list should be empty again.
    assert len(acquired) == 0


@pytest.mark.parametrize("path_type", [str, Path])
def test_non_blocking_lock_from_multiple_threads(locked_file, path_type):
    path = path_type(locked_file)

    acquired = []

    # Only one thread will ever be able to acquire this lock.
    def acquire(_):
        try:
            store.aquire_lock(path, blocking=False)
            acquired.append(1)
            assert store.have_lock(path)
            store.release_lock(path)
            assert not store.have_lock(path)
        except IOError:
            assert not store.have_lock(path)

    pool = ThreadPool(2)
    pool.map(acquire, range(20))
    pool.close()
    pool.join()

    assert len(acquired) > 1, "No thread got any lock."


@pytest.mark.parametrize("path_type", [str, Path])
def test_blocking_lock_while_other_holds_the_lock(locked_file, path_type, t1, t2, monkeypatch):
    assert t1.store != t2.store

    path = path_type(locked_file)

    assert t1.store.have_lock(path) is False
    assert t2.store.have_lock(path) is False

    try:
        # Take lock with t1
        t1.lock()

        # Now request the lock in t2, but don't wait for the successful locking. Only wait until we
        # start waiting for the lock.
        t2.lock_nowait()
        _wait_for_waiting_lock()
    finally:
        t1.unlock()

    t2.join_jobs()


@pytest.mark.parametrize("path_type", [str, Path])
def test_non_blocking_locking_without_previous_lock(locked_file, path_type, t1):
    assert t1.store != store
    path = path_type(locked_file)

    # Try to lock first
    assert store.try_aquire_lock(path) is True
    assert store.have_lock(path) is True
    store.release_lock(path)
    assert store.have_lock(path) is False


@pytest.mark.parametrize("path_type", [str, Path])
def test_non_blocking_locking_while_already_locked(locked_file, path_type, t1):
    assert t1.store != store
    path = path_type(locked_file)

    # Now take lock with t1.store
    t1.lock()

    # And now try to get the lock (which should not be possible)
    assert store.try_aquire_lock(path) is False
    assert store.have_lock(path) is False


@pytest.mark.parametrize("path_type", [str, Path])
def test_non_blocking_decorated_locking_without_previous_lock(locked_file, path_type, t1):
    assert t1.store != store
    path = path_type(locked_file)

    with store.try_locked(path) as result:
        assert result is True
        assert store.have_lock(path) is True
    assert store.have_lock(path) is False


@pytest.mark.parametrize("path_type", [str, Path])
def test_non_blocking_decorated_locking_while_already_locked(locked_file, path_type, t1):
    assert t1.store != store
    path = path_type(locked_file)

    # Take lock with t1.store
    t1.lock()

    # And now try to get the lock (which should not be possible)
    with store.try_locked(path) as result:
        assert result is False
        assert store.have_lock(path) is False
    assert store.have_lock(path) is False


@pytest.mark.parametrize("text, storage_format", [
    ("standard", store.StorageFormat.STANDARD),
    ("raw", store.StorageFormat.RAW),
])
def test_storage_format(text, storage_format):
    assert store.StorageFormat(text) == storage_format
    assert str(storage_format) == text
    assert store.StorageFormat.from_str(text) == storage_format


@pytest.mark.parametrize("storage_format, expected_extension", [
    (store.StorageFormat.STANDARD, ".mk"),
    (store.StorageFormat.RAW, ".cfg"),
])
def test_storage_format_extension(storage_format, expected_extension):
    assert storage_format.extension() == expected_extension


def test_storage_format_other():
    assert store.StorageFormat("standard") != store.StorageFormat.RAW
    with pytest.raises(KeyError):
        store.StorageFormat.from_str("bad")


@pytest.mark.parametrize("storage_format, expected_file", [
    (store.StorageFormat.STANDARD, "hosts.mk"),
    (store.StorageFormat.RAW, "hosts.cfg"),
])
def test_storage_host_file(storage_format, expected_file):
    assert storage_format.hosts_file() == expected_file


@pytest.mark.parametrize("file_path, valid_for_standard, valid_for_raw", [
    ("/wato/the/aaa/hosts.mk", True, False),
    ("wato/the/aaa/hosts.mk", False, False),
    ("/wato/the/aaa/hosts.m", False, False),
    ("/wato/the/aaa/hosts.cfg", False, True),
    ("wato/the/aaa/hosts.cfg", False, False),
    ("/wato/the/aaa/hosts.c", False, False),
])
def test_storage_is_hosts_config(file_path, valid_for_standard, valid_for_raw):
    assert store.StorageFormat.STANDARD.is_hosts_config(file_path) == valid_for_standard
    assert store.StorageFormat.RAW.is_hosts_config(file_path) == valid_for_raw


_raw_storage_loader_test_data = """{
    'all_hosts': ['0699z0abcnpsl01', '0699z0abcnpsl02'],
    'host_tags': {
        '0699z0abcnpsl01': {
            'site': 'heute',
            'address_family': 'ip-v4-only',
            'ip-v4': 'ip-v4',
            'agent': 'cmk-agent',
            'tcp': 'tcp',
            'piggyback': 'auto-piggyback',
            'snmp_ds': 'no-snmp',
            'criticality': 'prod',
            'networking': 'lan'
        },
        '0699z0abcnpsl02': {
            'site': 'heute',
            'address_family': 'ip-v4-only',
            'ip-v4': 'ip-v4',
            'agent': 'cmk-agent',
            'tcp': 'tcp',
            'piggyback': 'auto-piggyback',
            'snmp_ds': 'no-snmp',
            'criticality': 'prod',
            'networking': 'lan'
        }
    },
    'host_labels': {
        '0699z0abcnpsl01': {
            'hw': 'test1'
        },
        '0699z0abcnpsl02': {
            'hw': 'test2'
        }
    },
    'attributes': {
        'ipaddresses': {
            '0699z0abcnpsl01': '10.211.162.80',
            '0699z0abcnpsl02': '10.211.162.81'
        },
    },
    'extra_host_conf': {
        'alias': [(u'699 Radius Server 02', ['0699z0abcnpsl02']),
                  (u'699 Radius Server 01', ['0699z0abcnpsl01'])],
        '_neui_country_id': [(u'699', ['0699z0abcnpsl02']), (u'699', ['0699z0abcnpsl01'])]
    },
    'explicit_host_conf': {
        'alias': {
            '0699z0abcnpsl01': '699 Radius Server 01',
            '0699z0abcnpsl02': '699 Radius Server 02'
        },
    },
    'contact_groups': {},
    'host_attributes': {
        '0699z0abcnpsl01': {
            'alias': '699 Radius Server 01',
            'ipaddress': '10.211.162.80',
            'meta_data': {
                'created_at': 1619089977.0,
                'created_by': 'cmkadmin',
                'updated_at': 1619094577.9326406
            },
            'labels': {
                'hw': 'test1'
            },
            'tag_agent': 'cmk-agent',
            'tag_snmp_ds': 'no-snmp',
            'tag_criticality': 'prod'
        },
        '0699z0abcnpsl02': {
            'alias': '699 Radius Server 02',
            'ipaddress': '10.211.162.81',
            'meta_data': {
                'created_at': 1619089977.0,
                'created_by': 'cmkadmin',
                'updated_at': 1619094577.9345043
            },
            'labels': {
                'hw': 'test2'
            },
            'tag_agent': 'cmk-agent',
            'tag_snmp_ds': 'no-snmp',
            'tag_criticality': 'prod'
        }
    },
}
"""


@pytest.fixture(scope="function")
def raw_loader():
    loader = store.RawStorageLoader()
    loader._data = _raw_storage_loader_test_data
    loader.parse()
    loader.apply({})
    yield loader


@pytest.fixture(scope="function")
def pickle_loader():
    loader = store.PickleStorageLoader()
    loader._data = pickle.dumps(ast.literal_eval(_raw_storage_loader_test_data))
    loader.parse()
    loader.apply({})
    yield loader


@pytest.mark.parametrize("loader_name", ["raw_loader", "pickle_loader"])
def test_raw_storage_loader(loader_name, request):
    storage_loader = request.getfixturevalue(loader_name)
    hosts = storage_loader._all_hosts()
    assert hosts == ['0699z0abcnpsl01', '0699z0abcnpsl02']
    ips = storage_loader._attributes()["ipaddresses"]
    host_conf_alias = storage_loader._explicit_host_conf()["alias"]
    for h in hosts:
        assert isinstance(storage_loader._host_tags()[h], dict)
        assert isinstance(storage_loader._host_labels()[h], dict)
        assert isinstance(storage_loader._host_attributes()[h], dict)
        assert isinstance(ips[h], str)
        assert isinstance(host_conf_alias[h], str)

    assert isinstance(storage_loader._extra_host_conf()['alias'], list)
    assert isinstance(storage_loader._extra_host_conf()['_neui_country_id'], list)
