using UnityEngine;
using Michsky.MUIP;

public class QuizManager : MonoBehaviour
{
    [SerializeField] private ButtonManager button1;
    [SerializeField] private ButtonManager button2;
    [SerializeField] private ButtonManager button3;
    [SerializeField] private ButtonManager button4;

    [SerializeField] private GameObject incorrectAnswer1;
    [SerializeField] private GameObject incorrectAnswer2;
    [SerializeField] private GameObject incorrectAnswer3;
    [SerializeField] private GameObject correctAnswer;

    private string correctAnswerText;

    void Start()
    {
        SetupQuiz(incorrectAnswer1, incorrectAnswer2, incorrectAnswer3, correctAnswer);

        button1.onClick.AddListener(() => CheckAnswer(button1.buttonText));
        button2.onClick.AddListener(() => CheckAnswer(button2.buttonText));
        button3.onClick.AddListener(() => CheckAnswer(button3.buttonText));
        button4.onClick.AddListener(() => CheckAnswer(button4.buttonText));
    }

    private void SetupQuiz(GameObject incAns1, GameObject incAns2, GameObject incAns3, GameObject corrAns)
    {
        // Randomly assign answer GameObjects to buttons
        GameObject[] answers = { incAns1, incAns2, incAns3, corrAns };
        System.Random rand = new System.Random();
        for (int i = 0; i < 4; i++)
        {
            int index = rand.Next(0, answers.Length - i);
            ButtonManager button = GetButtonByIndex(i + 1);
            button.SetText(answers[index].name);

            if (answers[index] == corrAns)
            {
                correctAnswerText = answers[index].name;
            }

            // Remove assigned answer from the array
            answers[index] = answers[answers.Length - 1 - i];
        }
    }

    private ButtonManager GetButtonByIndex(int index)
    {
        switch (index)
        {
            case 1:
                return button1;
            case 2:
                return button2;
            case 3:
                return button3;
            case 4:
                return button4;
            default:
                return null;
        }
    }

    private void CheckAnswer(string answer)
    {
        if (answer == correctAnswerText)
        {
            Debug.Log("Correct!");
        }
        else
        {
            Debug.Log("Incorrect!");
        }
    }
}
