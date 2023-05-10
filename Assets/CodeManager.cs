using UnityEngine;
using TMPro;
using Michsky.MUIP;
using UnityEngine.Events;
using System.Collections.Generic;

public class CodeManager : MonoBehaviour
{
    [SerializeField] private TMP_InputField inputField;
    [SerializeField] private ButtonManager submitButton;
    [SerializeField] private List<PasswordObject> passwordObjects;

    private GameObject currentActiveObject;

    private void Start()
    {
        submitButton.onClick.AddListener(CheckPassword);
    }

    private void CheckPassword()
    {
        string inputPassword = inputField.text;

        foreach (PasswordObject passwordObject in passwordObjects)
        {
            if (inputPassword == passwordObject.password)
            {
                if (currentActiveObject != null)
                {
                    currentActiveObject.SetActive(false);
                }

                passwordObject.associatedObject.SetActive(true);
                currentActiveObject = passwordObject.associatedObject;
                Debug.Log("Correct password");
                return;
            }
        }

        Debug.Log("Incorrect password");
    }

    [System.Serializable]
    public class PasswordObject
    {
        public string password;
        public GameObject associatedObject;
    }
}