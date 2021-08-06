"""
-----------------------------------------------------------------------------
This source file is part of VPET - Virtual Production Editing Tools
http://vpet.research.animationsinstitut.de/
http://github.com/FilmakademieRnd/VPET

Copyright (c) 2021 Filmakademie Baden-Wuerttemberg, Animationsinstitut R&D Lab

This project has been initiated in the scope of the EU funded project
Dreamspace under grant agreement no 610005 in the years 2014, 2015 and 2016.
http://dreamspaceproject.eu/
Post Dreamspace the project has been further developed on behalf of the
research and development activities of Animationsinstitut.

The VPET component Blender Scene Distribution is intended for research and development
purposes only. Commercial use of any kind is not permitted.

There is no support by Filmakademie. Since the Blender Scene Distribution is available
for free, Filmakademie shall only be liable for intent and gross negligence;
warranty is limited to malice. Scene DistributiorUSD may under no circumstances
be used for racist, sexual or any illegal purposes. In all non-commercial
productions, scientific publications, prototypical non-commercial software tools,
etc. using the Blender Scene Distribution Filmakademie has to be named as follows:
“VPET-Virtual Production Editing Tool by Filmakademie Baden-Württemberg,
Animationsinstitut (http://research.animationsinstitut.de)“.

In case a company or individual would like to use the Blender Scene Distribution in
a commercial surrounding or for commercial purposes, software based on these
components or any part thereof, the company/individual will have to contact
Filmakademie (research<at>filmakademie.de).
-----------------------------------------------------------------------------
"""

import bpy

from .serverAdapter import set_up_thread
from .serverAdapter import close_socket_d
from .serverAdapter import close_socket_s
from .tools import cleanUp, installZmq, checkZMQ
from .tools import setupCollections
from .sceneDistribution import gatherSceneData

## operator classes
#
class SetupScene(bpy.types.Operator):
    bl_idname = "object.setup_vpet"
    bl_label = "VPET Scene Setup"

    def execute(self, context):
        print('setup scene')
        setupCollections()
        return {'FINISHED'}


class DoDistribute(bpy.types.Operator):
    bl_idname = "object.zmq_distribute"
    bl_label = "VPET Do Distribute"

    def execute(self, context):
        print("do distribute")
        if checkZMQ():
            reset()
            objCount = gatherSceneData()
            if objCount > 0:
                set_up_thread()
                self.report({'INFO'}, f'Sending {str(objCount)} Objects to VPET')
            else:
                self.report({'ERROR'}, 'VPET collections not found or empty')
        else:
            self.report({'ERROR'}, 'Please Install Zero MQ before continuing')
        
        return {'FINISHED'}

class StopDistribute(bpy.types.Operator):
    bl_idname = "object.zmq_stopdistribute"
    bl_label = "VPET Stop Distribute"

    def execute(self, context):
        print('stop distribute')
        print('stop subscription')
        reset()
        return {'FINISHED'}

class InstallZMQ(bpy.types.Operator):
    bl_idname = "object.zmq_install"
    bl_label = "Install ZMQ"

    def execute(self, context):
        print('installing ZMQ')
        zmq_result = installZmq()
        if zmq_result == True:
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, str(zmq_result))
            return {'FAILED'}

def reset():
    close_socket_d()
    close_socket_s()
    cleanUp()