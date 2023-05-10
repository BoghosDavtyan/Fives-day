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
                passwordObject.associatedObject.SetActive(true);
                Debug.Log("Correct password");
                return;
            }
        }

        Debug.Log("Incorrect password.");
    }

    [System.Serializable]
    public class PasswordObject
    {
        public string password;
        public GameObject associatedObject;
    }
}