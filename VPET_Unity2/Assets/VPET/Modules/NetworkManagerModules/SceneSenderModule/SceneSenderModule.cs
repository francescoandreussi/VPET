﻿/*
-------------------------------------------------------------------------------
VPET - Virtual Production Editing Tools
vpet.research.animationsinstitut.de
https://github.com/FilmakademieRnd/VPET
 
Copyright (c) 2021 Filmakademie Baden-Wuerttemberg, Animationsinstitut R&D Lab
 
This project has been initiated in the scope of the EU funded project 
Dreamspace (http://dreamspaceproject.eu/) under grant agreement no 610005 2014-2016.
 
Post Dreamspace the project has been further developed on behalf of the 
research and development activities of Animationsinstitut.
 
In 2018 some features (Character Animation Interface and USD support) were
addressed in the scope of the EU funded project  SAUCE (https://www.sauceproject.eu/) 
under grant agreement no 780470, 2018-2020
 
VPET consists of 3 core components: VPET Unity Client, Scene Distribution and
Syncronisation Server. They are licensed under the following terms:
-------------------------------------------------------------------------------
*/

//! @file "SceneSenderModule.cs"
//! @brief Implementation of the scene sender module, listening to scene requests and sending scene data. 
//! @author Simon Spielmann
//! @author Jonas Trottnow
//! @version 0
//! @date 20.06.2021

using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Threading;
using System;
using NetMQ;
using NetMQ.Sockets;

namespace vpet
{
    //!
    //! Class implementing the scene sender module, listening to scene requests and sending scene data.
    //!
    public class SceneSenderModule : NetworkManagerModule
    {
        private Dictionary<string, byte[]> m_responses;
        //!
        //! Constructor
        //!
        //! @param  name  The  name of the module.
        //! @param core A reference to the VPET core.
        //!
        public SceneSenderModule(string name, Core core) : base(name, core)
        {
        }

        //!
        //! Function, sending messages containing the scene data as reponces to the requested package (executed in separate thread).
        //!
        protected override void run()
        {
            m_isRunning = true;
            AsyncIO.ForceDotNet.Force();
            using (var dataSender = new ResponseSocket())
            {
                dataSender.Bind("tcp://" + m_ip + ":" + m_port);
                Debug.Log("Enter while.. ");

                while (m_isRunning)
                {
                    string message = "";
                    dataSender.TryReceiveFrameString(out message);       // TryReceiveFrameString returns null if no message has been received!
                    if (message != null)
                    {
                        if (m_responses.ContainsKey(message))
                            dataSender.SendFrame(m_responses[message]);
                        else
                            dataSender.SendFrame(new byte[0]);
                    }
                }

                // TODO: check first if closed
                try
                {
                    dataSender.Disconnect("tcp://" + m_ip + ":" + m_port);
                    dataSender.Dispose();
                    dataSender.Close();
                }
                finally
                {
                    NetMQConfig.Cleanup(false);
                }

            }
        }

        //!
        //! Function to start the scene sender module.
        //! @param ip The IP address to be used from the sender.
        //! @param port The port number to be used from the sender.
        //!
        public void sendScene(string ip, string port)
        {
            // [REVIEW]
            m_responses = new Dictionary<string, byte[]>();
            SceneManager.SceneDataHandler dataHandler = m_core.getManager<SceneManager>().sceneDataHandler;

            m_responses.Add("header", dataHandler.headerByteDataRef);
            m_responses.Add("nodes", dataHandler.nodesByteDataRef);
            m_responses.Add("objects", dataHandler.objectsByteDataRef);
            m_responses.Add("characters", dataHandler.characterByteDataRef);
            m_responses.Add("textures", dataHandler.texturesByteDataRef);
            m_responses.Add("materials", dataHandler.materialsByteDataRef);

            start(ip, port);
        }
    }
}