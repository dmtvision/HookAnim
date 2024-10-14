bl_info = {
    "name": "HookAnim",
    "author": "Hugo Livet",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "Properties > Object Properties > HookAnim",
    "description": "Easily animate verts inside a mesh using empty objects",
    "category": "Animation",
}

import bpy
from bpy.types import Panel, Operator

class OBJECT_OT_create_hooks(Operator):
    bl_idname = "object.create_hooks"
    bl_label = "Create Hooks"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            # Create a new collection for hooks
            hook_collection = bpy.data.collections.new(f"{obj.name}_hook")
            bpy.context.scene.collection.children.link(hook_collection)

            # Deselect all vertices before starting
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')

            # Create hooks for each vertex
            for i, v in enumerate(obj.data.vertices):
                # Get the vertex's world coordinates
                world_position = obj.matrix_world @ v.co

                # Create empty
                empty = bpy.data.objects.new(f"{obj.name}_hook_{i}", None)
                empty.empty_display_type = 'SPHERE'
                empty.empty_display_size = 0.1
                hook_collection.objects.link(empty)

                # Set empty's location to the vertex's world coordinates
                empty.location = world_position

                # Parent empty to the mesh object
                empty.parent = obj

                # Add hook modifier
                hook_mod = obj.modifiers.new(f"Hook_{i}", type='HOOK')
                hook_mod.object = empty
                hook_mod.vertex_indices_set([i])

            # Reset hooks in a batch after creating all of them
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

            for i in range(len(obj.data.vertices)):
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                obj.data.vertices[i].select = True
                bpy.ops.object.mode_set(mode='EDIT')
                hook_mod_name = f"Hook_{i}"
                bpy.ops.object.hook_reset(modifier=hook_mod_name)
                bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}

class OBJECT_OT_delete_hooks(Operator):
    bl_idname = "object.delete_hooks"
    bl_label = "Delete Hooks"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            hook_collection = bpy.data.collections.get(f"{obj.name}_hook")
            if hook_collection:
                # Remove hook modifiers
                for mod in obj.modifiers:
                    if mod.type == 'HOOK':
                        obj.modifiers.remove(mod)

                # Delete objects in the collection
                for ob in hook_collection.objects:
                    bpy.data.objects.remove(ob, do_unlink=True)

                # Remove the collection
                bpy.data.collections.remove(hook_collection)

        return {'FINISHED'}

class OBJECT_PT_hook_anim(Panel):
    bl_label = "HookAnim"
    bl_idname = "OBJECT_PT_hook_anim"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.create_hooks", text="Create Hooks")
        layout.operator("object.delete_hooks", text="Delete Hooks")

def register():
    bpy.utils.register_class(OBJECT_OT_create_hooks)
    bpy.utils.register_class(OBJECT_OT_delete_hooks)
    bpy.utils.register_class(OBJECT_PT_hook_anim)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_hook_anim)
    bpy.utils.unregister_class(OBJECT_OT_delete_hooks)
    bpy.utils.unregister_class(OBJECT_OT_create_hooks)

if __name__ == "__main__":
    register()
