# SPDX-License-Identifier: Apache-2.0
# Copyright Red Hat, Inc.
"""Utilities for integration test setup"""
import functools
import subprocess
from pathlib import Path


root_repo_dir = Path(__file__).resolve().parent.parent.parent
scripts_dir = root_repo_dir / "scripts"


def is_complytime_installed(install_dir: Path) -> bool:
    install_dir / ".config/complytime"
    openscap_plugin_bin = (install_dir / '.config/complytime/plugins/openscap-plugin').resolve()
    openscap_plugin_conf = (install_dir / '.config/complytime/plugins/openscap-plugin.yml').resolve()
    if not openscap_plugin_bin.exists():
        return False
    if not openscap_plugin_conf.exists():
        return False
    return True


def setup_complytime(complytime_home: Path):
    complytime_home.mkdir(parents=True, exist_ok=True)
    complytime_release_dir = complytime_home
    if not is_complytime_installed(complytime_home):
        result = subprocess.run(
            [scripts_dir / "get-github-release.sh"],
            cwd=complytime_release_dir,
            capture_output=True,
            text=True)
        if result.returncode != 0:
            raise ValueError(f"Unable to install ComplyTime for int test!\n{result.stdout}\n{result.stderr}")
        result = subprocess.run(
            f'for file in releases/*/*_linux_x86_64.tar.gz; do tar -xf "$file"; done',
            cwd=complytime_release_dir,
            shell=True,
        )
        if result.returncode != 0:
            raise ValueError(f"Unable to install ComplyTime for int test!\n{result.stdout}\n{result.stderr}")
        print("stdout:", result.stdout)
        print("exit code:", result.returncode)

    def decorator_setup_complytime(func):
        @functools.wraps
        def wrapper(install_dir: Path) -> None:
            if is_complytime_installed(install_dir):
                return

            result = subprocess.run(
                [scripts_dir / "get-github-release.sh"],
                cwd=install_dir,
                capture_output=True,
                text=True)
            if result.returncode != 0:
                raise ValueError("Unable to install ComplyTime for int test!")
            # return result.stdout, result.returncode

            print("stdout:", result.stdout)
            print("exit code:", result.returncode)
            func_result = func(*args, **kwargs)
            pass
        return wrapper
    return decorator_setup_complytime
