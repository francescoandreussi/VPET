/*
-------------------------------------------------------------------------------
VPET - Virtual Production Editing Tools
vpet.research.animationsinstitut.de
https://github.com/FilmakademieRnd/VPET
 
Copyright(c) 2022 Filmakademie Baden-Wuerttemberg, Animationsinstitut R&D Lab
 
This project has been initiated in the scope of the EU funded project 
Dreamspace (http://dreamspaceproject.eu/) under grant agreement no 610005 2014-2016.
 
Post Dreamspace the project has been further developed on behalf of the 
research and development activities of Animationsinstitut.
 
In 2018 some features (Character Animation Interface and USD support) were
addressed in the scope of the EU funded project  SAUCE (https://www.sauceproject.eu/) 
under grant agreement no 780470, 2018-2022
 
VPET consists of 3 core components: VPET Unity Client, Scene Distribution and
Syncronisation Server. They are licensed under the following terms:
-------------------------------------------------------------------------------
*/

//! @file "MenuCreatorModule.cs"
//! @brief Implementation of the IconCreatorModule, creating icons for scene objects without geometry.
//! @author Simon Spielmann
//! @author Jonas Trottnow
//! @version 0
//! @date 03.03.2022

using System;
using System.Collections.Generic;
using UnityEngine;

namespace vpet
{

    public class IconCreatorModule : UIManagerModule
    {
        //!
        //! The list containing all UI elemets of the current menu.
        //!
        private List<SceneObject> m_sceneObjects;
        //!
        //! Prefab for the icon.
        //!
        private GameObject m_Icon;
        //!
        //! Sprite for the light icon.
        //!
        private Sprite m_lightSprite;
        //!
        //! Sprite for the camera icon.
        //!
        private Sprite m_cameraSprite;

        //!
        //! Constructor
        //! @param name Name of this module
        //! @param core Reference to the VPET core
        //!
        public IconCreatorModule(string name, Core core) : base(name, core)
        {
        }



        //!
        //! Init Function
        //!
        protected override void Init(object sender, EventArgs e)
        {
            m_sceneObjects = new List<SceneObject>();
            m_Icon = Resources.Load("Prefabs/Icon") as GameObject;
            m_lightSprite = Resources.Load<Sprite>("Images/LightIcon");
            m_cameraSprite = Resources.Load<Sprite>("Images/CameraIcon");

            SceneManager sceneManager = m_core.getManager<SceneManager>();
            sceneManager.sceneReady += createIcons;
        }

        //!
        //! Function that parses the given list of scene objects to create and
        //! add icons depending on it's type as child objects.
        //!
        private void createIcons(object sender, EventArgs e)
        {
            SceneManager sceneManager = ((SceneManager)sender);

            foreach (SceneObject sceneObject in sceneManager.sceneObjects)
            {
                GameObject icon = null;
                SpriteRenderer renderer = null;
                switch (sceneObject)
                {
                    case SceneObjectLight:
                        icon = GameObject.Instantiate(m_Icon, sceneObject.transform);
                        renderer = icon.GetComponent<SpriteRenderer>();
                        renderer.sprite = m_lightSprite;
                        Parameter<Color> colorParameter = sceneObject.getParameter<Color>("color");
                        renderer.color = colorParameter.value;
                        colorParameter.hasChanged += updateIconColor;
                        m_sceneObjects.Add(sceneObject);
                        break;
                    case SceneObjectCamera:
                        icon = GameObject.Instantiate(m_Icon, sceneObject.transform);
                        renderer = icon.GetComponent<SpriteRenderer>();
                        renderer.sprite = m_cameraSprite;
                        m_sceneObjects.Add(sceneObject);
                        break;
                }

                if (icon)
                    sceneObject._icon = icon;
            }
        }

        //!
        //! Function for updating the color of an icon.
        //!
        //! @param sender The connected parameter holding the color value.
        //! @param color The color value the icon's color will be set to.
        //!
        private void updateIconColor(object sender, Color color)
        {
            SceneObject sceneObject = (SceneObject) ((AbstractParameter)sender).parent;
            sceneObject._icon.GetComponent<SpriteRenderer>().color = color;
        }

        //!
        //! Function for disposing and cleanup of all created gizmos.
        //!
        private void diosposeIcons()
        {
            foreach(SceneObject sceneObject in m_sceneObjects)
            {
                if (sceneObject.GetType() == typeof(SceneObjectLight))
                    sceneObject.getParameter<Color>("color").hasChanged -= updateIconColor;
                
                UnityEngine.Object.Destroy(sceneObject._icon);
            }
        }
    }
}