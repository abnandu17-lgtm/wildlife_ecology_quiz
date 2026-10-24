import json
import random
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Wildlife Ecology Quiz",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_PATH = Path(__file__).with_name("questions.json")
with DATA_PATH.open("r", encoding="utf-8") as f:
    ALL_QUESTIONS = json.load(f)

st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #f5fbf5 0%, #ffffff 38%); }
    .block-container { max-width: 850px; padding-top: 1.5rem; padding-bottom: 3rem; }
    .hero { padding: 1.25rem 1.4rem; border-radius: 20px; background: #173f35; color: white; margin-bottom: 1rem; }
    .hero h1 { color: white; margin: 0; font-size: 2rem; }
    .hero p { color: #d9eee4; margin: .4rem 0 0 0; }
    .question-card { border: 1px solid #dce8df; border-radius: 18px; padding: 1.15rem 1.2rem; background: white; margin: .8rem 0; }
    .muted { color: #61736a; font-size: .92rem; }
    div.stButton > button { border-radius: 12px; min-height: 2.8rem; font-weight: 600; }
    [data-testid="stRadio"] label { border-radius: 10px; }
</style>
<div class="hero">
  <h1>🌿 Wildlife Ecology Quiz</h1>
  <p>12 weekly assignments · 120 MCQs · Instant feedback</p>
</div>
""", unsafe_allow_html=True)

st.write("Choose how you want to practise. The correct options are taken from the bolded answers in your assignment PDFs.")

mode = st.radio(
    "Quiz mode",
    ["Week-wise practice", "Sequential quiz (Week 1–12)", "Random quiz"],
    horizontal=False,
    key="mode_selector",
)
week = None
if mode == "Week-wise practice":
    week = st.selectbox("Select a week", list(range(1, 13)), format_func=lambda x: f"Week {x}", key="week_selector")

config_signature = f"{mode}|{week if week is not None else 'all'}"
if st.session_state.get("config_signature") != config_signature:
    for key in ["quiz_questions", "answers", "current_index", "finished"]:
        st.session_state.pop(key, None)
    st.session_state["config_signature"] = config_signature
    if mode == "Week-wise practice":
        selected = [q for q in ALL_QUESTIONS if q["week"] == week]
    else:
        selected = list(ALL_QUESTIONS)
    if mode == "Random quiz":
        random.shuffle(selected)
    st.session_state["quiz_questions"] = selected
    st.session_state["answers"] = {}
    st.session_state["current_index"] = 0
    st.session_state["finished"] = False

questions = st.session_state["quiz_questions"]
answers = st.session_state["answers"]
total = len(questions)
idx = st.session_state["current_index"]

def option_text(question, label):
    return next((o["text"] for o in question["options"] if o["label"] == label), label)

def finish_quiz():
    st.session_state["finished"] = True

if st.session_state["finished"] or idx >= total:
    finish_quiz()
    correct_count = sum(
        1 for i, q in enumerate(questions)
        if answers.get(i) == q["answer"]
    )
    attempted = len(answers)
    percent = round((correct_count / total) * 100) if total else 0
    st.success("Quiz completed! 🎉")
    c1, c2, c3 = st.columns(3)
    c1.metric("Score", f"{correct_count}/{total}")
    c2.metric("Percentage", f"{percent}%")
    c3.metric("Incorrect", total - correct_count)
    st.progress(correct_count / total if total else 0)
    if correct_count == total:
        st.balloons()
        st.markdown("### Excellent work — all answers are correct!")
    wrong = [(i, q) for i, q in enumerate(questions) if answers.get(i) != q["answer"]]
    if wrong:
        st.markdown("### Review incorrect answers")
        for original_i, q in wrong:
            your = answers.get(original_i, "Not answered")
            your_text = option_text(q, your) if your != "Not answered" else "Not answered"
            correct_text = option_text(q, q["answer"])
            with st.expander(f"Week {q['week']} · Question {q['number']}"):
                st.write(q["question"])
                st.markdown(f"**Your answer:** {your_text}")
                st.markdown(f"**Correct answer ({q['answer'].upper()}):** {correct_text}")
    else:
        st.info("No incorrect answers to review.")
    if st.button("🔄 Restart this quiz", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("choice_") or key in ["quiz_questions", "answers", "current_index", "finished", "config_signature"]:
                st.session_state.pop(key, None)
        st.rerun()
else:
    q = questions[idx]
    progress = idx / total
    st.progress(progress)
    left, right = st.columns([2, 1])
    left.markdown(f"**Question {idx + 1} of {total}**")
    right.markdown(f"<div style='text-align:right' class='muted'>Week {q['week']} · Q{q['number']}</div>", unsafe_allow_html=True)
    st.markdown("<div class='question-card'>", unsafe_allow_html=True)
    st.markdown(f"### {q['question']}")
    st.markdown("</div>", unsafe_allow_html=True)

    choices = [f"{o['label'].upper()}. {o['text']}" for o in q["options"]]
    label_lookup = {f"{o['label'].upper()}. {o['text']}": o["label"] for o in q["options"]}
    stored_answer = answers.get(idx)
    selected_default = next((choice for choice, lab in label_lookup.items() if lab == stored_answer), None)
    radio_key = f"choice_{config_signature}_{idx}"
    if radio_key not in st.session_state and selected_default is not None:
        st.session_state[radio_key] = selected_default

    chosen = st.radio(
        "Choose one answer:",
        choices,
        index=choices.index(selected_default) if selected_default in choices else None,
        key=radio_key,
        disabled=stored_answer is not None,
    )

    if stored_answer is None:
        if st.button("Submit answer", type="primary", use_container_width=True, disabled=chosen is None):
            answers[idx] = label_lookup[chosen]
            st.session_state["answers"] = answers
            st.rerun()
    else:
        if stored_answer == q["answer"]:
            st.success("Correct! ✅")
        else:
            st.error("Not quite. ❌")
        st.info(f"Correct answer: **{q['answer'].upper()}. {option_text(q, q['answer'])}**")
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"Correct so far: {sum(1 for i, item in enumerate(questions[:idx+1]) if answers.get(i) == item['answer'])}")
        with col2:
            st.caption(f"Questions left: {total - idx - 1}")
        if st.button("Next question →" if idx < total - 1 else "See final result", type="primary", use_container_width=True):
            st.session_state["current_index"] += 1
            if st.session_state["current_index"] >= total:
                st.session_state["finished"] = True
            st.rerun()

st.markdown("---")
st.caption("Practice tool built from your 12 Wildlife Ecology assignment PDFs. Each week contains 10 questions.")
