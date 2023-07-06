#!/usr/bin/python

#    Copyright 2023 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Test for Trestle Bot Authored SSP."""

import os
import pathlib

import pytest
from trestle.common import const
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.author.ssp import SSPGenerate
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal import ssp as ossp

from tests import testutils
from trestlebot.tasks.authored.base_authored import AuthoredObjectException
from trestlebot.tasks.authored.ssp import AuthoredSSP, SSPIndex


test_prof = "simplified_nist_profile"
test_comp = "test_comp"
test_ssp_output = "test-ssp"
markdown_dir = "md_ssp"


def test_assemble(tmp_trestle_dir: str) -> None:
    """Test to test assemble functionality for SSPs"""
    # Prepare the workspace and generate the markdown
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = f"{markdown_dir}/{test_ssp_output}"
    args = testutils.setup_for_ssp(trestle_root, test_prof, test_comp, md_path)
    ssp_generate = SSPGenerate()
    assert ssp_generate._run(args) == 0

    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, test_ssp_output, test_prof, [test_comp])
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    authored_ssp = AuthoredSSP(tmp_trestle_dir, ssp_index)

    # Run to ensure no exceptions are raised
    authored_ssp.assemble(md_path)

    # Check that the ssp is present in the correct location
    ssp, _ = ModelUtils.load_model_for_class(
        trestle_root, test_ssp_output, ossp.SystemSecurityPlan, FileContentType.JSON
    )
    assert len(ssp.control_implementation.implemented_requirements) == 12


def test_assemble_no_ssp_entry(tmp_trestle_dir: str) -> None:
    """Test to trigger failure for missing SSP index"""
    # Prepare the workspace and generate the markdown
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = f"{markdown_dir}/{test_ssp_output}"
    args = testutils.setup_for_ssp(trestle_root, test_prof, test_comp, md_path)
    ssp_generate = SSPGenerate()
    assert ssp_generate._run(args) == 0

    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, "fake", test_prof, [test_comp])
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    authored_ssp = AuthoredSSP(tmp_trestle_dir, ssp_index)

    with pytest.raises(
        AuthoredObjectException, match="SSP test-ssp does not exists in the index"
    ):
        authored_ssp.assemble(md_path)


def test_regenerate(tmp_trestle_dir: str) -> None:
    """Test to test regenerate functionality for SSPs"""
    # Prepare the workspace and generate the markdown
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(markdown_dir, test_ssp_output)
    _ = testutils.setup_for_ssp(trestle_root, test_prof, test_comp, md_path)

    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, test_ssp_output, test_prof, [test_comp])
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    authored_ssp = AuthoredSSP(tmp_trestle_dir, ssp_index)

    # Run to ensure no exceptions are raised
    model_path = os.path.join(const.MODEL_DIR_SSP, test_ssp_output)
    authored_ssp.regenerate(model_path, md_path)

    assert os.path.exists(os.path.join(tmp_trestle_dir, markdown_dir, test_ssp_output))


def test_regenerate_no_ssp_entry(tmp_trestle_dir: str) -> None:
    """Test to trigger failure for missing SSP index"""
    # Prepare the workspace and generate the markdown
    trestle_root = pathlib.Path(tmp_trestle_dir)
    md_path = os.path.join(markdown_dir, test_ssp_output)
    _ = testutils.setup_for_ssp(trestle_root, test_prof, test_comp, md_path)

    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, "fake", test_prof, [test_comp])
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    authored_ssp = AuthoredSSP(tmp_trestle_dir, ssp_index)

    model_path = os.path.join(const.MODEL_DIR_SSP, test_ssp_output)
    with pytest.raises(
        AuthoredObjectException, match="SSP test-ssp does not exists in the index"
    ):
        authored_ssp.regenerate(model_path, md_path)


# SSPIndex tests


def test_get_comps_by_ssp(tmp_trestle_dir: str) -> None:
    """Test to get component definition list from index"""
    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(
        ssp_index_path, test_ssp_output, test_prof, [test_comp, "another_comp"]
    )
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    assert test_comp in ssp_index.get_comps_by_ssp(test_ssp_output)
    assert "another_comp" in ssp_index.get_comps_by_ssp(test_ssp_output)


def test_get_profile_by_ssp(tmp_trestle_dir: str) -> None:
    """Test to get profile from index"""
    ssp_index_path = os.path.join(tmp_trestle_dir, "ssp-index.json")
    testutils.write_index_json(ssp_index_path, test_ssp_output, test_prof, [test_comp])
    ssp_index: SSPIndex = SSPIndex(ssp_index_path)

    assert ssp_index.get_profile_by_ssp(test_ssp_output) == test_prof
