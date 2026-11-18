# Trekking Management System (MAD II)

A full-stack, role-based web application for discovering, booking, and managing trekking expeditions. Built with **Vue 3 (Vite)** on the frontend, **Flask** on the backend, **SQLite** for relational storage, **Redis** for caching, and **Celery** for scheduled and asynchronous background tasks.

Developed as a capstone project for **Modern Application Development II (MAD II)**.

---

## 📌 Table of Contents

- [Features & Role Capabilities](#-features--role-capabilities)
  - [1. Trekker (User)](#1-trekker-user)
  - [2. Staff (Trek Leader)](#2-staff-trek-leader)
  - [3. Administrator](#3-administrator)
- [System Architecture & Tech Stack](#-system-architecture--tech-stack)
- [Directory Structure](#-directory-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
  - [1. Backend Setup](#1-backend-setup)
  - [2. Frontend Setup](#2-frontend-setup)
  - [3. Redis & Celery Setup (Async & Scheduled Jobs)](#3-redis--celery-setup-async--scheduled-jobs)
- [Default Admin Credentials](#-default-admin-credentials)
- [API Endpoints Overview](#-api-endpoints-overview)
- [Environment Variables](#-environment-variables)

---

## 🚀 Features & Role Capabilities

The application implements a secure, token-based Role-Based Access Control (RBAC) system with three distinct roles:

### 1. Trekker (User)
- **Account Management:** User registration, JWT login, profile view/edit, and password change.
- **Trek Discovery:** Search and browse upcoming treks with real-time slot availability, location, duration, and difficulty filters.
- **Booking Management:** 
  - Instant trek booking with automatic slot decrement.
  - View current bookings and cancel active bookings (re-credits available slot).
- **Booking History & CSV Export:** 
  - Detailed historical log of completed and cancelled treks.
  - Asynchronous background CSV export powered by Celery with download capabilities.
- **In-App Notifications:** Automated alerts for booking status and daily start reminders.

### 2. Staff (Trek Leader)
- **Dedicated Dashboard:** Overview of treks assigned to the staff member.
- **Participant Manifest:** Real-time participant roster with contact information for assigned treks.
- **Status Management:** Ability to update trek expedition status (e.g., *Open*, *In Progress*, *Completed*).

### 3. Administrator
- **Executive Analytics:** High-level metrics for total treks, active bookings, user distribution, and slot utilization.
- **Trek Operations:** Full CRUD operations for treks (Name, Location, Dates, Duration, Difficulty, Max Slots).
- **Staff Administration:** Create staff credentials, manage profiles (experience, specialization), and assign staff members to specific treks.
- **User Governance:** Inspect registered users and blacklist/un-blacklist accounts.
- **Booking Oversight:** Global view of all platform bookings with administrative cancellation rights.
- **Automated Monthly Reporting:** Scheduled report generation summarizing platform performance.

---

## 🛠 System Architecture & Tech Stack

```
┌────────────────────────────────────────────────────────┐
│                   Frontend (Vue 3 + Vite)              │
│      Pinia Store  •  Vue Router  •  Bootstrap 5        │
└───────────────────────────┬────────────────────────────┘
                            │ REST API (JSON / JWT)
┌───────────────────────────▼────────────────────────────┐
│                  Backend (Flask REST API)              │
│       Flask-JWT-Extended  •  Flask-SQLAlchemy (ORM)    │
└──────────────┬────────────────────────────┬────────────┘
               │                            │
       ┌───────▼───────┐            ┌───────▼────────┐
       │ SQLite (DB)   │            │ Redis Server   │
       │ (trek.db)     │            │ (Cache + Queue)│
       └───────────────┘            └───────┬────────┘
                                            │
                                    ┌───────▼────────┐
                                    │ Celery Worker  │
                                    │ & Celery Beat  │
                                    └────────────────┘
```

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Vue.js 3 (Composition API) | Reactive single-page application |
| **Build Tool** | Vite | Lightning-fast HMR and bundle optimization |
| **State Management**| Pinia | Centralized auth & application state store |
| **Styling** | Bootstrap 5 | Modern responsive UI components & layouts |
| **Backend** | Python 3.10+ / Flask 3.x | Lightweight, modular RESTful API |
| **ORM** | Flask-SQLAlchemy | Relational database modeling and queries |
| **Authentication**| Flask-JWT-Extended | Stateless JWT token issuance and route security |
| **Database** | SQLite 3 | Embedded SQL database (`backend/instance/trek.db`) |
| **Broker / Cache**| Redis | Task queue broker (DB 0) and API cache store (DB 1) |
| **Task Queue** | Celery | Asynchronous background processing (CSV exports) |
| **Scheduler** | Celery Beat | Scheduled crontab jobs (daily reminders & monthly reports) |

---

## 📂 Directory Structure

```
trekking-management-system/
├── backend/
│   ├── instance/              # SQLite database storage (trek.db)
│   ├── jobs/                  # Celery tasks & scheduler definitions
│   │   ├── celery_app.py      # Celery initialization & crontab schedules
│   │   ├── export_history.py  # Asynchronous CSV booking history export task
│   │   ├── monthly_report.py  # Monthly admin summary report task
│   │   └── reminders.py       # Daily 8:00 AM trek reminder notification task
│   ├── routes/                # Modular Flask blueprints
│   │   ├── admin.py           # Admin metrics and booking management
│   │   ├── auth.py            # Registration, login, profile, notifications
│   │   ├── bookings.py        # Booking lifecycle, history & export downloads
│   │   ├── staff.py           # Staff creation, profiles & trek assignments
│   │   ├── treks.py           # Trek CRUD & staff assignment endpoints
│   │   └── users.py           # User management & account blacklisting
│   ├── services/
│   │   └── cache.py           # Redis caching helper (get, set, clear)
│   ├── app.py                 # Application factory, CORS, and default admin seeder
│   ├── config.py              # Configuration & environment variable ingestion
│   ├── database.py            # SQLAlchemy database instance
│   ├── models.py              # User, Trek, Booking, StaffProfile, Notification models
│   ├── requirements.txt       # Python backend dependencies
│   ├── .env.example           # Example backend environment template
│   └── .env                   # Active backend configuration (git-ignored)
├── frontend/
│   ├── src/
│   │   ├── components/        # Sidebar, TopNavbar, reusable UI components
│   │   ├── layouts/           # Page layouts
│   │   ├── router/            # Vue Router with navigation auth guards
│   │   ├── services/          # Axios API client services
│   │   ├── stores/            # Pinia state stores (auth, user session)
│   │   ├── views/             # Views (Admin, Staff, Trekker dashboards, Treks)
│   │   ├── App.vue            # Root Vue component
│   │   └── main.js            # Frontend entrypoint
│   ├── package.json           # Frontend dependencies & scripts
│   ├── vite.config.js         # Vite configuration
│   ├── .env.example           # Frontend environment template
│   └── .env                   # Active frontend environment
├── .gitignore                 # Git ignore rules for Python, Node, DB & secrets
└── README.md                  # Project documentation
```

---

## ⚙️ Prerequisites

Ensure the following tools are installed on your workstation:

1. **Python**: `v3.10` or higher
2. **Node.js**: `v20.19.0` or higher (with `npm`)
3. **Redis Server**: Installed and running on `localhost:6379` (via native service, WSL2, or Docker)

---

## 🚀 Installation & Setup

### 1. Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a Python virtual environment:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   *(Ensure `FLASK_SECRET_KEY` and `JWT_SECRET_KEY` are populated).*

5. **Initialize Database & Start Backend Server:**
   ```bash
   python app.py
   ```
   The database tables and the **Default Admin Account** will be seeded automatically.
   The API will be available at: `http://127.0.0.1:5000`

---

### 2. Frontend Setup

1. **Open a new terminal and navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node packages:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   Ensure `.env` exists (copied from `.env.example`):
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:5000/api
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```
   The client application will run at: `http://localhost:5173`

---

### 3. Redis & Celery Setup (Async & Scheduled Jobs)

Celery powers asynchronous operations (such as CSV export generation) and automated schedules (daily reminders and monthly admin reports).

1. **Start the Redis Server:**
   ```bash
   redis-server
   ```

2. **Run Celery Worker (In a new terminal inside `backend/` with virtualenv activated):**
   - **Windows:**
     ```powershell
     celery -A jobs.celery_app.celery worker --loglevel=info --pool=solo
     ```
   - **Linux / macOS:**
     ```bash
     celery -A jobs.celery_app.celery worker --loglevel=info
     ```

3. **Run Celery Beat Scheduler (In a separate terminal inside `backend/`):**
   ```bash
   celery -A jobs.celery_app.celery beat --loglevel=info
   ```

#### Configured Background Schedules:
- **Daily Trek Reminders:** Runs every morning at `08:00 AM IST` to alert users of treks starting the following day.
- **Monthly Summary Report:** Runs on the `1st of every month at 08:00 AM IST` to calculate booking summaries and dispatch notifications to administrators.

---

## 🔑 Default Admin Credentials

Upon launching `app.py` for the first time, a default system administrator account is seeded:

| Field | Value |
| :--- | :--- |
| **Email** | `admin@trek.com` |
| **Password** | `admin123` |
| **Role** | `admin` |

*New trekkers can self-register via the `/register` page.*  
*Staff accounts must be created by the Administrator from the Admin portal.*

---

## 📡 API Endpoints Overview

All protected routes require an `Authorization: Bearer <JWT_TOKEN>` header.

### Authentication (`/api/auth`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Public | Register new trekker account |
| `POST` | `/api/auth/login` | Public | Authenticate user & receive JWT token |
| `GET` | `/api/auth/profile` | Authenticated | Retrieve authenticated user profile |
| `PUT` | `/api/auth/profile` | Authenticated | Update user name and phone |
| `PUT` | `/api/auth/change-password` | Authenticated | Change account password |
| `GET` | `/api/auth/notifications` | Authenticated | Fetch user in-app notifications |
| `PUT` | `/api/auth/notifications/<id>/read` | Authenticated | Mark a notification as read |

### Treks (`/api/treks`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/treks/` | Public / Auth | List available treks (cached in Redis) |
| `POST` | `/api/treks/` | Admin | Create a new trek |
| `PUT` | `/api/treks/<id>` | Admin | Update trek details & slots |
| `DELETE`| `/api/treks/<id>` | Admin | Remove an existing trek |
| `GET` | `/api/treks/<id>/staff` | Admin | View staff assigned to a trek |
| `POST` | `/api/treks/<id>/staff` | Admin | Assign staff member to a trek |
| `DELETE`| `/api/treks/<id>/staff/<staff_id>`| Admin | Remove staff assignment |

### Bookings (`/api/bookings`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/bookings/<trek_id>` | Trekker | Book an expedition slot |
| `GET` | `/api/bookings/my-bookings` | Trekker | View active upcoming bookings |
| `PUT` | `/api/bookings/<id>/cancel` | Trekker / Admin | Cancel a booking and restore slot |
| `GET` | `/api/bookings/history` | Trekker | View past/completed booking history |
| `POST` | `/api/bookings/history/export` | Trekker | Trigger asynchronous CSV export task |
| `GET` | `/api/bookings/history/export/<id>` | Trekker | Check status of CSV export task |
| `GET` | `/api/bookings/history/export/<id>/download` | Trekker | Download generated CSV file |

### Staff Management (`/api/staff`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/staff/` | Admin | Create new staff account |
| `GET` | `/api/staff/` | Admin | List all staff members |
| `PUT` | `/api/staff/<id>` | Admin | Update staff profile details |
| `PUT` | `/api/staff/<id>/status` | Admin | Update approval / active status |
| `GET` | `/api/staff/my-treks` | Staff | View treks assigned to logged-in staff |
| `GET` | `/api/staff/my-treks/<id>/participants` | Staff | View participant roster for trek |
| `PUT` | `/api/staff/my-treks/<id>/manage` | Staff | Update status of assigned trek |

### Admin & Users (`/api/admin`, `/api/users`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/admin/dashboard` | Admin | High-level metrics and statistics |
| `GET` | `/api/admin/bookings` | Admin | View all bookings across all users |
| `GET` | `/api/users/` | Admin | List all registered users |
| `PUT` | `/api/users/<id>/status` | Admin | Blacklist or un-blacklist user account |

---

## 🔐 Environment Variables

### Backend (`backend/.env`)
```env
# Flask application secret key for session integrity
FLASK_SECRET_KEY=ce361f2c26666c7be8b2651897c51135a5d0b54f5169aecaa81e68424b431679

# Secret key used for signing JWT tokens
JWT_SECRET_KEY=c976297a7a39920a8e4e19a5e640f205c8c0d1828c79bcabf1a05c0eede83ac1

# JWT token expiration time in seconds (e.g., 3600 = 1 hour)
JWT_ACCESS_TOKEN_EXPIRES=3600

# SQLite database connection URL
DATABASE_URL=sqlite:///trek.db
```

### Frontend (`frontend/.env`)
```env
# Base URL for backend Flask API service
VITE_API_BASE_URL=http://127.0.0.1:5000/api
```

---

## 📄 License & Academic Attribution
This project was designed and implemented for the **Modern Application Development II (MAD II)** course project. All rights reserved.
