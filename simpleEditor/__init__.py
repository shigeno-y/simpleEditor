# SPDX-License-Identifier: Apache-2.0


from pxr import Tf
from pxr.Usdviewq.plugin import PluginContainer


class SimpleEditorPluginContainer(PluginContainer):
    def registerPlugins(self, plugRegistry, usdviewApi):
        edit = self.deferredImport(".edit")
        self._edit = plugRegistry.registerCommandPlugin(
            "SimpleEditor.edit", "Edit Prim", edit.edit
        )

        graph = self.deferredImport(".graph")
        self._graph = plugRegistry.registerCommandPlugin(
            "SimpleEditor.graph", "Graph View", graph.graph
        )

    def configureView(self, plugRegistry, plugUIBuilder):
        simpleEditorMenu = plugUIBuilder.findOrCreateMenu("SimpleEditor")
        simpleEditorMenu.addItem(self._edit)
        simpleEditorMenu.addItem(self._graph)


Tf.Type.Define(SimpleEditorPluginContainer)
