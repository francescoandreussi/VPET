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
import struct
import mathutils
import math

## Setup ZMQ thread
def set_up_thread():
    try:
        import zmq
    except Exception as e:
        print('Could not import ZMQ\n' + str(e))
    global vpet, v_prop
    vpet = bpy.context.window_manager.vpet_data
    v_prop = bpy.context.scene.vpet_properties
    # Prepare ZMQ
    vpet.ctx = zmq.Context()
    
    # Prepare Subscriber
    vpet.socket_s = vpet.ctx.socket(zmq.SUB)
    vpet.socket_s.connect(f'tcp://{v_prop.server_ip}:{v_prop.sync_port}')
    vpet.socket_s.setsockopt_string(zmq.SUBSCRIBE, "")
    vpet.socket_s.setsockopt(zmq.RCVTIMEO,1)   
    
    bpy.app.timers.register(listener)
    
    # Prepare Distributor
    vpet.socket_d = vpet.ctx.socket(zmq.REP)
    vpet.socket_d.bind(f'tcp://{v_prop.server_ip}:{v_prop.dist_port}')

    # Prepare poller
    vpet.poller = zmq.Poller()
    vpet.poller.register(vpet.socket_d, zmq.POLLIN)    

    bpy.app.timers.register(read_thread)

## Read requests and send packages
def read_thread():
    global vpet, v_prop
    vpet = bpy.context.window_manager.vpet_data
    v_prop = bpy.context.scene.vpet_properties
    if vpet.socket_d:
        # Get sockets with messages (0: don't wait for msgs)
        sockets = dict(vpet.poller.poll(0))
        # Check if this socket has a message
        if vpet.socket_d in sockets:
            # Receive message
            msg = vpet.socket_d.recv_string()
            print(msg) # debug
            # Classify message
            if msg == "header":
                print("Header request! Sending...")
                vpet.socket_d.send(vpet.headerByteData)
            elif msg == "nodes":
                print("Nodes request! Sending...")
                vpet.socket_d.send(vpet.nodesByteData)
            elif msg == "objects":
                print("Object request! Sending...")
                vpet.socket_d.send(vpet.geoByteData)
            elif msg == "textures":
                print("Texture request! Sending...")
                vpet.socket_d.send(vpet.texturesByteData)
            else: # sent empty
                vpet.socket_d.send_string("")
    return 0.1 # repeat every .1 second

## process scene updates
def listener():
    global vpet, v_prop
    vpet = bpy.context.window_manager.vpet_data
    v_prop = bpy.context.scene.vpet_properties
    msg = None
    try:
        msg = vpet.socket_s.recv()
    except Exception as e:
        msg = None
        
    if msg != None:
        type = vpet.parameterTypes[msg[1]]
        objName = bytearray(vpet.nodeList[msg[2]].name).decode('ascii')
        obj = bpy.data.objects[objName]
        objType = vpet.nodeTypes[vpet.nodeList[msg[2]].vpetType]
        
        if type == 'POS':
            newPos = mathutils.Vector((     unpack('f', msg, 6),\
                                            unpack('f', msg, 10),\
                                            unpack('f', msg, 14)))
                                            
            obj.location = (newPos[0], newPos[2], newPos[1])
            
        elif type == 'ROT':
            newRot = mathutils.Quaternion(( unpack('f', msg, 6),\
                                            unpack('f', msg, 14),\
                                            unpack('f', msg, 10),\
                                            unpack('f', msg, 18)))
            newRot.invert()
            obj.rotation_mode = 'QUATERNION'
            newQuat = mathutils.Quaternion((newRot[3],\
                                            newRot[0],\
                                            -newRot[1],\
                                            -newRot[2]))

            obj.rotation_quaternion = newQuat

            obj.rotation_mode = 'XYZ'

            if objType == 'LIGHT' or objType == 'CAMERA':
                obj.rotation_euler.rotate_axis("X", math.radians(90))

        elif type == 'SCALE':
            newScale = mathutils.Vector((   unpack('f', msg, 6),\
                                            unpack('f', msg, 10),\
                                            unpack('f', msg, 14)))
                                            
            obj.scale = (newScale[0], newScale[2], newScale[1])
            
        elif type == 'LOCK':
            pass
        elif type == 'HIDDENLOCK':
            pass
        elif type == 'KINEMATIC':
            pass
        elif type == 'FOV':
            print(type)
            print(unpack('f', msg, 6))
            
        elif type == 'ASPECT':
            print(type)
            print(unpack('f', msg, 6))
            
        elif type == 'FOCUSDIST':
            print(type)
            print(unpack('f', msg, 6))
            
        elif type == 'FOCUSSIZE':
            print(type)
            print(unpack('f', msg, 6))
            
        elif type == 'APERTURE':
            print(type)
            print(unpack('f', msg, 6))
            
        elif type == 'COLOR':
            newColor = (unpack('f', msg, 6), unpack('f', msg, 10), unpack('f', msg, 14))
            obj.data.color = newColor
            
        elif type == 'INTENSITY':
            obj.data.energy = unpack('f', msg, 6)*100
            
        elif type == 'EXPOSURE':
            # no exposure in Blender
            pass
        elif type == 'RANGE':
            # no range in Blender
            pass
        elif type == 'ANGLE':
            obj.data.spot_size = math.radians(unpack('f', msg, 6))
        elif type == 'BONEANIM':
            pass
            
    return 0.01 # repeat every .1 second

def unpack(type, array, offset):
    return struct.unpack_from(type, array, offset)[0]
                
## Stopping the thread and closing the sockets

def close_socket_d():
    global vpet, v_prop
    vpet = bpy.context.window_manager.vpet_data
    v_prop = bpy.context.scene.vpet_properties
    if bpy.app.timers.is_registered(read_thread):
        print("Stopping thread")
        bpy.app.timers.unregister(read_thread)
    if vpet.socket_d:
        vpet.socket_d.close()
        
def close_socket_s():
    global vpet, v_prop
    vpet = bpy.context.window_manager.vpet_data
    v_prop = bpy.context.scene.vpet_properties
    if bpy.app.timers.is_registered(listener):
        print("Stopping subscription")
        bpy.app.timers.unregister(listener)
    if vpet.socket_s:
        vpet.socket_s.close()