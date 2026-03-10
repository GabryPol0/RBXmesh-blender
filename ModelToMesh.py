#
# - ghostypep
#
# NOTICE!!!! DO YOU NOTICE ME!!!! COOL
# to export objects you need to have them SELECTED!!!! only one at a time!!!!
#
# this is a plugin that allows for easy mesh importing and exporting with blender
#
# it is (probably) horribly written because i do not use python ever. i use luau.
#
# unfortunately for the doubters it (somehow) works.
#
# it only supports importing (and exporting) version 2.00 meshes.
# you're only missing out on LODs, mesh deformation and facial animations
# thankfully nobody cares!!! this is only really for animators and modellers who don't need any of that.
#
# very cool resource by clonetrooper1019/maximum_adhd for how this works
# https://devforum.roblox.com/t/roblox-mesh-format/326114
#
# put exported .mesh files in the roblox > current studio version folder > content. if you don't know where that is figure it out BUDDY!!!!
# load them with rbxasset://(path to wherever). rbxasset pretty much just starts you from the content folder so like rbxasset://folder/mesh.mesh
#
# fun fact: the rbxasset method actually works for every file type. 
# you could load images with .png (or .dds??? the fuck??) and videos with .webm (very buggy)
# and now you can load meshes!!!! wwe're so back

##
## - gabry_polo
##
## Heya! Gabry here, so I fixed the code and made small adjustments.
##
## It now exports UV maps correctly ( I think )... Whoho!
## 
## Also, I left few comments around in which i tried my best to explain the code.
## PLEASE use the documentation to figure out how this cursed file type works. You won't learn a single thing here.
##
## P.S: Multiple comments made by ghosty had to be removed since they were filled with swears :,>. The ones left are recognizable by only having 1 "#", unlike mine that have 2.



import bpy
import bmesh
import struct
import mathutils
import os
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

def build_mesh(vertex_list, face_list): ## Function used to create the model from the .mesh file
    
    mesh = bpy.data.meshes.new("Imported_Mesh")
    bm = bmesh.new()    
    for vertex in vertex_list: ## Gets the XYZ positions of vectors and basically creates them
        
        newvert = bm.verts.new((-vertex[0], vertex[2], vertex[1]))
        newvert.normal = mathutils.Vector((-vertex[3], vertex[5], vertex[4]))
        
    
    bm.verts.ensure_lookup_table()
    
    for face in face_list: ## Creates the faces of the object
        
        vert1 = bm.verts[face[0]]
        vert2 = bm.verts[face[1]]
        vert3 = bm.verts[face[2]]
        
        newface = bm.faces.new((vert1, vert2, vert3))
        
        
        newface.smooth = True 
    
        newface.normal_flip()
    
    bm.verts.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.new("MeshUV") ## Creates the UV layer
    
    vertex_index = 0
    
    for vertex in bm.verts: ## Reads and sets up UV using vertexes
        for loop in vertex.link_loops:
            this_vertex = vertex_list[vertex_index]
            print("[" + str(vertex_index) + "] = " + str(this_vertex))
            this_uv = mathutils.Vector((this_vertex[6], this_vertex[7]))
            #print(this_uv)
            loop[uv_layer].uv = this_uv
        
        vertex_index = vertex_index + 1
    
    
    
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("RBXMesh", mesh)
    
    bpy.context.scene.collection.objects.link(obj)
    
    

