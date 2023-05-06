using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Michsky.MUIP;

public class Startup : MonoBehaviour
{
    [SerializeField] private ModalWindowManager myModalWindow; // Your window variable
    private const string FirstLaunchKey = "FirstLaunch";

    void Start()
    {
        InitializeGame();
    }

    void InitializeGame()
    {
        // Set up your game initialization logic here

        // Check if this is the first launch
        if (PlayerPrefs.GetInt(FirstLaunchKey, 1) == 1)
        {
            myModalWindow.Open(); // Open window

            // Set PlayerPrefs key to indicate that the game has been launched before
            PlayerPrefs.SetInt(FirstLaunchKey, 0);
            PlayerPrefs.Save();
        }
    }
}