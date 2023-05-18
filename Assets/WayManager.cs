using System.Collections.Generic;
using UnityEngine;

public class WayManager : MonoBehaviour
{
    public List<GameObject> objects;

    private GameObject _currentlyEnabledObject;

    private void Start()
    {
        // Disable all objects in the list at the beginning
        foreach (GameObject obj in objects)
        {
            obj.SetActive(false);
        }
    }

    public void EnableObject(GameObject newObject)
    {
        // If there is a currently enabled object, disable it
        if (_currentlyEnabledObject != null)
        {
            _currentlyEnabledObject.SetActive(false);
        }

        // Enable the new object and set it as the currently enabled object
        newObject.SetActive(true);
        _currentlyEnabledObject = newObject;
    }
}