def read_mesh(context, filepath): ## Reads the .mesh file to load into blender, it basically just uses the function above and gives it a list of vertexes and faces
    
    versiontext = "version x.xx\n"
    
    f = open(filepath, 'rb')
    data = f.read()
    
    version_string = "c" * len(versiontext)
    header_string = "HBBII"
    vertex_string = "ffffffffbbbbBBBB"
    face_string = "III"
    
    version_size = struct.calcsize(version_string)
    header_size = struct.calcsize(header_string)
    vertex_size = struct.calcsize(vertex_string)
    face_size = struct.calcsize(face_string)
    
    read_offset = 0
    buffer_size = version_size
    
    version_unpack = struct.unpack_from(version_string, data[:buffer_size], read_offset)
    
    read_offset = read_offset + version_size
    buffer_size = buffer_size + header_size
    
    header_unpack = struct.unpack_from(header_string, data[:buffer_size], read_offset)
    

    sizeof_MeshHeader = header_unpack[0]
    sizeof_Vertex = header_unpack[1]
    sizeof_Face = header_unpack[2]
    numVerts = header_unpack[3]
    numFaces = header_unpack[4]
    
    if sizeof_Vertex == 36:
        print("mesh does not use rgba")
        vertex_string = "ffffffffbbbb"
        vertex_size = sizeof_Vertex
        
    read_offset = read_offset + sizeof_MeshHeader
    buffer_size = buffer_size + vertex_size
    
    vertex_list = []
    face_list = []
    
    for i in range(0, numVerts):
        this_vertex = struct.unpack_from(vertex_string, data[:buffer_size], read_offset)
        
        if vertex_size == 36:
            this_vertex = this_vertex + (255, 255, 255, 255)
        
        read_offset = read_offset + vertex_size
        buffer_size = buffer_size + vertex_size
        
        vertex_list.append(this_vertex)
    
    #print(vertex_list)
    #print("^^^ thats vertex list")
    
    # okj true>???
    
    for i in range(0, numFaces):
        
        this_face = struct.unpack_from(face_string, data[:buffer_size], read_offset)
        
        read_offset = read_offset + face_size
        buffer_size = buffer_size + face_size
        
        face_list.append(this_face)
        
    #print(face_list)
    #print("^^^ thats face list")
    # ok true:??? that is the face list
    
    build_mesh(vertex_list, face_list)
    
    f.close()
    
    # free ghostypep
    
    return {'FINISHED'}

def write_mesh(context, filepath): ## Function that actually creates the .mesh file when you export ( Very important!!! )
    
    ## File information
    
    split_path = filepath.split("\\")
    
    want_name = split_path[len(split_path)-1]
    
    split_path = filepath[0:len(filepath) - len(want_name):1]
    
    if want_name.find(".mesh") == -1:
        want_name = want_name + ".mesh"
    
    filename = want_name
    new_path = split_path + "/" + filename
    
    if os.path.exists(new_path):
        os.utime(new_path, None)
    else:
        open(new_path, 'a').close()
    
    file = open(new_path, 'wb')

    ## Actually wiring the file
    
    version_string = 'version 2.00\n'
    
    file.write(bytes(version_string, "utf-8"))
    
    selected_object = bpy.context.selected_objects[0]
    bm = bmesh.new()
    bm.from_mesh(selected_object.data)
    bm.transform(selected_object.matrix_basis)
    
    bmesh.ops.triangulate(bm, faces=bm.faces)
    
    ## Setting up Header
    
    # byte format taken from devforum bost
    # numbers taken from the standard size of those formats
    
    sizeof_MeshHeader = 1 + 1 + 2 + 4 + 4 
    sizeof_Vertex = 40
    sizeof_Faces = 4 + 4 + 4
    numVerts = len(bm.verts)
    numFaces = len(bm.faces)
    
    # turn it into bytes
    
    sizeof_MeshHeader = struct.pack("H", sizeof_MeshHeader)
    sizeof_Vertex = struct.pack("B", sizeof_Vertex)
    sizeof_Faces = struct.pack("B", sizeof_Faces)
    numVerts = struct.pack("I", numVerts)
    numFaces = struct.pack("I", numFaces)
    
    ##FileMeshHeaderv2 - writes the header information

    # write it
    
    file.write(sizeof_MeshHeader)
    file.write(sizeof_Vertex)
    file.write(sizeof_Faces)
    file.write(numVerts)
    file.write(numFaces)
    
    bm.verts.index_update()
    
    ##print("[[[[[[UV COORDS]]]]]]")

    for vertex in bm.verts:

        vert_position = vertex.co
        vert_normal = vertex.normal
        vert_tangent = vertex.link_loops[0].calc_tangent()

        uv_layer = bm.loops.layers.uv.active
        for loop in vertex.link_loops:
            uv_coords = loop[uv_layer].uv
            ##print(f"UV X: {uv_coords.x}, UV Y: {uv_coords.y}")

            vert_uv = mathutils.Vector((uv_coords.x, uv_coords.y))

        ##vert_uv = (5, 0) - PROBLEMATIC LINE - This old line has been changed to the loop above this so it actually creates the UV :D
        
        #vert_position = vert_position * obj_scale + obj_position
        
        
        tangent_sign = -1
        
        if vert_tangent.magnitude <= 0:
            tangent_sign = 1
        
        
        ## Position

        px = struct.pack("f", -vert_position[0])
        py = struct.pack("f", vert_position[2])
        pz = struct.pack("f", vert_position[1])
        
        ## Normals

        nx = struct.pack("f", -vert_normal[0])
        ny = struct.pack("f", vert_normal[2])
        nz = struct.pack("f", vert_normal[1])
        
        ## UV

        tu = struct.pack("f", vert_uv[0])
        tv = struct.pack("f", vert_uv[1])

        ## more stuff
        
        tx = struct.pack("b", round(vert_tangent[0]))
        ty = struct.pack("b", round(vert_tangent[2]))
        tz = struct.pack("b", round(vert_tangent[1]))
        ts = struct.pack("b", tangent_sign)
        

        ## !!! This code section might not work, please modify it yourself if you need to !!!

        r = struct.pack("B", 255)
        g = struct.pack("B", 255)
        b = struct.pack("B", 255)
        a = struct.pack("B", 255)
        
        # write vertex bytes
        
        ## FileMeshVertex

        file.write(px) ## Writes positions
        file.write(py)
        file.write(pz)
        
        file.write(nx) ## Writes normals
        file.write(ny)
        file.write(nz)
        
        file.write(tu) ## Writes UV
        file.write(tv)
        
        file.write(tx) ## Writes even more stuff
        file.write(ty)
        file.write(tz)
        file.write(ts)
        
        file.write(r)
        file.write(g)
        file.write(b)
        file.write(a)
    
    for face in bm.faces:
        
        ##FileMeshFaces

        # oh but vert index works fine here ok buddy
        
        #print((face.verts[0].index, face.verts[1].index, face.verts[2].index))
        
        file.write(struct.pack("I", face.verts[0].index))
        file.write(struct.pack("I", face.verts[1].index))
        file.write(struct.pack("I", face.verts[2].index))
        
        face.normal_update()
        face.normal_flip()
    
    
    bm.free()
    file.close()

    return {'FINISHED'}
    

