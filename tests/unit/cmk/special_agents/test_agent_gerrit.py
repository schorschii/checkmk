#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


import pytest

from cmk.utils.semantic_version import SemanticVersion

from cmk.special_agents import agent_gerrit
from cmk.special_agents.agent_gerrit import LatestVersions, SectionName, Sections


def test_parse_arguments() -> None:
    argv = ["--user", "abc", "--password", "123", "review.gerrit.com"]
    args = agent_gerrit.parse_arguments(argv)

    value = (args.user, args.password, args.hostname)
    expected = ("abc", "123", "review.gerrit.com")

    assert value == expected


def test_fetch_section_data() -> None:
    class DummySectionCollector:
        def collect(self) -> Sections:
            return {SectionName("foobar"): {"foo": "bar"}}

    value = agent_gerrit.collect_sections(DummySectionCollector())
    expected = {SectionName("foobar"): {"foo": "bar"}}

    assert value == expected


def test_write_sections(capsys: pytest.CaptureFixture) -> None:
    sections: Sections = {
        SectionName("version"): {
            "current": "1.2.3",
            "latest": {"major": None, "minor": "1.3.4", "patch": "1.2.5"},
        }
    }
    agent_gerrit.write_sections(sections)

    value = capsys.readouterr().out
    expected = """\
<<<gerrit_version:sep(0)>>>
{"current": "1.2.3", "latest": {"major": null, "minor": "1.3.4", "patch": "1.2.5"}}
"""

    assert value == expected


def test_latest_versions() -> None:
    curr, latest_patch, latest_minor, latest_major = "1.2.3", "1.2.5", "1.3.1", "3.0.1"
    raw_versions = [curr, "1.2.4", latest_patch, "1.3.0", latest_minor, "3.0.0", latest_major]
    current = SemanticVersion.from_string(curr)
    versions = [SemanticVersion.from_string(v) for v in raw_versions]

    value = LatestVersions.build(current, versions)
    expected = LatestVersions(major=latest_major, minor=latest_minor, patch=latest_patch)

    assert value == expected


def test_latest_versions_no_available_updates() -> None:
    value = LatestVersions.build(current=SemanticVersion.from_string("1.2.3"), versions=[])
    expected = LatestVersions(major=None, minor=None, patch=None)
    assert value == expected
