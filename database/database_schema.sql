-- ===============================
-- 1. Extensions
-- ===============================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===============================
-- 2. Master / Identity
-- ===============================
CREATE TABLE roles (
    id              SMALLSERIAL PRIMARY KEY,
    code            VARCHAR(30) NOT NULL UNIQUE, -- SUPER_ADMIN, BRANCH_ADMIN, CUSTOMER, STAFF
    name            VARCHAR(100) NOT NULL
);

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    phone           VARCHAR(20) UNIQUE,
    password_hash   TEXT NOT NULL,
    full_name       VARCHAR(150) NOT NULL,
    date_of_birth   DATE,
    gender          VARCHAR(10),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_roles (
    user_id         UUID NOT NULL,
    role_id         SMALLINT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT
);

-- ===============================
-- 3. Multi-vendor (Cinema chain / Branch)
-- ===============================
CREATE TABLE vendors (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code            VARCHAR(50) NOT NULL UNIQUE,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE branches (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_id       UUID NOT NULL,
    code            VARCHAR(50) NOT NULL UNIQUE,
    name            VARCHAR(200) NOT NULL,
    address_line    VARCHAR(300) NOT NULL,
    city            VARCHAR(100) NOT NULL,
    district        VARCHAR(100),
    latitude        NUMERIC(10,7),
    longitude       NUMERIC(10,7),
    phone           VARCHAR(20),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE RESTRICT
);

-- branch admin/staff mapping
CREATE TABLE branch_staff (
    branch_id        UUID NOT NULL,
    user_id          UUID NOT NULL,
    staff_role       VARCHAR(30) NOT NULL, -- BRANCH_ADMIN, STAFF
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    assigned_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (branch_id, user_id),
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ===============================
-- 4. Movie catalog
-- ===============================
CREATE TABLE movie_genres (
    id              SMALLSERIAL PRIMARY KEY,
    code            VARCHAR(40) NOT NULL UNIQUE,
    name            VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE movies (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title           VARCHAR(255) NOT NULL,
    original_title  VARCHAR(255),
    description     TEXT,
    duration_min    SMALLINT NOT NULL CHECK (duration_min > 0),
    release_date    DATE,
    age_rating      VARCHAR(10), -- P, K, T13, T16, T18...
    language        VARCHAR(50),
    trailer_url     TEXT,
    poster_url      TEXT,
    status          VARCHAR(20) NOT NULL DEFAULT 'UPCOMING', -- UPCOMING/NOW_SHOWING/ENDED
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE movie_genre_map (
    movie_id         UUID NOT NULL,
    genre_id         SMALLINT NOT NULL,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES movie_genres(id) ON DELETE RESTRICT
);

-- ===============================
-- 5. Auditorium / Seat
-- ===============================
CREATE TABLE auditoriums (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_id        UUID NOT NULL,
    code             VARCHAR(30) NOT NULL,  -- Room code in branch
    name             VARCHAR(100) NOT NULL,
    total_seats      INTEGER NOT NULL CHECK (total_seats > 0),
    screen_type      VARCHAR(30), -- 2D, 3D, IMAX...
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (branch_id, code),
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE
);

CREATE TABLE seat_types (
    id               SMALLSERIAL PRIMARY KEY,
    code             VARCHAR(30) NOT NULL UNIQUE, -- STANDARD, VIP, COUPLE
    name             VARCHAR(100) NOT NULL
);

CREATE TABLE seats (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auditorium_id    UUID NOT NULL,
    seat_row         VARCHAR(5) NOT NULL,
    seat_number      SMALLINT NOT NULL CHECK (seat_number > 0),
    seat_type_id     SMALLINT NOT NULL,
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (auditorium_id, seat_row, seat_number),
    FOREIGN KEY (auditorium_id) REFERENCES auditoriums(id) ON DELETE CASCADE,
    FOREIGN KEY (seat_type_id) REFERENCES seat_types(id) ON DELETE RESTRICT
);

-- ===============================
-- 6. Showtimes / Pricing
-- ===============================
CREATE TABLE showtimes (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    movie_id         UUID NOT NULL,
    auditorium_id    UUID NOT NULL,
    starts_at        TIMESTAMPTZ NOT NULL,
    ends_at          TIMESTAMPTZ NOT NULL,
    status           VARCHAR(20) NOT NULL DEFAULT 'OPEN', -- OPEN/CLOSED/CANCELLED
    base_price       NUMERIC(12,2) NOT NULL CHECK (base_price >= 0),
    created_by       UUID,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (ends_at > starts_at),
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE RESTRICT,
    FOREIGN KEY (auditorium_id) REFERENCES auditoriums(id) ON DELETE RESTRICT,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Optional: price by seat type per showtime
CREATE TABLE showtime_seat_prices (
    showtime_id      UUID NOT NULL,
    seat_type_id     SMALLINT NOT NULL,
    price            NUMERIC(12,2) NOT NULL CHECK (price >= 0),
    PRIMARY KEY (showtime_id, seat_type_id),
    FOREIGN KEY (showtime_id) REFERENCES showtimes(id) ON DELETE CASCADE,
    FOREIGN KEY (seat_type_id) REFERENCES seat_types(id) ON DELETE RESTRICT
);

-- ===============================
-- 7. Booking / Ticketing
-- ===============================
CREATE TABLE bookings (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_code     VARCHAR(30) NOT NULL UNIQUE,
    user_id          UUID NOT NULL,
    showtime_id      UUID NOT NULL,
    status           VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING/CONFIRMED/CANCELLED/EXPIRED
    subtotal_amount  NUMERIC(12,2) NOT NULL CHECK (subtotal_amount >= 0),
    discount_amount  NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
    total_amount     NUMERIC(12,2) NOT NULL CHECK (total_amount >= 0),
    expires_at       TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (showtime_id) REFERENCES showtimes(id) ON DELETE RESTRICT
);

CREATE TABLE booking_items (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id       UUID NOT NULL,
    seat_id          UUID NOT NULL,
    unit_price       NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    UNIQUE (booking_id, seat_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (seat_id) REFERENCES seats(id) ON DELETE RESTRICT
);

-- Prevent double booking for same showtime + seat
CREATE TABLE tickets (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_item_id  UUID NOT NULL UNIQUE,
    showtime_id      UUID NOT NULL,
    seat_id          UUID NOT NULL,
    ticket_code      VARCHAR(50) NOT NULL UNIQUE,
    qr_code_data     TEXT,
    status           VARCHAR(20) NOT NULL DEFAULT 'ISSUED', -- ISSUED/USED/CANCELLED/REFUNDED
    issued_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    used_at          TIMESTAMPTZ,
    UNIQUE (showtime_id, seat_id),
    FOREIGN KEY (booking_item_id) REFERENCES booking_items(id) ON DELETE CASCADE,
    FOREIGN KEY (showtime_id) REFERENCES showtimes(id) ON DELETE RESTRICT,
    FOREIGN KEY (seat_id) REFERENCES seats(id) ON DELETE RESTRICT
);

-- ===============================
-- 8. Future-ready modules: Promotion / Payment
-- ===============================
CREATE TABLE promotions (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code             VARCHAR(50) NOT NULL UNIQUE,
    name             VARCHAR(200) NOT NULL,
    description      TEXT,
    discount_type    VARCHAR(20) NOT NULL, -- PERCENT/FIXED
    discount_value   NUMERIC(12,2) NOT NULL CHECK (discount_value >= 0),
    max_discount     NUMERIC(12,2),
    min_order_amount NUMERIC(12,2),
    starts_at        TIMESTAMPTZ NOT NULL,
    ends_at          TIMESTAMPTZ NOT NULL,
    vendor_id        UUID,   -- null = global
    branch_id        UUID,   -- optional branch-specific promo
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (ends_at > starts_at),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE SET NULL,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL
);

CREATE TABLE booking_promotions (
    booking_id       UUID NOT NULL,
    promotion_id     UUID NOT NULL,
    applied_amount   NUMERIC(12,2) NOT NULL CHECK (applied_amount >= 0),
    PRIMARY KEY (booking_id, promotion_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (promotion_id) REFERENCES promotions(id) ON DELETE RESTRICT
);

CREATE TABLE payment_methods (
    id               SMALLSERIAL PRIMARY KEY,
    code             VARCHAR(30) NOT NULL UNIQUE, -- MOMO, VNPAY, CARD, CASH...
    name             VARCHAR(100) NOT NULL
);

CREATE TABLE payments (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id       UUID NOT NULL,
    method_id        SMALLINT NOT NULL,
    provider_txn_id  VARCHAR(100) UNIQUE,
    amount           NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
    status           VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING/PAID/FAILED/REFUNDED
    paid_at          TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE RESTRICT,
    FOREIGN KEY (method_id) REFERENCES payment_methods(id) ON DELETE RESTRICT
);

-- ===============================
-- 9. Indexes (frequent queries)
-- ===============================
CREATE INDEX idx_users_email_active ON users(email, is_active);
CREATE INDEX idx_branches_vendor ON branches(vendor_id);
CREATE INDEX idx_auditoriums_branch ON auditoriums(branch_id);
CREATE INDEX idx_seats_auditorium ON seats(auditorium_id);
CREATE INDEX idx_showtimes_movie_start ON showtimes(movie_id, starts_at);
CREATE INDEX idx_showtimes_auditorium_start ON showtimes(auditorium_id, starts_at);
CREATE INDEX idx_bookings_user_created ON bookings(user_id, created_at DESC);
CREATE INDEX idx_bookings_showtime ON bookings(showtime_id);
CREATE INDEX idx_booking_items_booking ON booking_items(booking_id);
CREATE INDEX idx_tickets_showtime_seat ON tickets(showtime_id, seat_id);
CREATE INDEX idx_payments_booking_status ON payments(booking_id, status);
CREATE INDEX idx_promotions_active_time ON promotions(is_active, starts_at, ends_at);