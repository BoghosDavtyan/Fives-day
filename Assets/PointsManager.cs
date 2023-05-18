using UnityEngine;
using TMPro;
using Michsky.MUIP;
using System.Collections.Generic;

public class PointsManager : MonoBehaviour
{
    public TextMeshProUGUI pointsText;
    public ButtonManager[] singlePointButtons;
    public ButtonManager[] fivePointButtons;
    private int points;

    public static PointsManager Instance { get; private set; }

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
        }
        else
        {
            Destroy(gameObject);
        }
    }

    private void Start()
    {
        points = 0;
        UpdatePointsText();
        RegisterButtonListeners();
    }

    private void UpdatePointsText()
    {
        if (pointsText != null)
        {
            pointsText.text = points.ToString();
        }
    }

    public void AddPoints(int amount)
    {
        points += amount;
        UpdatePointsText();
    }

    private void RegisterButtonListeners()
    {
        foreach (var button in singlePointButtons)
        {
            button.onClick.AddListener(IncrementPoints);
        }

        foreach (var button in fivePointButtons)
        {
            button.onClick.AddListener(IncrementFivePoints);
        }
    }

    private void IncrementPoints()
    {
        AddPoints(1);
    }

    private void IncrementFivePoints()
    {
        AddPoints(5);
    }
}