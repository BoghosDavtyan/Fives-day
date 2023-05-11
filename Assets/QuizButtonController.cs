using UnityEngine;
using Michsky.MUIP;
using System.Collections.Generic;

public class QuizButtonController : MonoBehaviour
{
    [System.Serializable]
    public class ButtonMapping
    {
        public GameObject buttonParent;
        public GameObject targetObject;
        public List<GameObject> objectsToTurnOff;

        public ButtonManager GetButtonManager()
        {
            return buttonParent.GetComponentInChildren<ButtonManager>();
        }
    }

    public List<ButtonMapping> buttonMappings;

    private void Start()
    {
        foreach (var mapping in buttonMappings)
        {
            ButtonManager button = mapping.GetButtonManager();
            button.onClick.AddListener(() => ToggleGameObject(mapping));
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
