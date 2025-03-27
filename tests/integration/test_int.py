# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Red Hat, Inc.

"""
Integration tests for validating that trestle-bot output is consumable by complytime
"""

import logging
import pathlib
import shutil
import subprocess
import tempfile
from typing import Tuple, Generator, TypeVar

import pytest
from click import BaseCommand
from click.testing import CliRunner

from git import Repo

from int.int_setup import setup_complytime
from trestlebot.cli.commands.sync_cac_content import sync_cac_catalog_cmd, sync_cac_content_profile_cmd, \
    sync_content_to_component_definition_cmd
from tests.testutils import TEST_DATA_DIR, setup_for_catalog, setup_for_profile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

test_content_dir = TEST_DATA_DIR / "content_dir"

T = TypeVar("T")
YieldFixture = Generator[T, None, None]

_TEST_PREFIX = "trestlebot_tests"


@pytest.mark.slow
def test_complytime_setup() -> None:
    result = subprocess.run(
        ['complytime', 'list'],
        # cwd=complytime_home,
        capture_output=True,
    )
    assert result.returncode == 0


@pytest.mark.slow
def test_sync_catalog(tmp_repo: Tuple[str, Repo]) -> None:
    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    setup_for_catalog(repo_path, "simplified_nist_catalog", "catalog")
    test_cac_control = "abcd-levels"

    runner = CliRunner()
    assert isinstance(sync_cac_catalog_cmd, BaseCommand)
    result = runner.invoke(
        sync_cac_catalog_cmd,
        [
            "--cac-content-root",
            test_content_dir,
            "--repo-path",
            str(repo_path.resolve()),
            "--policy-id",
            test_cac_control,
            "--oscal-catalog",
            test_cac_control,
            "--committer-email",
            "test@email.com",
            "--committer-name",
            "test name",
            "--branch",
            "test",
            "--dry-run",
        ],
    )
    # Check the CLI sync-cac-content is successful
    assert result.exit_code == 0, result.output





@pytest.mark.slow
def test_sync_component_definition(tmp_init_dir: str) -> None:
    """Test `trestlebot sync component-definition`"""
    tmp_init_dir = pathlib.Path(tmp_init_dir)
    setup_complytime(tmp_init_dir)
    assert True



@pytest.mark.slow
def test_sync_profile(tmp_repo: Tuple[str, Repo]) -> None:
    """Test `trestlebot sync profile`"""
    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)

    setup_for_catalog(repo_path, "simplified_nist_catalog", "catalog")

    runner = CliRunner()
    result = runner.invoke(
        sync_cac_content_profile_cmd,
        [
            "--repo-path",
            str(repo_path.resolve()),
            "--cac-content-root",
            str(test_content_dir),
            "--product",
            "rhel8",
            "--oscal-catalog",
            "simplified_nist_catalog",
            "--policy-id",
            "1234-levels",
            "--filter-by-level",
            "medium",
            "--committer-email",
            "test@email.com",
            "--committer-name",
            "test name",
            "--branch",
            "test",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert True


@pytest.mark.slow
def test_create_compdef(tmp_repo: Tuple[str, Repo]) -> None:
    """Test `trestlebot create compdef`"""
    repo_dir, _ = tmp_repo
    repo_path = pathlib.Path(repo_dir)
    setup_for_catalog(repo_path, "simplified_nist_catalog", "catalog")
    setup_for_profile(repo_path, "simplified_nist_profile", "profile")
    test_comp_path = "component-definitions/rhel8/component-definition.json"

    runner = CliRunner()
    result = runner.invoke(
        sync_content_to_component_definition_cmd,
        [
            "--product",
            "rhel8",
            "--repo-path",
            str(repo_path.resolve()),
            "--cac-content-root",
            test_content_dir,
            "--cac-profile",
            "products/rhel8/profiles/example.profile",
            "--oscal-profile",
            "simplified_nist_profile",
            "--committer-email",
            "test@email.com",
            "--committer-name",
            "test name",
            "--branch",
            "test",
            "--dry-run",
            "--component-definition-type",
            "validation",
        ],
    )
    # Check the CLI sync-cac-content is successful
    assert result.exit_code == 0
    assert True


@pytest.mark.slow
def test_create_ssp() -> None:
    """Test `trestlebot create ssp`"""
    assert True
