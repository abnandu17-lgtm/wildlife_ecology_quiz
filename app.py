import json
import random
from pathlib import Path

import streamlit as st


# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="Wildlife Ecology Quiz",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# SIMPLE DARK UI
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background-color: #171717;
        color: #eeeeee;
    }

    h1, h2, h3, p, label {
        color: #eeeeee !important;
    }

    div.stButton > button {
        background-color: #303030;
        color: #eeeeee;
        border: 1px solid #555555;
        border-radius: 5px;
    }

    div.stButton > button:hover {
        background-color: #414141;
        color: #ffffff;
        border-color: #777777;
    }

    div[data-baseweb="select"] > div {
        background-color: #252525;
        color: #eeeeee;
    }

    div[role="radiogroup"] label {
        color: #eeeeee !important;
    }

    hr {
        border-color: #444444;
    }

    #MainMenu, footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# LOAD QUESTIONS
# --------------------------------------------------

file_path = Path(__file__).parent / "questions.json"

try:
    with open(file_path, "r", encoding="utf-8") as file:
        all_questions = json.load(file)
except FileNotFoundError:
    st.error("questions.json was not found in the app folder.")
    st.stop()
except json.JSONDecodeError:
    st.error("questions.json contains invalid JSON.")
    st.stop()

if not isinstance(all_questions, list) or not all_questions:
    st.error("No questions were found in questions.json.")
    st.stop()


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "quiz_run_id" not in st.session_state:
    st.session_state.quiz_run_id = 0

if "question_orders" not in st.session_state:
    st.session_state.question_orders = {}

if "option_orders" not in st.session_state:
    st.session_state.option_orders = {}


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("Wildlife Ecology Quiz")
st.write("Practice questions and check your answers instantly.")


# --------------------------------------------------
# QUIZ MODE
# --------------------------------------------------

mode = st.radio(
    "Choose quiz mode",
    [
        "Week-wise Practice",
        "Sequential Quiz",
        "Random Quiz",
    ],
    horizontal=True,
)


# --------------------------------------------------
# WEEK SELECTION
# --------------------------------------------------

selected_week = None

if mode == "Week-wise Practice":

    available_weeks = sorted(
        {
            int(q["week"])
            for q in all_questions
            if "week" in q
        }
    )

    if not available_weeks:
        st.error("No week information was found in questions.json.")
        st.stop()

    selected_week = st.selectbox(
        "Select week",
        available_weeks,
        format_func=lambda week: f"Week {week}",
    )


# --------------------------------------------------
# PREPARE BASE QUESTIONS
# --------------------------------------------------

if mode == "Week-wise Practice":

    base_questions = [
        q for q in all_questions
        if int(q.get("week", -1)) == selected_week
    ]

elif mode == "Sequential Quiz":

    base_questions = sorted(
        all_questions,
        key=lambda q: (
            int(q.get("week", 0)),
            int(q.get("number", 0)),
        ),
    )

else:
    base_questions = all_questions.copy()


if not base_questions:
    st.warning("No questions are available for this selection.")
    st.stop()


# --------------------------------------------------
# SHUFFLE SETTINGS FOR EVERY SECTION
# --------------------------------------------------

st.markdown("### Quiz Settings")

shuffle_questions = st.checkbox(
    "Shuffle questions",
    value=(mode == "Random Quiz"),
    key=f"shuffle_questions_{mode}_{selected_week}",
)

shuffle_options = st.checkbox(
    "Shuffle answer options",
    value=False,
    key=f"shuffle_options_{mode}_{selected_week}",
)


# --------------------------------------------------
# CREATE A QUIZ SESSION
# --------------------------------------------------

section_key = f"{mode}_{selected_week}"

settings = (
    shuffle_questions,
    shuffle_options,
)

current_signature = (
    section_key,
    settings,
)

if st.session_state.get("current_signature") != current_signature:

    st.session_state.quiz_run_id += 1
    run_id = st.session_state.quiz_run_id

    # Prepare question order.
    questions = base_questions.copy()

    if shuffle_questions:
        random.shuffle(questions)

    st.session_state.question_orders[section_key] = {
        "run_id": run_id,
        "questions": questions,
    }

    # Prepare a stable option order for each question.
    option_orders = {}

    for index, question in enumerate(questions):
        options = question.get("options", []).copy()

        if shuffle_options:
            random.shuffle(options)

        option_orders[index] = options

    st.session_state.option_orders[section_key] = {
        "run_id": run_id,
        "options": option_orders,
    }

    # Clear previous answers when settings change.
    for key in list(st.session_state.keys()):
        if key.startswith("answer_"):
            del st.session_state[key]

    st.session_state.current_signature = current_signature


