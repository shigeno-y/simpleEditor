from pxr import Tf
from pxr.Usdviewq.plugin import PluginContainer


class SimpleEditorPluginContainer(PluginContainer):
    def registerPlugins(self, plugRegistry, usdviewApi):
        printer = self.deferredImport(".printMessage")
        self._printMessage = plugRegistry.registerCommandPlugin(
            "SimpleEditor.PrintMessage", "[TUTORIAL] Print Message", printer.main
        )

        edit_add = self.deferredImport(".edit.add")
        self._edit_add_cube = plugRegistry.registerCommandPlugin(
            "SimpleEditor.edit_add_cube", "Add Cube", edit_add.addCube
        )

        edit_edit = self.deferredImport(".edit.edit")
        self._edit_edit = plugRegistry.registerCommandPlugin(
            "SimpleEditor.edit", "Edit Prim", edit_edit.edit
        )

    def configureView(self, plugRegistry, plugUIBuilder):
        simpleEditorMenu = plugUIBuilder.findOrCreateMenu("SimpleEditor")
        simpleEditorMenu.addItem(self._printMessage)
        simpleEditorMenu.addItem(self._edit_add_cube)
        simpleEditorMenu.addItem(self._edit_edit)


Tf.Type.Define(SimpleEditorPluginContainer)
