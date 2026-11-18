# StayEasy — Hotel Booking Website

A beginner-friendly hotel booking project using **Django REST Framework + SQLite** for the backend and **React + Vite** for the frontend. It includes customer, hotel-owner and admin roles, room bookings, reviews, and a simulated payment flow.

## Requirements
- Python 3.10+
- Node.js 18+
- npm

## 1. Run the backend
Open a terminal in `backend/`:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations booking
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API runs at `http://127.0.0.1:8000/`. Django admin is at `http://127.0.0.1:8000/admin/`.

The first superuser is an administrator. For demo data, log into Django admin and add hotels/rooms, or register an owner through the frontend and create them there.

## 2. Run the frontend
Open another terminal in `frontend/`:

```bash
npm install
npm run dev
```

Open the URL Vite prints, usually `http://localhost:5173/`.

## Demo notes
- The payment is simulated. **Do not enter real card details.**
- For an easy local demo, register a customer and an owner. Owner-created hotels need admin approval before customers can see them.
- To create an admin, use `createsuperuser`; staff/superusers have admin access.
- API permissions are intentionally kept simple for learning. This is a learning project, not production-ready software.

## Project map
- `backend/` — API, database models, authentication and permissions.
- `frontend/` — React pages and styles.
- `DOCUMENTATION.md` — step-by-step explanation in plain language.
