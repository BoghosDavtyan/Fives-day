using UnityEngine;
using Michsky.MUIP;

public class QuizManager : MonoBehaviour
{
    [SerializeField] private ButtonManager incorrectAnswer1;
    [SerializeField] private ButtonManager incorrectAnswer2;
    [SerializeField] private ButtonManager incorrectAnswer3;
    [SerializeField] private ButtonManager correctAnswer;

    void Start()
    {
        SetupQuiz("Incorrect 1", "Incorrect 2", "Incorrect 3", "Correct");

        incorrectAnswer1.onClick.AddListener(() => CheckAnswer(incorrectAnswer1.buttonText));
        incorrectAnswer2.onClick.AddListener(() => CheckAnswer(incorrectAnswer2.buttonText));
        incorrectAnswer3.onClick.AddListener(() => CheckAnswer(incorrectAnswer3.buttonText));
        correctAnswer.onClick.AddListener(() => CheckAnswer(correctAnswer.buttonText));
    }

    private void SetupQuiz(string ans1, string ans2, string ans3, string correctAns)
    {
        incorrectAnswer1.SetText(ans1);
        incorrectAnswer2.SetText(ans2);
        incorrectAnswer3.SetText(ans3);
        correctAnswer.SetText(correctAns);
    }

    private void CheckAnswer(string answer)
    {
        if (answer == correctAnswer.buttonText)
        {
            Debug.Log("Correct!");
        }
        else
        {
            Debug.Log("Incorrect!");
        }
    }
}
