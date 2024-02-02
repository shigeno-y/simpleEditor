# SPDX-License-Identifier: Apache-2.0


from pathlib import Path

from conan.tools.env import VirtualRunEnv
from conans import ConanFile


class conan(ConanFile):
    settings = "os"
    no_copy_source = True

    def requirements(self):
        self.requires("simpleeditor/[*]"),

    def generate(self):
        runenv = VirtualRunEnv(self)
        runenv.generate()
