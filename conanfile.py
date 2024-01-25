# SPDX-License-Identifier: Apache-2.0

from conan.tools.env import VirtualRunEnv
from conans import ConanFile


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
        self.requires("usdmmdplugins/[*]")

    def config_options(self):
        self.options["usdmmdplugins"].USD = self.options.USD
        self.options["usdmmdplugins"].build_tools = True
        self.options["usdmmdplugins"].enable_physic_bake = True
        self.options["openusd"].python = True

    def generate(self):
        runenv = VirtualRunEnv(self)
        env = runenv.environment()

        env.prepend_path("PXR_PLUGINPATH_NAME", self.recipe_folder)
        env.prepend_path("PYTHONPATH", self.recipe_folder)

        env.define("TF_DEBUG", "PLUG*")

        envvars = env.vars(self, scope="run")
        envvars.save_script("run_env")
