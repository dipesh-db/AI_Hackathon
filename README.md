# Smart Onboarding & Compliance AI Copilot

An AI-powered SaaS solution for staffing agencies to automate onboarding and compliance document verification, reducing manual effort, speeding processing, and improving regulatory adherence.

---

## 🚀 How to Run Locally

### 1. Clone this repository, create & activate virtual environment, and install dependencies

`## 🛠️ Local Setup Instructions

Follow these steps to run the app locally.

### 1. 📁 Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
2. 🐍 (Optional) Create a Virtual Environment
Helps keep dependencies isolated.

bash
Copy
Edit
python -m venv env
source env/bin/activate          # For Linux/macOS
# OR
env\Scripts\activate             # For Windows
3. 📦 Install Dependencies
Make sure you have Python ≥3.9 installed.

bash
Copy
Edit
pip install -r requirements.txt
4. 🗝️ Set Environment Variables (if using .env)
If your app needs API keys (e.g., OpenAI), create a .env file in the root directory:

bash
Copy
Edit
touch .env                     # or create manually in any editor
Then add your secrets like this:

ini
Copy
Edit
OPENAI_API_KEY=your-key-here
GROQ_API_KEY=your-groq-key
Make sure .env is listed in .gitignore to avoid pushing secrets.

5. ▶️ Run the Streamlit App
Start the frontend locally:

bash
Copy
Edit
streamlit run main.py
The app should open automatically in your browser at http://localhost:8501

