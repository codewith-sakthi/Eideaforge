# 🚀 Eideaforge

> **A Comprehensive Campus Innovation & Pitching Competition Platform**

Eideaforge empowers students to transform their innovative ideas into impactful ventures through team collaboration, multi-round pitch competitions, and rigorous rubric-based faculty evaluation.

---

## 🏗️ Architecture & Project Structure

```
EIDEAFORGE/
├── frontend/             # Clean HTML5 + CSS3 + Vanilla ES6 JS (Modular REST Consumer)
│   ├── index.html        # Public Portal
│   ├── login.html        # Unified Role Login & Auth
│   ├── competitions.html # Public Competitions Discovery
│   ├── student/          # Student Portal (Ideas, Teams, Submissions, Results)
│   ├── admin/            # Admin Command Center (Students, Rubrics, Competitions)
│   ├── evaluator/        # Evaluator Scoring Workspace
│   ├── css/              # Design System, Themes & Glassmorphism Styles
│   └── js/               # API Client, Auth State & Role Controllers
│
├── backend/              # Flask 3.0 REST API (Modular Architecture)
│   ├── app.py            # Application Factory & Startup
│   ├── config.py         # App Configuration & Security
│   ├── routes/           # Blueprints for all REST API endpoints
│   ├── models/           # MySQL Database Access Layer
│   ├── services/         # Business Logic Layer
│   ├── middleware/       # JWT Auth, Role RBAC & Upload Handlers
│   └── utils/            # Password Hashing, Token Generators & Validators
│
├── database/             # Database Schema & Seed Data
│   ├── schema.sql        # Full MySQL DDL
│   ├── seed.sql          # Sample Competitions, Teams & Users
│   └── README.md
│
└── docs/                 # Platform Documentation & Specifications
```

---

## ⚡ Quick Start

### 1. Database Setup
```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env .env.local  # Update your MySQL connection details
python app.py
```

### 3. Frontend Portal
Serve the `frontend/` directory using any static web server (e.g. Live Server in VS Code, `npx serve frontend`, or Python's `python -m http.server 8080 -d frontend`).

---

## 👥 Demo Credentials

| Role | Email | Password |
|---|---|---|
| 👑 **Administrator** | `admin@eideaforge.edu` | `Admin@1234` |
| 🎓 **Student** | `student1@eideaforge.edu` | `Student@123` |
| 🧑‍⚖️ **Evaluator** | `evaluator1@eideaforge.edu` | `Evaluator@123` |

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
