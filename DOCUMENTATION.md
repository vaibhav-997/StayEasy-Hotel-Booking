# StayEasy: Simple Project Documentation

This guide explains how the website is organized and how its main features work.

## 1. What are we building?
StayEasy lets customers find hotels, reserve rooms and simulate paying. Owners manage their own hotels and rooms. Administrators approve hotels and can manage content.

The app has six main data models:
1. **User** — account details and role (`customer`, `owner`, or `admin`).
2. **Hotel** — name, location, description, image URL, owner and approval state.
3. **Room** — belongs to a hotel and has a type, price, capacity and availability.
4. **Booking** — customer, room, dates, price and status.
5. **Review** — customer rating and comment for a hotel.
6. **Payment** — booking, amount, method, status, transaction ID and payment date.

## 2. How the folders fit together
### Backend (`backend/`)
- `manage.py`: command-line entry point for Django.
- `config/settings.py`: installed apps, database and authentication settings.
- `config/urls.py`: connects the API URLs to the application.
- `booking/models.py`: database table definitions.
- `booking/serializers.py`: converts database objects to JSON and validates incoming data.
- `booking/permissions.py`: role checks.
- `booking/views.py`: API logic, such as creating bookings and simulating payments.
- `booking/urls.py`: API endpoint paths.

### Frontend (`frontend/`)
- `src/main.jsx`: starts the React app.
- `src/App.jsx`: page layout and navigation.
- `src/api.js`: Axios setup and API requests.
- `src/styles.css`: visual design.
- `package.json`: frontend dependencies and commands.

## 3. Run the project
Follow the commands in `README.md`. Run the backend and frontend in two separate terminals. The backend uses SQLite, so you do not need to install a separate database server.

## 4. User roles
- **Customer:** register, log in, browse approved hotels, create bookings, pay, view bookings and submit reviews.
- **Owner:** create and manage their hotels and rooms; view bookings related to their hotels and confirm or cancel them.
- **Admin:** use Django admin and admin-only API endpoints to approve hotels and inspect users, bookings and payments.

For the simplest admin setup, run `python manage.py createsuperuser` and use the Django admin website.

## 5. Booking flow, step by step
1. A customer opens a hotel and chooses a room.
2. The customer enters check-in and check-out dates.
3. The API checks that check-out is after check-in and that no confirmed or pending booking overlaps those dates.
4. The API creates a booking with `pending` status and calculates the number of nights multiplied by the room's nightly price.
5. The customer clicks **Pay now** and chooses a demo payment method.
6. The API creates a successful fake payment, generates a transaction ID and marks the booking confirmed.
7. The customer can view the booking and payment receipt.

A real payment gateway is **not** connected. The demo payment endpoint must be replaced with a provider such as Razorpay or Stripe test mode before real use.

## 6. Preventing date overlap
Two date ranges overlap when the new check-in is before an existing check-out AND the new check-out is after the existing check-in. The API uses this rule to reject conflicting pending or confirmed bookings. A cancelled booking no longer blocks the room.

## 7. Important API paths
All API paths begin with `/api/`.
- `POST /api/auth/register/` — create a customer or owner account.
- `POST /api/auth/token/` — get JWT access/refresh tokens.
- `GET /api/hotels/` — list approved hotels; supports `?city=Pune&max_price=5000`.
- `GET /api/hotels/<id>/` — hotel details.
- `POST /api/rooms/` — owner creates a room.
- `POST /api/bookings/` — customer creates a booking.
- `GET /api/bookings/` — current user's bookings, or all bookings for an admin.
- `POST /api/payments/` — simulate payment for a booking.
- `GET /api/payments/` — current user's payments, or all payments for an admin.
- `POST /api/reviews/` — submit a review.
- `GET /api/admin/hotels/` — admin hotel approval list.
- `POST /api/admin/hotels/<id>/approve/` — approve a hotel.

## 8. How authentication works
The login endpoint returns JWT tokens. The frontend stores the access token in local storage and sends it in the `Authorization: Bearer ...` header. The backend checks the token before allowing protected actions. For a real production app, consider secure cookie-based storage and additional security review.

## 9. Try a simple demo
1. Create an admin using `createsuperuser`.
2. Register an owner in the app and add a hotel.
3. Approve the hotel through Django admin or the admin API.
4. Add a room as the owner.
5. Register a customer, book dates and use the fake payment.
6. Open **My bookings** to see the confirmed booking and receipt.

## 10. Learning suggestions
Read files in this order:
1. `booking/models.py` — understand the data.
2. `booking/serializers.py` — understand validation.
3. `booking/permissions.py` — understand roles.
4. `booking/views.py` — understand the API behavior.
5. `booking/urls.py` — see how URLs connect to views.
6. `frontend/src/api.js` and `frontend/src/App.jsx` — see how React calls the API.

## 11. Limitations and next steps
This is a learning/demo project. It needs additional work before public deployment: robust automated tests, email verification, password reset, rate limiting, audit logs, stronger concurrency protection for booking, secure production settings, image uploads, and integration with a real payment provider.
