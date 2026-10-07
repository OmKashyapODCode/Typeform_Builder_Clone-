<div align="center">
  
  # 🧩 Typeform Builder Clone
  
  <p align="center">
    A full-stack, production-quality form builder that feels like a polished SaaS product. 
    Built as an SDE Fullstack Assignment.
  </p>

  <p align="center">
    <a href="https://typeform-builder-clone.vercel.app" target="_blank"><strong>🌐 View Live Frontend</strong></a> ·
    <a href="https://typeform-builder-clone.onrender.com/api/docs" target="_blank"><strong>⚙️ View Live API Docs</strong></a>
  </p>

</div>

---

## ✨ Features

### 🛠️ Creator Dashboard & Builder
- **Dashboard:** Create, edit, duplicate, publish, unpublish, and delete forms.
- **Drag-and-Drop Builder:** Reorder questions with visual feedback using `dnd-kit`.
- **Question Types:** Short Text, Long Text, Multiple Choice, Dropdown, Email, Number, Yes/No, Rating, and **File Upload**.
- **Custom Themes:** Set a primary color, background color, and font per form. 
- **Logic Jumps:** Conditional branching (e.g., "If answer is Yes → Jump to Q5").

### 🗣️ Respondent Experience
- **One-Question-at-a-Time UX:** Beautiful, distraction-free conversational UI.
- **Animations:** Smooth page transitions using Framer Motion.
- **Keyboard Navigation:** Press `Enter` to seamlessly advance through questions.
- **Adaptive Contrast:** Automatically ensures text is visible against custom background colors regardless of system dark mode.

### 📊 Analytics & Responses
- **Response Dashboard:** View submissions, completion status, and timestamps.
- **Completion Tracking:** Tracks "partial" vs "complete" responses and calculates drop-off rates.
- **Data Export:** One-click download of all form responses as a formatted `.csv` file.

---

## 💻 Tech Stack

**Frontend**
- Next.js 16 (App Router)
- React 19 + TypeScript
- Tailwind CSS
- shadcn/ui + Radix UI
- Framer Motion (Animations)
- dnd-kit (Drag and Drop)

**Backend**
- FastAPI (Python 3.12)
- SQLite (Database)
- SQLAlchemy 2.0 (ORM)
- Pydantic v2 (Data Validation)
- Pytest (Automated Testing)

**Deployment**
- Vercel (Frontend)
- Render (Backend)

---

## 🚀 Local Development

### 1. Clone the repository
```bash
git clone https://github.com/OmKashyapODCode/Typeform_Builder_Clone-.git
cd Typeform_Builder_Clone-
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed the database with demo data (3 forms, 25 responses)
python seed.py

# Run the API
uvicorn app.main:app --reload --port 8000
```
API runs at: `http://localhost:8000`

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env.local

# Run the development server
npm run dev
```
Frontend runs at: `http://localhost:3000`

---

## 🧪 Testing

The backend includes a comprehensive test suite (22 tests) covering CRUD operations, public access, response submission, and analytics.

```bash
cd backend
python -m pytest tests/ -v
```

---

## 🏗️ Architecture Decisions

- **Two-ID System:** Forms use an internal UUID for creator APIs and a separate `public_id` for shareable URLs, ensuring safe routing.
- **JSON Settings Schema:** Question-specific configurations (choices, max_rating, logic jumps) are stored in a flexible JSON column, keeping the relational schema clean.
- **Client-Side Logic:** Logic jumps are evaluated on the frontend to provide instant, zero-latency transitions for respondents.
- **Test Isolation:** Pytest utilizes an in-memory SQLite `StaticPool` to ensure complete state isolation between test runs without file locking.

<div align="center">
  <i>Built with ❤️ for the SDE Fullstack Assignment</i>
</div>
