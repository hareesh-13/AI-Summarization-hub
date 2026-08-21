# AI Summarization Hub 🚀

An advanced, highly customizable AI-powered summarization tool built with **Streamlit** and **Google Gemini**. It allows you to generate rich, professional summaries from a variety of sources with just a single click.

## ✨ Features

- **🎬 YouTube Summarization:** Instantly extract and summarize transcripts from any YouTube video.
- **🌐 Website Summarization:** Scrape and summarize public articles, blog posts, and webpages.
- **📝 Text Summarization:** Paste any raw text (emails, reports, social media posts) for immediate summarization.
- **📄 Document Summarization:** Upload and summarize multiple file formats including `PDF`, `DOCX`, `PPTX`, `TXT`, and `CSV`.
- **⚙️ Deep Customization:** Control the AI's output by adjusting the **Summary Style** (Professional, Academic, Business, Beginner), **Summary Length** (Short, Medium, Detailed), or by providing your own **Custom Instructions**.
- **🧠 Map-Reduce Architecture:** Automatically handles extremely long documents and videos by splitting them into chunks and intelligently combining the summaries, bypassing standard AI context limits.

## 🛠️ Technology Stack

- **Frontend:** Streamlit, Custom CSS
- **AI/LLM:** Google Gemini, LangChain
- **Processing:** `youtube-transcript-api`, `beautifulsoup4`, `pdfplumber`, `python-docx`, `python-pptx`, `pandas`

## 🚀 Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API Key:**
   - Create a `.env` file in the root directory.
   - Add your Google Gemini API key:
     ```env
     GOOGLE_API_KEY="your_api_key_here"
     ```

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## ☁️ Free Deployment (Streamlit Community Cloud)

This project is perfectly configured to be deployed for free on Streamlit Community Cloud.

1. Push your code to a GitHub repository (your `.env` file is safely ignored via `.gitignore`).
2. Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New app** and select your repository and branch.
4. Set the Main file path to `app.py`.
5. **Crucial Step:** Before clicking Deploy, click **Advanced settings...** and paste your API key into the **Secrets** box like this:
   ```toml
   GOOGLE_API_KEY = "your_actual_api_key_here"
   ```
6. Click **Deploy** and your app will be live!

## ⚠️ Important Note on API Limits
If you are using the Free Tier of the Gemini API, you are limited to 15 requests per minute and 1,500 requests per day. For very long documents or videos, the app uses a Map-Reduce strategy which sends multiple requests under the hood. If you hit an error, simply wait a minute for your quota to refresh.
