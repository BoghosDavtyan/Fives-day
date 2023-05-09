using UnityEngine;
using UnityEngine.UI;

public class QuizController : MonoBehaviour
{
    public Text questionText;
    public Button[] optionButtons;
    public int correctOptionIndex;

    // Your custom scripts for correct and incorrect answers
    public MonoBehaviour correctScript;
    public MonoBehaviour incorrectScript;

    private void Start()
    {
        // Set question text and options here

        // Add listener to each button
        for (int i = 0; i < optionButtons.Length; i++)
        {
            int currentOptionIndex = i; // To prevent closure issues with lambdas
            optionButtons[i].onClick.AddListener(() => OnOptionSelected(currentOptionIndex));
        }
    }

    private void OnOptionSelected(int selectedOption)
    {
        if (selectedOption == correctOptionIndex)
        {
            correctScript.enabled = true;
        }
        else
        {
            incorrectScript.enabled = true;
        }
    }
}