# stolen from the file import template lmao!!!!!!
class ImportClass(Operator, ImportHelper):
    bl_idname = "rbxformat.mesh_import"
    bl_label = "Roblox Mesh Format (.mesh)"

    filename_ext = ".mesh"

    filter_glob: StringProperty(
        default="*.mesh",
        options={'HIDDEN'},
        maxlen=1024*16,
    )

    def execute(self, context):
        return read_mesh(context, self.filepath)

class ExportClass(Operator, ImportHelper):
    bl_idname = "rbxformat.mesh_export"
    bl_label = "Roblox Mesh Format (.mesh)"
    
    filename_ext = ".mesh"
    
    filter_glob: StringProperty(
        default="*.mesh",
        options={'HIDDEN'},
        maxlen=1024*16,
    )

    def execute(self, context):
        return write_mesh(context, self.filepath)

def menu_func_import(self, context):
    self.layout.operator(ImportClass.bl_idname, text=ImportClass.bl_label)

def menu_func_export(self, context):
    self.layout.operator(ExportClass.bl_idname, text=ExportClass.bl_label)

def register():
    bpy.utils.register_class(ImportClass)
    bpy.utils.register_class(ExportClass)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ImportClass)
    bpy.utils.unregister_class(ExportClass)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

# had to steal this from rbx2blender because i didn't know how to do it :smiling_imp:
# this might* just not work for anything below 4.0. can't be asked to cfheck.

bl_info = {"name": "Roblox Mesh Format", "category": "Import-Export", "blender": (4, 0, 0)}

if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.rbxformat.mesh_import('INVOKE_DEFAULT')
    bpy.ops.rbxformat.mesh_export('INVOKE_DEFAULT')