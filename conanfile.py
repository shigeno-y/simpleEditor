# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from conan.tools.files import copy
from conan.tools.scm import Git
from conans import ConanFile


class SimpleEditorDevConan(ConanFile):
    name = "simpleeditor"
    url = "https://github.com/shigeno-y/simpleEditor"
    homepage = url
    license = "Apache-2.0"
    description = "Simple Editor plugin for usdview"
    package_type = "application"
    settings = "os"
    no_copy_source = True

    options = {
        "USD": [
            "v23.11",
            "v23.08",
            "v23.05",
            "v23.02",
            "v22.11",
            "v22.08",
            "v22.05b",
            "v21.11",
        ],
    }
    default_options = {
        "USD": "v23.11",
    }

    def set_version(self):
        git = Git(self, self.recipe_folder)

        tag = "0.1.0"
        try:
            tag = git.run("describe --tags --abbrev=0")
        except Exception:
            pass
        self.version = tag

    def export_sources(self):
        copy(self, "simpleEditor/**", self.recipe_folder, self.export_sources_folder, excludes="**/__pycache__")

    def requirements(self):
        self.requires(f"openusd/{self.options.USD}")

    def config_options(self):
        self.options["openusd"].python = True

    def package(self):
        # This will also copy the "include" folder
        copy(self, "simpleEditor/*", self.source_folder, self.package_folder, excludes="**/__pycache__")

    def package_info(self):
        self.cpp_info.bindirs = list()
        self.cpp_info.libdirs = list()

        self.buildenv_info.prepend_path("PYTHONPATH", str(Path(self.package_folder) / Path("lib/python")))
        self.runenv_info.prepend_path("PYTHONPATH", str(Path(self.package_folder) / Path("lib/python")))

        self.buildenv_info.prepend_path("PXR_PLUGINPATH_NAME", str(Path(self.package_folder) / Path("plugin/usd")))
        self.runenv_info.prepend_path("PXR_PLUGINPATH_NAME", str(Path(self.package_folder) / Path("plugin/usd")))

        for require, dependency in self.dependencies.items():
            binDir = Path(dependency.package_folder) / "bin"
            if binDir.exists():
                self.buildenv_info.prepend_path("PATH", str(binDir.absolute()))
                self.runenv_info.prepend_path("PATH", str(binDir.absolute()))
