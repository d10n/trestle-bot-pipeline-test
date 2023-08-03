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

"""Test for CLI"""

import sys
from typing import List
from unittest.mock import patch

import pytest

from trestlebot.cli import run as cli_main


@pytest.fixture
def valid_args_dict() -> dict:
    return {
        "branch": "main",
        "markdown-path": "/my/path",
        "oscal-model": "profile",
        "committer-name": "test",
        "committer-email": "test@email.com",
        "working-dir": "tmp",
        "file-patterns": ".",
    }


def args_dict_to_list(args_dict: dict) -> List[str]:
    args = []
    for k, v in args_dict.items():
        args.append(f"--{k}")
        if v is not None:
            args.append(v)
    return args


def test_invalid_oscal_model(monkeypatch, valid_args_dict, capsys):
    """Test invalid oscal model"""
    args_dict = valid_args_dict
    args_dict["oscal-model"] = "fake"
    monkeypatch.setattr(sys, "argv", ["trestlebot", *args_dict_to_list(args_dict)])

    with pytest.raises(SystemExit):
        cli_main()

    captured = capsys.readouterr()
    assert (
        "Invalid value fake for oscal model. Please use catalog, profile, compdef, or ssp."
        in captured.err
    )


def test_no_ssp_index(monkeypatch, valid_args_dict, capsys):
    """Test missing index file for ssp"""
    args_dict = valid_args_dict
    args_dict["oscal-model"] = "ssp"
    args_dict["ssp-index-path"] = ""
    monkeypatch.setattr(sys, "argv", ["trestlebot", *args_dict_to_list(args_dict)])

    with pytest.raises(SystemExit):
        cli_main()

    captured = capsys.readouterr()

    assert "Must set ssp_index_path when using SSP as oscal model." in captured.err


def test_no_markdown_path(monkeypatch, valid_args_dict, capsys):
    """Test without a markdown file passed as a flag"""
    args_dict = valid_args_dict
    args_dict["markdown-path"] = ""
    monkeypatch.setattr(sys, "argv", ["trestlebot", *args_dict_to_list(args_dict)])

    with pytest.raises(SystemExit):
        cli_main()

    captured = capsys.readouterr()

    assert "Must set markdown path with oscal model." in captured.err


def test_with_target_branch(monkeypatch, valid_args_dict, capsys):
    """Test with target branch set an an unsupported Git provider"""
    args_dict = valid_args_dict
    args_dict["target-branch"] = "main"
    monkeypatch.setattr(sys, "argv", ["trestlebot", *args_dict_to_list(args_dict)])

    # Patch is_github_actions since these tests will be running in
    # GitHub Actions
    with patch("trestlebot.cli.is_github_actions") as mock_check:
        mock_check.return_value = False

        with pytest.raises(SystemExit):
            cli_main()

    captured = capsys.readouterr()

    expected_string = (
        "target-branch flag is set with an unset git provider. "
        "To test locally, set the GITHUB_ACTIONS or GITLAB_CI environment variable."
    )

    assert expected_string in captured.err

    mock_check.assert_called_once()
