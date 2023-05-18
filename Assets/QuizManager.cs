using UnityEngine;
using UnityEngine.UI;
using Michsky.MUIP;

public class QuizManager : MonoBehaviour
{
    [SerializeField] private ButtonManager buttonManager;
    [SerializeField] private GameObject gameElement;
    [SerializeField] private GameObject specificObjectToDisable;

    private void Start()
    {
        // Add event listener for button click
        buttonManager.onClick.AddListener(OnButtonClick);
    }

    private void OnButtonClick()
    {
        // Enable game element and disable specific object
        gameElement.SetActive(true);
        specificObjectToDisable.SetActive(false);
    }
}
