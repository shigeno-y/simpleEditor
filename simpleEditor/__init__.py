# SPDX-License-Identifier: Apache-2.0


from pxr import Tf
from pxr.Usdviewq.plugin import PluginContainer


class SimpleEditorPluginContainer(PluginContainer):
    def registerPlugins(self, plugRegistry, usdviewApi):
        edit = self.deferredImport(".edit")
        self._edit = plugRegistry.registerCommandPlugin("SimpleEditor.edit", "Edit Prim", edit.edit)

    def configureView(self, plugRegistry, plugUIBuilder):
        simpleEditorMenu = plugUIBuilder.findOrCreateMenu("SimpleEditor")
        simpleEditorMenu.addItem(self._edit)


Tf.Type.Define(SimpleEditorPluginContainer)
