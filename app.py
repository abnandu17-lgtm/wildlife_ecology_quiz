import json
import random
from pathlib import Path

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Wildlife Ecology Quiz",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Load questions
file_path = Path(__file__).parent / "questions.json"

with open(file_path, "r", encoding="utf-8") as file:
    all_questions = json.load(file)

# Simple styling
st.markdown("""
<style>
.stApp {
    background-color: #171717;
    color: #eeeeee;
}

.block-container {
    max-width: 780px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, p, label, li {
    color: #eeeeee;
}

div[role="radiogroup"] {
    gap: 8px;
}

div[role="radiogroup"] label {
    background-color: transparent;
    border: none;
    padding: 5px 0;
    color: #eeeeee;
}

.stButton > button {
    background-color: #303030;
    color: #eeeeee;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 8px 16px;
}

.stButton > button:hover {
    background-color: #414141;
    color: #ffffff;
    border-color: #777777;
}

div[data-baseweb="select"] > div {
    background-color: #252525;
    color: #eeeeee;
    border-color: #555555;
}

div[data-testid="stProgress"] > div {
    background-color: #303030;
}

div[data-testid="stProgress"] > div > div {
    background-color: #999999;
}

div[data-testid="stMetric"] {
    background-color: transparent;
    border: none;
}

div[data-testid="stAlert"] {
    background-color: transparent;
    border: none;
}

header[data-testid="stHeader"] {
    background-color: #171717;
}

hr {
    border-color: #444444;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# Page title
st.title("Wildlife Ecology Quiz")

st.write(
    "Practice multiple-choice questions from the "
    "12 weekly assignments."
)

# Select quiz mode
mode = st.radio(
    "Choose quiz mode",
    [
        "Week-wise practice",
        "Sequential quiz",
        "Random quiz",
    ],
)

selected_week = None

if mode == "Week-wise practice":
    selected_week = st.selectbox(
        "Select week",
        list(range(1, 13)),
        format_func=lambda x: f"Week {x}",
    )

# Prepare quiz when settings change
quiz_settings = f"{mode}-{selected_week}"

if st.session_state.get("quiz_settings") != quiz_settings:

    if mode == "Week-wise practice":
        quiz_questions = [
            q for q in all_questions
            if q["week"] == selected_week
        ]
    else:
        quiz_questions = list(all_questions)

    if mode == "Random quiz":
        random.shuffle(quiz_questions)

    st.session_state["quiz_questions"] = quiz_questions
    st.session_state["user_answers"] = {}
    st.session_state["question_index"] = 0
    st.session_state["quiz_finished"] = False
    st.session_state["quiz_settings"] = quiz_settings

questions = st.session_state["quiz_questions"]
user_answers = st.session_state["user_answers"]
total_questions = len(questions)
question_index = st.session_state["question_index"]


def get_option_text(question, label):
    for option in question["options"]:
        if option["label"] == label:
            return option["text"]
    return ""


# Results page
if st.session_state["quiz_finished"]:

    st.header("Quiz Results")

    score = sum(
        1 for i, question in enumerate(questions)
        if user_answers.get(i) == question["answer"]
    )

    incorrect = sum(
        1 for i, question in enumerate(questions)
        if i in user_answers
        and user_answers[i] != question["answer"]
    )

    unanswered = total_questions - len(user_answers)

    percentage = (
        round(score * 100 / total_questions)
        if total_questions else 0
    )

    st.progress(score / total_questions if total_questions else 0)

    st.metric("Final score", f"{score} / {total_questions}")
    st.write(f"Percentage: {percentage}%")
    st.write(f"Incorrect answers: {incorrect}")
    st.write(f"Unanswered questions: {unanswered}")

    st.subheader("Review incorrect answers")

    wrong_questions = [
        (i, question)
        for i, question in enumerate(questions)
        if user_answers.get(i) != question["answer"]
    ]

    if wrong_questions:
        for i, question in wrong_questions:

            with st.expander(
                f"Week {question['week']} - "
                f"Question {question['number']}"
            ):
                st.write(question["question"])

                selected = user_answers.get(i)

                if selected is None:
                    st.write("Your answer: Not answered")
                else:
                    st.write(
                        f"Your answer: {selected.upper()}. "
                        f"{get_option_text(question, selected)}"
                    )

                correct = question["answer"]

                st.write(
                    f"Correct answer: {correct.upper()}. "
                    f"{get_option_text(question, correct)}"
                )
    else:
        st.write("All answers are correct.")

    if st.button("Restart quiz", use_container_width=True):

        keys_to_clear = [
            "quiz_questions",
            "user_answers",
            "question_index",
            "quiz_finished",
            "quiz_settings",
        ]

        for key in keys_to_clear:
            st.session_state.pop(key, None)

        st.rerun()

# Question page
else:

    question = questions[question_index]

    st.progress(
        (question_index + 1) / total_questions
        if total_questions else 0
    )

    st.write(
        f"Question {question_index + 1} "
        f"of {total_questions}"
    )

    st.caption(
        f"Week {question['week']} - "
        f"Question {question['number']}"
    )

    st.divider()

    st.subheader(question["question"])

    options = question["options"]

    option_labels = [
        f"{option['label'].upper()}. {option['text']}"
        for option in options
    ]

    option_lookup = {
        f"{option['label'].upper()}. {option['text']}":
        option["label"]
        for option in options
    }

    previous_answer = user_answers.get(question_index)

    # Show submitted answer and feedback
    if previous_answer is not None:

        previous_choice = next(
            (
                label for label in option_labels
                if option_lookup[label] == previous_answer
            ),
            None,
        )

        st.radio(
            "Choose your answer",
            option_labels,
            index=(
                option_labels.index(previous_choice)
                if previous_choice in option_labels
                else None
            ),
            disabled=True,
            key=f"submitted_{quiz_settings}_{question_index}",
        )

        correct_answer = question["answer"]

        if previous_answer == correct_answer:
            st.write("Result: Correct")
        else:
            st.write("Result: Incorrect")

        st.write(
            f"Correct answer: {correct_answer.upper()}. "
            f"{get_option_text(question, correct_answer)}"
        )

        if st.button(
            "Next question"
            if question_index < total_questions - 1
            else "View results",
            use_container_width=True,
        ):

            st.session_state["question_index"] += 1

            if (
                st.session_state["question_index"]
                >= total_questions
            ):
                st.session_state["quiz_finished"] = True

            st.rerun()

    # Show unanswered question
    else:

        choice = st.radio(
            "Choose your answer",
            option_labels,
            index=None,
            key=f"choice_{quiz_settings}_{question_index}",
        )

        if st.button(
            "Submit answer",
            disabled=choice is None,
            use_container_width=True,
        ):

            user_answers[question_index] = option_lookup[choice]
            st.session_state["user_answers"] = user_answers
            st.rerun()

st.divider()
st.caption("Wildlife Ecology - Weekly Assignment Practice")
