# Wildlife Ecology Quiz Website

A mobile-friendly Streamlit quiz app built from the 12 uploaded Wildlife Ecology weekly assignment PDFs.

## Features
- Week-wise practice (10 questions per week)
- Sequential quiz (Week 1 through Week 12; 120 questions)
- Random quiz (all 120 questions shuffled)
- Instant correct/incorrect feedback after submission
- Correct answer reveal
- Final score and percentage
- Review incorrect answers

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the website:
   ```bash
   streamlit run app.py
   ```

## Deploy free on Streamlit Community Cloud
1. Create a GitHub repository and upload `app.py`, `questions.json`, and `requirements.txt`.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Choose **Create app**, select the repository and branch, and set the main file path to `app.py`.
4. Deploy.

## Answer key source
Correct answers are detected from the bold option formatting in the uploaded PDFs. Questions/options are transcribed from those PDFs; obvious blanks in the prompt text caused by formatting are shown as `_____`.
