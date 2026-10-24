if selected is None:
                    st.write("Your answer: Not answered")
                else:
                    st.write(
                        "Your answer: "
                        f"{selected.upper()}. "
                        f"{option_text(q, selected)}"
                    )

                correct_label = q["answer"]
                st.write(
                    "Correct answer: "
                    f"{correct_label.upper()}. "
                    f"{option_text(q, correct_label)}"
                )
    else:
        st.write("All answers are correct.")

    if st.button("Restart quiz"):
        for key in [
            "questions", "answers", "index",
            "submitted", "finished", "signature",
        ]:
            st.session_state.pop(key, None)
        st.rerun()

# Question page
else:
    question = questions[index]

    st.progress((index + 1) / total if total else 0)

    st.write(f"Question {index + 1} of {total}")
    st.write(
        f"Week {question['week']} - "
        f"Question {question['number']}"
    )

    st.divider()

    st.subheader(question["question"])

    options = question["options"]

    labels = [
        f"{o['label'].upper()}. {o['text']}"
        for o in options
    ]

    label_map = {
        f"{o['label'].upper()}. {o['text']}": o["label"]
        for o in options
    }

    saved_answer = answers.get(index)

    if saved_answer is not None:
        selected_label = next(
            (
                label for label in labels
                if label_map[label] == saved_answer
            ),
            None,
        )
        st.radio(
            "Choose one answer",
            labels,
            index=(
                labels.index(selected_label)
                if selected_label in labels else None
            ),
            disabled=True,
            key=f"answered_{signature}_{index}",
        )

        correct_label = question["answer"]

        if saved_answer == correct_label:
            st.success("Correct answer.")
        else:
            st.error("Incorrect answer.")

        st.write(
            "Correct answer: "
            f"{correct_label.upper()}. "
            f"{option_text(question, correct_label)}"
        )

        if st.button(
            "Next question" if index < total - 1
            else "View results",
            use_container_width=True,
        ):
            st.session_state["index"] += 1

            if st.session_state["index"] >= total:
                st.session_state["finished"] = True

            st.rerun()

    else:
        selected = st.radio(
            "Choose one answer",
            labels,
            index=None,
            key=f"choice_{signature}_{index}",
        )

        if st.button(
            "Submit answer",
            disabled=selected is None,
            use_container_width=True,
        ):
            answers[index] = label_map[selected]
            st.session_state["answers"] = answers
            st.rerun()

st.divider()
st.caption("Wildlife Ecology weekly assignment practice")