# Use saved orders so Streamlit reruns don't reshuffle questions.
saved_question_data = st.session_state.question_orders[section_key]
questions = saved_question_data["questions"]

saved_option_data = st.session_state.option_orders[section_key]
option_orders = saved_option_data["options"]

run_id = saved_question_data["run_id"]


# --------------------------------------------------
# GENERATE A NEW ORDER BUTTON
# --------------------------------------------------

if st.button("Shuffle Again"):

    st.session_state.current_signature = None

    for key in list(st.session_state.keys()):
        if key.startswith("answer_"):
            del st.session_state[key]

    st.rerun()


# --------------------------------------------------
# QUIZ INFORMATION
# --------------------------------------------------

st.markdown("---")
st.write(f"Total questions: {len(questions)}")

if mode == "Week-wise Practice":
    st.subheader(f"Week {selected_week}")
elif mode == "Random Quiz":
    st.subheader("Random Quiz")

st.write(
    "Choose an option for each question. "
    "Feedback appears immediately. Scroll down to continue."
)


# --------------------------------------------------
# DISPLAY QUESTIONS WITH INSTANT FEEDBACK
# --------------------------------------------------

for i, question in enumerate(questions):

    st.markdown("---")
    st.markdown(f"**Question {i + 1}**")
    st.write(question["question"])

    original_options = question.get("options", [])

    if not original_options:
        st.warning("Options are missing for this question.")
        continue

    displayed_options = option_orders[i]

    correct_answer = str(
        question.get("answer", "")
    ).strip().lower()

    answer_key = f"answer_{run_id}_{i}"

    selected_option = st.radio(
        "Select your answer:",
        displayed_options,
        format_func=lambda option: (
            f"{option['label']}. {option['text']}"
        ),
        key=answer_key,
        index=None,
        label_visibility="collapsed",
    )

    if selected_option is not None:

        selected_label = str(
            selected_option.get("label", "")
        ).strip().lower()

        if selected_label == correct_answer:
            st.markdown("**Correct!**")

        else:
            st.markdown("**Incorrect.**")

            correct_option = next(
                (
                    option for option in original_options
                    if str(option.get("label", "")).strip().lower()
                    == correct_answer
                ),
                None,
            )

            if correct_option:
                st.write(
                    f"Correct answer: {correct_option['label']}. "
                    f"{correct_option['text']}"
                )
            else:
                st.write(
                    f"Correct answer: {question.get('answer', 'Not available')}"
                )


# --------------------------------------------------
# FINAL RESULTS
# --------------------------------------------------

st.markdown("---")
st.subheader("Quiz Results")

score = 0
answered = 0
unanswered = 0
incorrect_questions = []

for i, question in enumerate(questions):

    selected_option = st.session_state.get(
        f"answer_{run_id}_{i}"
    )

    if selected_option is None:
        unanswered += 1
        continue

    answered += 1

    correct_answer = str(
        question.get("answer", "")
    ).strip().lower()

    selected_label = str(
        selected_option.get("label", "")
    ).strip().lower()

    if selected_label == correct_answer:
        score += 1

    else:

        correct_option = next(
            (
                option for option in question.get("options", [])
                if str(option.get("label", "")).strip().lower()
                == correct_answer
            ),
            None,
        )

        incorrect_questions.append(
            {
                "question": question.get("question", ""),
                "your_answer": (
                    f"{selected_option.get('label', '')}. "
                    f"{selected_option.get('text', '')}"
                ),
                "correct_answer": (
                    f"{correct_option.get('label', '')}. "
                    f"{correct_option.get('text', '')}"
                    if correct_option
                    else question.get("answer", "Not available")
                ),
            }
        )

percentage = (
    score / len(questions) * 100
    if questions else 0
)

col1, col2 = st.columns(2)

with col1:
    st.metric("Score", f"{score}/{len(questions)}")

with col2:
    st.metric("Percentage", f"{percentage:.1f}%")

st.write(f"Answered: {answered}")
st.write(f"Incorrect: {len(incorrect_questions)}")
st.write(f"Unanswered: {unanswered}")


# --------------------------------------------------
# REVIEW INCORRECT ANSWERS
# --------------------------------------------------

if incorrect_questions:

    with st.expander("Review Incorrect Answers"):

        for index, item in enumerate(incorrect_questions, start=1):
            st.markdown(f"**{index}. {item['question']}**")
            st.write(f"Your answer: {item['your_answer']}")
            st.write(f"Correct answer: {item['correct_answer']}")
            st.markdown("---")
