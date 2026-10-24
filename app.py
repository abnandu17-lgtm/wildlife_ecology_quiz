label_lookup = {
        f"{option['label'].upper()}. {option['text']}":
        option["label"]
        for option in question["options"]
    }

    stored_answer = answers.get(idx)

    radio_key = f"choice_{config_signature}_{idx}"

    selected_default = next(
        (
            choice
            for choice, label in label_lookup.items()
            if label == stored_answer
        ),
        None,
    )

    if (
        radio_key not in st.session_state
        and selected_default is not None
    ):
        st.session_state[radio_key] = selected_default

    chosen = st.radio(
        "Choose one answer",
        choices,
        index=(
            choices.index(selected_default)
            if selected_default in choices
            else None
        ),
        key=radio_key,
        disabled=stored_answer is not None,
    )

    # Submit answer
    if stored_answer is None:

        if st.button(
            "Submit answer",
            type="primary",
            use_container_width=True,
            disabled=chosen is None,
        ):
            answers[idx] = label_lookup[chosen]
            st.session_state["answers"] = answers
            st.rerun()

    # Instant feedback after submission
    else:

        correct_label = question["answer"]
        correct_text = get_option_text(question, correct_label)

        if stored_answer == correct_label:
            st.success("Correct! ✅")
        else:
            st.error("Incorrect. ❌")

        st.info(
            f"Correct answer: {correct_label.upper()}. {correct_text}"
        )

        correct_so_far = sum(
            1
            for i, item in enumerate(questions[:idx + 1])
            if answers.get(i) == item["answer"]
        )

        col1, col2 = st.columns(2)

        col1.caption(f"Correct so far: {correct_so_far}")
        col2.caption(f"Questions remaining: {total - idx - 1}")

        button_label = (
            "Next question →"
            if idx < total - 1
            else "View results"
        )

        if st.button(
            button_label,
            type="primary",
            use_container_width=True,
        ):

            st.session_state["current_index"] += 1

            if st.session_state["current_index"] >= total:
                st.session_state["finished"] = True

            st.rerun()

# -------------------- FOOTER --------------------

st.markdown("---")

st.caption("Wildlife Ecology · Weekly assignment practice")
