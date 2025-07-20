# Smart Onboarding & Compliance AI Copilot

An AI-powered SaaS solution for staffing agencies to automate onboarding and compliance document verification, reducing manual effort, speeding processing, and improving regulatory adherence.

---

## 🛠️ Local Setup Instructions

Follow these steps to run the app locally.

### 1. 📁 Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
2. 🐍 Create a Virtual Environment (Optional but Recommended)
Helps keep dependencies isolated.
bashpython -m venv env
source env/bin/activate          # For Linux/macOS
# OR
env\Scripts\activate             # For Windows
3. 📦 Install Dependencies
Make sure you have Python ≥3.9 installed.
bashpip install -r requirements.txt
4. 🗝️ Set Environment Variables
If your app needs API keys (e.g., OpenAI), create a .env file in the root directory:
bashtouch .env                     # or create manually in any editor
Then add your secrets like this:
iniOPENAI_API_KEY=your-key-here
GROQ_API_KEY=your-groq-key
Important: Make sure .env is listed in .gitignore to avoid pushing secrets to your repository.
5. ▶️ Run the Streamlit App
Start the frontend locally:
bashstreamlit run main.py
The app should open automatically in your browser at http://localhost:8501

🔧 Troubleshooting
If you encounter any issues:

Ensure Python 3.9+ is installed
Check that all dependencies are installed correctly
Verify your API keys are set properly in the .env file