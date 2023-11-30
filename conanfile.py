# SPDX-License-Identifier: usdMMDPlugins-LICENSE-1

from pathlib import Path

from conans import ConanFile
from conan.tools.env import Environment


class SimpleEditorDevConan(ConanFile):
    no_copy_source = True
    settings = "os"
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

    def requirements(self):
        self.requires(f"openusd/{self.options.USD}")

    def config_options(self):
        self.options["openusd"].python = True

    def generate(self):
        env = Environment()

        env.define("PXR_PLUGINPATH_NAME", self.recipe_folder)
        env.prepend_path("PYTHONPATH", self.recipe_folder)

        env.define("TF_DEBUG", "PLUG*")

        for require, dependency in self.dependencies.items():
            bin = Path(dependency.package_path) / "bin"
            if bin.exists():
                env.prepend_path("PATH", str(bin))

            lib = Path(dependency.package_path) / "lib"
            if lib.exists():
                env.prepend_path("PATH", str(lib))

            pythonpath = Path(dependency.package_path) / "lib" / "python"
            if pythonpath.exists():
                env.prepend_path("PYTHONPATH", str(pythonpath))

        envvars = env.vars(self, scope="run")
        envvars.save_script("run_env")
