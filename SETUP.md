# PPQ - CineAI Full Stack Setup

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/PhongNguyenKobe/PPQ_22BITV01.git
cd PPQ_22BITV01
```

### 2. Setup Environment Variables
```bash
# Copy example files
cp .env.example .env
cp .env.backend.example backend/.env
cp .env.frontend.example frontend/.env

# Edit .env files and change sensitive values
vim .env
```

### 3. Start Services with Docker Compose
```bash
# Start all services (db + backend + frontend)
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 4. Access Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

### 5. Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (warning: deletes database)
docker-compose down -v
```

## Local Development Setup (Without Docker)

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
alembic upgrade head

# Seed demo data (optional)
python scripts/seed_demo_auth.py

# Run server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user profile

### Movies
- `GET /api/v1/movies` - List all movies
- `GET /api/v1/movies/{id}` - Get movie details
- `GET /api/v1/movies/{id}/showtimes` - Get movie showtimes
- `GET /api/v1/movies/recommendations` - Get recommended movies
- `POST /api/v1/movies/semantic-search` - Search movies semantically

### Bookings
- `POST /api/v1/bookings/seats` - Get available seats for showtime
- `POST /api/v1/bookings` - Create new booking
- `GET /api/v1/bookings` - List user's bookings
- `GET /api/v1/bookings/{booking_id}` - Get booking details

### Payments
- `POST /api/v1/payments/process` - Process payment
- `POST /api/v1/payments/checkout` - Finalize checkout
- `GET /api/v1/payments/{payment_id}` - Get payment details

### Admin
- `GET /api/v1/admin/stats` - Get admin dashboard stats
- `GET /api/v1/admin/users` - List all users
- `POST /api/v1/admin/movies` - Create movie (admin only)
- `PUT /api/v1/admin/movies/{id}` - Update movie (admin only)
- `DELETE /api/v1/admin/movies/{id}` - Delete movie (admin only)

## Project Structure

### Backend (FastAPI)
```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── bookings.py
│   │   │   ├── movies.py
│   │   │   ├── payments.py
│   │   │   └── ...
│   │   ├── deps.py
│   │   └── router.py
│   ├── crud/
│   │   ├── booking.py
│   │   ├── movie.py
│   │   ├── payment.py
│   │   └── user.py
│   ├── db/
│   │   ├── base.py
│   │   ├── models.py
│   │   └── session.py
│   ├── schemas/
│   │   ├── booking.py
│   │   ├── payment.py
│   │   └── ...
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── ...
│   └── main.py
├── alembic/
├── scripts/
├── requirements.txt
└── Dockerfile
```

### Frontend (Nuxt 3)
```
frontend/
├── pages/
│   ├── checkout/
│   │   ├── cinema.vue
│   │   ├── seat.vue
│   │   ├── combo.vue
│   │   └── payment.vue
│   ├── index.vue
│   ├── products.vue
│   ├── login.vue
│   └── admin/
├── components/
├── composables/
│   ├── useAuth.ts
│   ├── useBooking.ts
│   └── useApi.ts
├── store/
│   ├── user.ts
│   ├── movies.ts
│   ├── tickets.ts
│   └── cart.ts
├── utils/
│   ├── format.ts
│   ├── errors.ts
│   └── validation.ts
├── middleware/
│   └── auth.ts
├── layouts/
│   ├── default.vue
│   ├── checkout.vue
│   └── admin.vue
├── nuxt.config.ts
├── package.json
└── Dockerfile
```

## Database Schema

### Main Tables
- `users` - User accounts
- `roles` - User roles (CUSTOMER, ADMIN, BRANCH_ADMIN, STAFF)
- `vendors` - Cinema chains
- `branches` - Cinema branches/locations
- `auditoriums` - Screens
- `seats` - Individual seats
- `movies` - Movie information
- `movie_genres` - Movie genres
- `showtimes` - Movie showtimes
- `bookings` - Ticket bookings
- `payments` - Payment records

## Testing

### Demo Accounts
```
Customer:
  Email: customer@gmail.com
  Password: customer123

Admin:
  Email: admin@cineai.vn
  Password: admin123

Branch Admin:
  Email: branch-admin@cineai.vn
  Password: branch123
```

## Troubleshooting

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Port Already in Use
```bash
# Change ports in .env file
BACKEND_PORT=8001
FRONTEND_PORT=3001
POSTGRES_PORT=5433

# Restart services
docker-compose down
docker-compose up -d
```

### Migration Errors
```bash
# Reset database and run migrations
docker-compose down -v
docker-compose up -d
```

## Contributing

1. Create feature branch: `git checkout -b feat/your-feature`
2. Make changes and commit: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feat/your-feature`
4. Create Pull Request

## Security Notes

⚠️ **Important**: Before deploying to production:
1. Change all default passwords in `.env`
2. Generate strong JWT secret key
3. Enable HTTPS
4. Configure proper CORS origins
5. Set up proper logging and monitoring
6. Use environment-specific configurations

## License

This project is part of a Software Engineering course.
