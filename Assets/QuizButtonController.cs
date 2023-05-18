using UnityEngine;
using Michsky.MUIP;
using System.Collections.Generic;

public class QuizButtonController : MonoBehaviour
{
    [System.Serializable]
    public class ButtonMapping
    {
        public List<GameObject> buttonParents;
        public GameObject targetObject;
        public List<GameObject> objectsToTurnOff;

        public List<ButtonManager> GetButtonManagers()
        {
            List<ButtonManager> buttonManagers = new List<ButtonManager>();
            foreach (var buttonParent in buttonParents)
            {
                ButtonManager buttonManager = buttonParent.GetComponentInChildren<ButtonManager>();
                if (buttonManager != null)
                {
                    buttonManagers.Add(buttonManager);
                }
            }
            return buttonManagers;
        }
    }

    public List<ButtonMapping> buttonMappings;

    private void Start()
    {
        foreach (var mapping in buttonMappings)
        {
            List<ButtonManager> buttonManagers = mapping.GetButtonManagers();
            foreach (var button in buttonManagers)
            {
                button.onClick.AddListener(() => ToggleGameObject(mapping));
            }
        }
    }

    private void ToggleGameObject(ButtonMapping mapping)
    {
        TurnOffGameObjects(mapping.objectsToTurnOff);
        mapping.targetObject.SetActive(!mapping.targetObject.activeSelf);
    }

    private void TurnOffGameObjects(List<GameObject> objectsToTurnOff)
    {
        foreach (var obj in objectsToTurnOff)
        {
            obj.SetActive(false);
        }
    }
}
