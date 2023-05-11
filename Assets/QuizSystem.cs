using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Michsky.MUIP;

public class QuizSystem : MonoBehaviour
{
    [SerializeField] private ButtonManager buttonManager;
    [SerializeField] private GameObject gameElement;
    [SerializeField] private GameObject specificObjectToDisable;
    [SerializeField] private List<GameObject> objectsToDisableGameElement;

    private void Start()
    {
        // Add event listener for button click
        buttonManager.onClick.AddListener(OnButtonClick);
    }

    private void OnButtonClick()
    {
        // Disable game element if any of the objects are enabled
        foreach (GameObject obj in objectsToDisableGameElement)
        {
            if (obj.activeSelf)
            {
                gameElement.SetActive(false);
                return; // Exit the loop early if game element is disabled
            }
        }

        // Enable game element and disable specific object
        gameElement.SetActive(true);
        specificObjectToDisable.SetActive(false);
    }

    private void Update()
    {
        // Check if any of the objects in the list are enabled
        foreach (GameObject obj in objectsToDisableGameElement)
        {
            if (obj.activeSelf)
            {
                // Disable game element if any of the objects are enabled
                gameElement.SetActive(false);
                return; // Exit the loop early if game element is disabled
            }
        }

        // Enable game element if none of the objects in the list are enabled
        gameElement.SetActive(true);
    }
}
