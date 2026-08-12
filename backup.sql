--
-- PostgreSQL database dump
--

\restrict Vzj0U7fKDvFKgNiQMLJmeqepMmu1eVanITV9kVYyFyS9erJHrpcYx1GUcw30qb9

-- Dumped from database version 16.14
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: cineai_audit_row(); Type: FUNCTION; Schema: public; Owner: ppq_user
--

CREATE FUNCTION public.cineai_audit_row() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        DECLARE row_id text;
        BEGIN
            row_id := COALESCE((to_jsonb(NEW)->>'id'), (to_jsonb(OLD)->>'id'), 'unknown');
            INSERT INTO audit_events(entity_type, entity_id, action, old_data, new_data, transaction_id)
            VALUES (TG_TABLE_NAME, row_id, TG_OP,
                    CASE WHEN TG_OP IN ('UPDATE','DELETE') THEN to_jsonb(OLD) END,
                    CASE WHEN TG_OP IN ('INSERT','UPDATE') THEN to_jsonb(NEW) END,
                    txid_current()::text);
            RETURN COALESCE(NEW, OLD);
        END; $$;


ALTER FUNCTION public.cineai_audit_row() OWNER TO ppq_user;

--
-- Name: prevent_audit_mutation(); Type: FUNCTION; Schema: public; Owner: ppq_user
--

CREATE FUNCTION public.prevent_audit_mutation() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN RAISE EXCEPTION 'audit_events are immutable'; END; $$;


ALTER FUNCTION public.prevent_audit_mutation() OWNER TO ppq_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO ppq_user;

--
-- Name: audit_events; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.audit_events (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id character varying(50) NOT NULL,
    action character varying(100) NOT NULL,
    new_data jsonb,
    transaction_id character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    old_data jsonb
);


ALTER TABLE public.audit_events OWNER TO ppq_user;

--
-- Name: auditoriums; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.auditoriums (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    branch_id uuid NOT NULL,
    code character varying(30) NOT NULL,
    name character varying(100) NOT NULL,
    total_seats integer NOT NULL,
    screen_type character varying(30),
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.auditoriums OWNER TO ppq_user;

--
-- Name: booking_combos; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.booking_combos (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    booking_id uuid NOT NULL,
    combo_id uuid NOT NULL,
    combo_name character varying(150) NOT NULL,
    unit_price numeric(12,2) NOT NULL,
    quantity integer NOT NULL,
    line_total numeric(12,2) NOT NULL,
    inventory_status character varying(20) DEFAULT 'RESERVED'::character varying NOT NULL
);


ALTER TABLE public.booking_combos OWNER TO ppq_user;

--
-- Name: booking_seats; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.booking_seats (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    booking_id uuid NOT NULL,
    showtime_id uuid NOT NULL,
    seat_id uuid NOT NULL,
    unit_price numeric(12,2) DEFAULT '0'::numeric NOT NULL,
    pricing_details jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE public.booking_seats OWNER TO ppq_user;

--
-- Name: bookings; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.bookings (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    showtime_id uuid NOT NULL,
    total_price numeric(12,2) NOT NULL,
    status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone,
    subtotal_price numeric(12,2) DEFAULT '0'::numeric NOT NULL,
    discount_amount numeric(12,2) DEFAULT '0'::numeric NOT NULL,
    promotion_id uuid,
    seat_snapshot jsonb DEFAULT '[]'::jsonb NOT NULL,
    cancellation_reason text,
    cancellation_requested_at timestamp with time zone,
    cancelled_at timestamp with time zone,
    cancelled_by uuid,
    cancellation_review_note text,
    cancellation_reviewed_at timestamp with time zone,
    cancellation_reviewed_by uuid,
    ticket_code character varying(32),
    checked_in_at timestamp with time zone,
    checked_in_by uuid,
    idempotency_key character varying(100),
    sales_channel character varying(20) DEFAULT 'ONLINE'::character varying NOT NULL,
    customer_name character varying(150),
    customer_email character varying(255),
    customer_phone character varying(20)
);


ALTER TABLE public.bookings OWNER TO ppq_user;

--
-- Name: branch_staff; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.branch_staff (
    branch_id uuid NOT NULL,
    user_id uuid NOT NULL,
    staff_role character varying(30) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    assigned_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.branch_staff OWNER TO ppq_user;

--
-- Name: branches; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.branches (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    vendor_id uuid NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    address_line character varying(300) NOT NULL,
    city character varying(100) NOT NULL,
    district character varying(100),
    latitude numeric(10,7),
    longitude numeric(10,7),
    phone character varying(20),
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.branches OWNER TO ppq_user;

--
-- Name: combos; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.combos (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    branch_id uuid NOT NULL,
    name character varying(150) NOT NULL,
    description text,
    price numeric(12,2) NOT NULL,
    image_url text,
    stock_quantity integer,
    is_active boolean DEFAULT true NOT NULL,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_combos_price_positive CHECK ((price > (0)::numeric))
);


ALTER TABLE public.combos OWNER TO ppq_user;

--
-- Name: movie_change_requests; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.movie_change_requests (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    requested_by_id uuid NOT NULL,
    target_movie_id uuid,
    request_type character varying(20) NOT NULL,
    status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    payload jsonb NOT NULL,
    review_note text,
    reviewed_by_id uuid,
    reviewed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.movie_change_requests OWNER TO ppq_user;

--
-- Name: movie_genre_map; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.movie_genre_map (
    movie_id uuid NOT NULL,
    genre_id smallint NOT NULL
);


ALTER TABLE public.movie_genre_map OWNER TO ppq_user;

--
-- Name: movie_genres; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.movie_genres (
    id smallint NOT NULL,
    code character varying(40) NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.movie_genres OWNER TO ppq_user;

--
-- Name: movie_genres_id_seq; Type: SEQUENCE; Schema: public; Owner: ppq_user
--

CREATE SEQUENCE public.movie_genres_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.movie_genres_id_seq OWNER TO ppq_user;

--
-- Name: movie_genres_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ppq_user
--

ALTER SEQUENCE public.movie_genres_id_seq OWNED BY public.movie_genres.id;


--
-- Name: movie_reviews; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.movie_reviews (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    movie_id uuid NOT NULL,
    user_id uuid NOT NULL,
    rating smallint NOT NULL,
    content text NOT NULL,
    is_visible boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_movie_reviews_rating CHECK (((rating >= 1) AND (rating <= 5)))
);


ALTER TABLE public.movie_reviews OWNER TO ppq_user;

--
-- Name: movies; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.movies (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    title character varying(255) NOT NULL,
    original_title character varying(255),
    description text,
    duration_min smallint NOT NULL,
    release_date date,
    age_rating character varying(10),
    language character varying(50),
    trailer_url text,
    poster_url text,
    status character varying(20) DEFAULT 'UPCOMING'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    tmdb_id integer,
    director character varying(255),
    cast_names jsonb DEFAULT '[]'::jsonb NOT NULL
);


ALTER TABLE public.movies OWNER TO ppq_user;

--
-- Name: notification_outbox; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.notification_outbox (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    event_type character varying(50) NOT NULL,
    channel character varying(20) DEFAULT 'EMAIL'::character varying NOT NULL,
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    attempts integer DEFAULT 0 NOT NULL,
    available_at timestamp with time zone DEFAULT now() NOT NULL,
    sent_at timestamp with time zone,
    last_error text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.notification_outbox OWNER TO ppq_user;

--
-- Name: payment_status_history; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.payment_status_history (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    payment_id uuid NOT NULL,
    old_status character varying(20),
    new_status character varying(20) NOT NULL,
    source character varying(20) NOT NULL,
    response_code character varying(10),
    provider_status character varying(10),
    signature_valid boolean,
    note text,
    raw_payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.payment_status_history OWNER TO ppq_user;

--
-- Name: payments; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.payments (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    booking_id uuid NOT NULL,
    user_id uuid NOT NULL,
    amount numeric(12,2) NOT NULL,
    payment_method character varying(30) NOT NULL,
    status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    transaction_id character varying(150),
    paid_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    provider_ref character varying(100),
    provider_transaction_no character varying(30),
    bank_transaction_no character varying(255),
    bank_code character varying(30),
    card_type character varying(30),
    response_code character varying(10),
    provider_status character varying(10),
    signature_valid boolean,
    provider_paid_at timestamp with time zone,
    last_verified_at timestamp with time zone,
    refund_request_id character varying(32),
    refund_transaction_no character varying(30),
    refund_response_code character varying(10),
    refund_provider_status character varying(10),
    refund_error text,
    refund_attempts integer DEFAULT 0 NOT NULL,
    refund_requested_at timestamp with time zone,
    refunded_at timestamp with time zone,
    idempotency_key character varying(100),
    checkout_url text
);


ALTER TABLE public.payments OWNER TO ppq_user;

--
-- Name: pricing_rules; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.pricing_rules (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(150) NOT NULL,
    branch_id uuid,
    screen_type character varying(30),
    day_of_week integer,
    starts_on timestamp with time zone,
    ends_on timestamp with time zone,
    time_from time without time zone,
    time_to time without time zone,
    multiplier numeric(6,3) DEFAULT '1'::numeric NOT NULL,
    surcharge numeric(12,2) DEFAULT '0'::numeric NOT NULL,
    priority integer DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT ck_pricing_rules_multiplier_positive CHECK ((multiplier > (0)::numeric))
);


ALTER TABLE public.pricing_rules OWNER TO ppq_user;

--
-- Name: promotion_redemptions; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.promotion_redemptions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    promotion_id uuid NOT NULL,
    user_id uuid NOT NULL,
    booking_id uuid NOT NULL,
    payment_id uuid NOT NULL,
    discount_amount numeric(12,2) NOT NULL,
    status character varying(20) DEFAULT 'RESERVED'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.promotion_redemptions OWNER TO ppq_user;

--
-- Name: promotions; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.promotions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    discount_type character varying(20) NOT NULL,
    discount_value numeric(12,2) NOT NULL,
    max_discount numeric(12,2),
    min_order_amount numeric(12,2) DEFAULT '0'::numeric NOT NULL,
    starts_at timestamp with time zone NOT NULL,
    ends_at timestamp with time zone NOT NULL,
    usage_limit integer,
    used_count integer DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    per_user_limit integer,
    budget_amount numeric(14,2),
    used_amount numeric(14,2) DEFAULT '0'::numeric NOT NULL,
    branch_ids jsonb DEFAULT '[]'::jsonb NOT NULL,
    movie_ids jsonb DEFAULT '[]'::jsonb NOT NULL,
    payment_methods jsonb DEFAULT '[]'::jsonb NOT NULL,
    excluded_dates jsonb DEFAULT '[]'::jsonb NOT NULL,
    CONSTRAINT ck_promotions_discount_positive CHECK ((discount_value > (0)::numeric)),
    CONSTRAINT ck_promotions_usage_limit CHECK (((usage_limit IS NULL) OR (usage_limit >= 0)))
);


ALTER TABLE public.promotions OWNER TO ppq_user;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.roles (
    id smallint NOT NULL,
    code character varying(30) NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.roles OWNER TO ppq_user;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: ppq_user
--

CREATE SEQUENCE public.roles_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO ppq_user;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ppq_user
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: seat_holds; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.seat_holds (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    showtime_id uuid NOT NULL,
    seat_id uuid NOT NULL,
    user_id uuid NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.seat_holds OWNER TO ppq_user;

--
-- Name: seat_types; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.seat_types (
    id smallint NOT NULL,
    code character varying(30) NOT NULL,
    name character varying(100) NOT NULL,
    price_multiplier numeric(5,2) DEFAULT 1.00 NOT NULL
);


ALTER TABLE public.seat_types OWNER TO ppq_user;

--
-- Name: seat_types_id_seq; Type: SEQUENCE; Schema: public; Owner: ppq_user
--

CREATE SEQUENCE public.seat_types_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.seat_types_id_seq OWNER TO ppq_user;

--
-- Name: seat_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ppq_user
--

ALTER SEQUENCE public.seat_types_id_seq OWNED BY public.seat_types.id;


--
-- Name: seats; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.seats (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    auditorium_id uuid NOT NULL,
    seat_row character varying(5) NOT NULL,
    seat_number smallint NOT NULL,
    seat_type_id smallint NOT NULL,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.seats OWNER TO ppq_user;

--
-- Name: showtimes; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.showtimes (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    movie_id uuid NOT NULL,
    auditorium_id uuid NOT NULL,
    starts_at timestamp with time zone NOT NULL,
    ends_at timestamp with time zone NOT NULL,
    status character varying(20) DEFAULT 'OPEN'::character varying NOT NULL,
    base_price numeric(12,2) NOT NULL,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    booking_closes_at timestamp with time zone NOT NULL,
    cancellation_reason text
);


ALTER TABLE public.showtimes OWNER TO ppq_user;

--
-- Name: tickets; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.tickets (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    booking_id uuid NOT NULL,
    booking_seat_id uuid,
    seat_id uuid NOT NULL,
    ticket_code character varying(40) NOT NULL,
    qr_nonce character varying(32) NOT NULL,
    seat_row character varying(5) NOT NULL,
    seat_number integer NOT NULL,
    status character varying(20) DEFAULT 'ISSUED'::character varying NOT NULL,
    issued_at timestamp with time zone DEFAULT now() NOT NULL,
    checked_in_at timestamp with time zone,
    checked_in_by uuid,
    unit_price numeric(12,2) DEFAULT '0'::numeric NOT NULL,
    pricing_details jsonb DEFAULT '{}'::jsonb NOT NULL,
    scan_code character varying(12) NOT NULL
);


ALTER TABLE public.tickets OWNER TO ppq_user;

--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.user_roles (
    user_id uuid NOT NULL,
    role_id smallint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_roles OWNER TO ppq_user;

--
-- Name: users; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.users (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    email character varying(255) NOT NULL,
    phone character varying(20),
    password_hash text NOT NULL,
    full_name character varying(150) NOT NULL,
    date_of_birth date,
    gender character varying(10),
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    address character varying(255),
    receive_marketing_emails boolean DEFAULT true NOT NULL,
    is_verified boolean DEFAULT false NOT NULL,
    verification_code character varying(10),
    verification_code_expires_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO ppq_user;

--
-- Name: vendors; Type: TABLE; Schema: public; Owner: ppq_user
--

CREATE TABLE public.vendors (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.vendors OWNER TO ppq_user;

--
-- Name: movie_genres id; Type: DEFAULT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_genres ALTER COLUMN id SET DEFAULT nextval('public.movie_genres_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: seat_types id; Type: DEFAULT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.seat_types ALTER COLUMN id SET DEFAULT nextval('public.seat_types_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.alembic_version (version_num) FROM stdin;
0029_single_active_branch
\.


--
-- Data for Name: audit_events; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.audit_events (id, entity_type, entity_id, action, new_data, transaction_id, created_at, old_data) FROM stdin;
59daa1a9-95da-438b-99ac-79f97ac0d88a	tickets	ce71e6d5-d739-427b-a72c-d96264fa9251	UPDATE	{"id": "ce71e6d5-d739-427b-a72c-d96264fa9251", "status": "ISSUED", "seat_id": "bb7adacc-7a56-450d-8421-ac0d76c60a86", "qr_nonce": "cfd55cf5258d46b8bd15af2656b9e620", "seat_row": "C", "issued_at": "2026-07-28T12:03:33.011302+00:00", "booking_id": "0c6f3ae9-dfaa-4713-91e9-6715e8f3b78d", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260730001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "fc09d9aa-d0b2-44d5-8115-82e83ffcffb2", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "ce71e6d5-d739-427b-a72c-d96264fa9251", "status": "ISSUED", "seat_id": "bb7adacc-7a56-450d-8421-ac0d76c60a86", "qr_nonce": "cfd55cf5258d46b8bd15af2656b9e620", "seat_row": "C", "issued_at": "2026-07-28T12:03:33.011302+00:00", "booking_id": "0c6f3ae9-dfaa-4713-91e9-6715e8f3b78d", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260730001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "fc09d9aa-d0b2-44d5-8115-82e83ffcffb2", "pricing_details": {}}
90aca5e0-f6e9-40ac-89a6-33a85e5bf48d	tickets	795636ef-4b39-4212-aea3-cfb77d7e66ae	UPDATE	{"id": "795636ef-4b39-4212-aea3-cfb77d7e66ae", "status": "ISSUED", "seat_id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "qr_nonce": "7e97f3080b3f4fdab8d1c6e343c4a9cf", "seat_row": "D", "issued_at": "2026-07-29T06:45:07.339846+00:00", "booking_id": "1860f4e8-918e-4597-a86d-2577be728613", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260730002-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "d2a29c4f-18e1-4880-a101-2c1a57760d38", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "795636ef-4b39-4212-aea3-cfb77d7e66ae", "status": "ISSUED", "seat_id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "qr_nonce": "7e97f3080b3f4fdab8d1c6e343c4a9cf", "seat_row": "D", "issued_at": "2026-07-29T06:45:07.339846+00:00", "booking_id": "1860f4e8-918e-4597-a86d-2577be728613", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260730002-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "d2a29c4f-18e1-4880-a101-2c1a57760d38", "pricing_details": {}}
480bfe55-6291-4610-9188-e064fa2287f8	tickets	69c90350-087f-462d-81b6-97984f547b2b	UPDATE	{"id": "69c90350-087f-462d-81b6-97984f547b2b", "status": "ISSUED", "seat_id": "078e8247-f639-442f-9ed8-c10452b93473", "qr_nonce": "a4a4f918a6df4ce19aa48d54688119a1", "seat_row": "E", "issued_at": "2026-07-29T07:21:40.053029+00:00", "booking_id": "ff8333f4-1be5-4a74-9b3d-e3ee400772d9", "unit_price": 0.00, "seat_number": 7, "ticket_code": "C7260730003-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "5273ef67-f2b6-4047-9890-b5fb2b534d34", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "69c90350-087f-462d-81b6-97984f547b2b", "status": "ISSUED", "seat_id": "078e8247-f639-442f-9ed8-c10452b93473", "qr_nonce": "a4a4f918a6df4ce19aa48d54688119a1", "seat_row": "E", "issued_at": "2026-07-29T07:21:40.053029+00:00", "booking_id": "ff8333f4-1be5-4a74-9b3d-e3ee400772d9", "unit_price": 0.00, "seat_number": 7, "ticket_code": "C7260730003-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "5273ef67-f2b6-4047-9890-b5fb2b534d34", "pricing_details": {}}
4e9879af-8bea-4309-bc92-9d8db846c2d7	tickets	0da25da9-2716-4167-acd3-1fafa1eb137f	UPDATE	{"id": "0da25da9-2716-4167-acd3-1fafa1eb137f", "status": "ISSUED", "seat_id": "5de88e3a-c599-4d7d-b4fb-35c594942a43", "qr_nonce": "c052d83ef66c45458011b1ac10a3f5b0", "seat_row": "E", "issued_at": "2026-07-29T07:21:40.053029+00:00", "booking_id": "ff8333f4-1be5-4a74-9b3d-e3ee400772d9", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260730003-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "d876cb60-941e-4880-9af5-c19d7591769f", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "0da25da9-2716-4167-acd3-1fafa1eb137f", "status": "ISSUED", "seat_id": "5de88e3a-c599-4d7d-b4fb-35c594942a43", "qr_nonce": "c052d83ef66c45458011b1ac10a3f5b0", "seat_row": "E", "issued_at": "2026-07-29T07:21:40.053029+00:00", "booking_id": "ff8333f4-1be5-4a74-9b3d-e3ee400772d9", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260730003-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "d876cb60-941e-4880-9af5-c19d7591769f", "pricing_details": {}}
d93e2a26-6df6-4232-8541-c00a9b11735e	tickets	7168df21-ae2d-46a6-968d-b43757255099	UPDATE	{"id": "7168df21-ae2d-46a6-968d-b43757255099", "status": "ISSUED", "seat_id": "03efca4b-c0a2-45b8-8212-fbc109c90f90", "qr_nonce": "53239c8b6d7d42a8a6362cb4c27a7703", "seat_row": "A", "issued_at": "2026-07-29T13:15:19.439433+00:00", "booking_id": "751d1181-addc-4100-a0d6-da785f9468b4", "unit_price": 0.00, "seat_number": 6, "ticket_code": "C7260730004-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "beb2aeff-1947-4af5-b46c-b63400619f95", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "7168df21-ae2d-46a6-968d-b43757255099", "status": "ISSUED", "seat_id": "03efca4b-c0a2-45b8-8212-fbc109c90f90", "qr_nonce": "53239c8b6d7d42a8a6362cb4c27a7703", "seat_row": "A", "issued_at": "2026-07-29T13:15:19.439433+00:00", "booking_id": "751d1181-addc-4100-a0d6-da785f9468b4", "unit_price": 0.00, "seat_number": 6, "ticket_code": "C7260730004-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "beb2aeff-1947-4af5-b46c-b63400619f95", "pricing_details": {}}
34673bc5-70d5-45b3-ba62-7ae3731dd4c2	tickets	281fe960-4869-453e-bedd-bb8bb497375a	UPDATE	{"id": "281fe960-4869-453e-bedd-bb8bb497375a", "status": "ISSUED", "seat_id": "25eae2e2-84b0-4afc-b3c9-63c500ea3879", "qr_nonce": "678f6b96f67b4044af97566a1b527271", "seat_row": "A", "issued_at": "2026-07-29T13:38:47.445028+00:00", "booking_id": "4b3483f4-1f1a-454c-9871-63b55cdf0c73", "unit_price": 0.00, "seat_number": 5, "ticket_code": "C7260730005-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "1ef23726-31b3-49f7-8828-6b173ca3dff9", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "281fe960-4869-453e-bedd-bb8bb497375a", "status": "ISSUED", "seat_id": "25eae2e2-84b0-4afc-b3c9-63c500ea3879", "qr_nonce": "678f6b96f67b4044af97566a1b527271", "seat_row": "A", "issued_at": "2026-07-29T13:38:47.445028+00:00", "booking_id": "4b3483f4-1f1a-454c-9871-63b55cdf0c73", "unit_price": 0.00, "seat_number": 5, "ticket_code": "C7260730005-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "1ef23726-31b3-49f7-8828-6b173ca3dff9", "pricing_details": {}}
83579899-c457-406a-88c9-a4c4db817b53	tickets	40d75731-ceb9-4f19-9d4f-eff337c59981	UPDATE	{"id": "40d75731-ceb9-4f19-9d4f-eff337c59981", "status": "ISSUED", "seat_id": "9ba6db82-6e32-4413-8a23-de398df9ffb1", "qr_nonce": "ec4e501067884769b3e7e84af3828883", "seat_row": "A", "issued_at": "2026-07-29T13:58:50.696343+00:00", "booking_id": "3e42ae6b-29d8-45ea-b80c-e7b5ddf1053d", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260730006-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "678d012f-0373-496c-a1fb-09070dae79ff", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "40d75731-ceb9-4f19-9d4f-eff337c59981", "status": "ISSUED", "seat_id": "9ba6db82-6e32-4413-8a23-de398df9ffb1", "qr_nonce": "ec4e501067884769b3e7e84af3828883", "seat_row": "A", "issued_at": "2026-07-29T13:58:50.696343+00:00", "booking_id": "3e42ae6b-29d8-45ea-b80c-e7b5ddf1053d", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260730006-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "678d012f-0373-496c-a1fb-09070dae79ff", "pricing_details": {}}
100051d0-b717-4d22-8641-af1d018bf496	tickets	84f60fa0-6a0c-42b9-90f7-eacbaf70270c	UPDATE	{"id": "84f60fa0-6a0c-42b9-90f7-eacbaf70270c", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "da6fae20eaaf493ab0be5d89ed1e124a", "seat_row": "A", "issued_at": "2026-07-30T15:11:33.114885+00:00", "booking_id": "2a99efd7-7196-4f63-ac4b-f3670caed351", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260801011-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "fd7bf76e-ad46-402e-8fd0-da8475677937", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "84f60fa0-6a0c-42b9-90f7-eacbaf70270c", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "da6fae20eaaf493ab0be5d89ed1e124a", "seat_row": "A", "issued_at": "2026-07-30T15:11:33.114885+00:00", "booking_id": "2a99efd7-7196-4f63-ac4b-f3670caed351", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260801011-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "fd7bf76e-ad46-402e-8fd0-da8475677937", "pricing_details": {}}
47f4a9aa-41ee-4ea7-aead-aef6c5329c11	tickets	cfacf2f0-2c9f-4226-9d1b-23c26e5a90e7	UPDATE	{"id": "cfacf2f0-2c9f-4226-9d1b-23c26e5a90e7", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "95a622bd4b964c92ab00482e6d059da8", "seat_row": "A", "issued_at": "2026-07-30T15:16:55.81962+00:00", "booking_id": "9c735dd5-26fc-4ca8-979c-5c529a8681b6", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731005-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c95d3b27-18d3-4277-85af-412b96b2bd34", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "cfacf2f0-2c9f-4226-9d1b-23c26e5a90e7", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "95a622bd4b964c92ab00482e6d059da8", "seat_row": "A", "issued_at": "2026-07-30T15:16:55.81962+00:00", "booking_id": "9c735dd5-26fc-4ca8-979c-5c529a8681b6", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731005-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c95d3b27-18d3-4277-85af-412b96b2bd34", "pricing_details": {}}
50c52f20-5c6e-476d-b8ef-6151feabc0f2	tickets	9e5a8039-efa3-4546-a3f7-de5bb05f553f	UPDATE	{"id": "9e5a8039-efa3-4546-a3f7-de5bb05f553f", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "f08c6a10a8a64aada0160a33602b20ca", "seat_row": "A", "issued_at": "2026-07-30T15:16:55.81962+00:00", "booking_id": "9c735dd5-26fc-4ca8-979c-5c529a8681b6", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260731005-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "01c0531c-9be8-4e75-80f6-1b952a530abf", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "9e5a8039-efa3-4546-a3f7-de5bb05f553f", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "f08c6a10a8a64aada0160a33602b20ca", "seat_row": "A", "issued_at": "2026-07-30T15:16:55.81962+00:00", "booking_id": "9c735dd5-26fc-4ca8-979c-5c529a8681b6", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260731005-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "01c0531c-9be8-4e75-80f6-1b952a530abf", "pricing_details": {}}
8690b2bd-f571-464a-8f12-b79f9932beee	tickets	7be39ad5-e5eb-4685-ae1a-956f2e67e894	UPDATE	{"id": "7be39ad5-e5eb-4685-ae1a-956f2e67e894", "status": "ISSUED", "seat_id": "aa2f6757-f430-4564-abf7-5ff595888024", "qr_nonce": "432c7eb597a04523a1703916d6e9c9e9", "seat_row": "A", "issued_at": "2026-07-30T15:22:43.78686+00:00", "booking_id": "bcbddc3f-79b6-4d4b-af86-33a1f1e93904", "unit_price": 0.00, "seat_number": 9, "ticket_code": "C7260731006-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "4233c406-1798-4234-90e8-5ba522f72b5d", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "7be39ad5-e5eb-4685-ae1a-956f2e67e894", "status": "ISSUED", "seat_id": "aa2f6757-f430-4564-abf7-5ff595888024", "qr_nonce": "432c7eb597a04523a1703916d6e9c9e9", "seat_row": "A", "issued_at": "2026-07-30T15:22:43.78686+00:00", "booking_id": "bcbddc3f-79b6-4d4b-af86-33a1f1e93904", "unit_price": 0.00, "seat_number": 9, "ticket_code": "C7260731006-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "4233c406-1798-4234-90e8-5ba522f72b5d", "pricing_details": {}}
21ea47ef-6b87-419e-be0c-9efc777f07ea	tickets	3c1e9158-fc60-41a5-86e4-63c8bfe844e1	UPDATE	{"id": "3c1e9158-fc60-41a5-86e4-63c8bfe844e1", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "fa0773e5d2da451b8c1c4082829acb28", "seat_row": "A", "issued_at": "2026-07-30T15:34:25.251012+00:00", "booking_id": "ffb77e65-d41f-48b7-a23a-fd0221a6c53c", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260731007-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "38b07830-d184-4376-b567-284552f0e615", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "3c1e9158-fc60-41a5-86e4-63c8bfe844e1", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "fa0773e5d2da451b8c1c4082829acb28", "seat_row": "A", "issued_at": "2026-07-30T15:34:25.251012+00:00", "booking_id": "ffb77e65-d41f-48b7-a23a-fd0221a6c53c", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260731007-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "38b07830-d184-4376-b567-284552f0e615", "pricing_details": {}}
b67df27d-1cb9-48d3-8ca9-3189971a49ee	tickets	3ccc4d92-e73a-46f9-bc78-2d880c95a370	UPDATE	{"id": "3ccc4d92-e73a-46f9-bc78-2d880c95a370", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "ccc4353362d74400a23fcefe779c5697", "seat_row": "A", "issued_at": "2026-07-30T15:44:52.380195+00:00", "booking_id": "fa5e723c-4c12-4fd5-8708-e23052f2cee8", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260802001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "35afc7d4-81ed-4e1b-9652-df2e67b53752", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "3ccc4d92-e73a-46f9-bc78-2d880c95a370", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "ccc4353362d74400a23fcefe779c5697", "seat_row": "A", "issued_at": "2026-07-30T15:44:52.380195+00:00", "booking_id": "fa5e723c-4c12-4fd5-8708-e23052f2cee8", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260802001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "35afc7d4-81ed-4e1b-9652-df2e67b53752", "pricing_details": {}}
55f46c76-2184-4892-b4c6-b75dfd57cfcf	tickets	5e78c323-d594-4845-bfc8-813643a8e6fe	UPDATE	{"id": "5e78c323-d594-4845-bfc8-813643a8e6fe", "status": "ISSUED", "seat_id": "1129090f-3c21-49d4-b882-b3c62f54be1a", "qr_nonce": "b37d821829b44c7fa674bb286599420b", "seat_row": "B", "issued_at": "2026-07-30T15:49:20.942537+00:00", "booking_id": "d210f403-2fdd-4583-8e18-8cb7034c1a7d", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731008-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c45ad659-7b0d-4f71-8d1e-e374b3ebd603", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "5e78c323-d594-4845-bfc8-813643a8e6fe", "status": "ISSUED", "seat_id": "1129090f-3c21-49d4-b882-b3c62f54be1a", "qr_nonce": "b37d821829b44c7fa674bb286599420b", "seat_row": "B", "issued_at": "2026-07-30T15:49:20.942537+00:00", "booking_id": "d210f403-2fdd-4583-8e18-8cb7034c1a7d", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731008-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c45ad659-7b0d-4f71-8d1e-e374b3ebd603", "pricing_details": {}}
97d29ae1-72a4-4bcd-ab8e-58b8b643be9b	tickets	21042024-b534-4b59-a9cb-4dbf9011de88	UPDATE	{"id": "21042024-b534-4b59-a9cb-4dbf9011de88", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "ee1ab763544243dc979c794b649fe23c", "seat_row": "A", "issued_at": "2026-07-30T16:14:39.110867+00:00", "booking_id": "8eb7e27f-5167-4c41-81a0-cde73361f10f", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260731009-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "8a8620dd-a9f7-4a4b-ad5e-915c57332708", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "21042024-b534-4b59-a9cb-4dbf9011de88", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "ee1ab763544243dc979c794b649fe23c", "seat_row": "A", "issued_at": "2026-07-30T16:14:39.110867+00:00", "booking_id": "8eb7e27f-5167-4c41-81a0-cde73361f10f", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260731009-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "8a8620dd-a9f7-4a4b-ad5e-915c57332708", "pricing_details": {}}
f3ca9321-06bb-4297-9dd7-3f465d995c25	tickets	19538c6d-d1fc-4312-914f-287ea82deb8c	UPDATE	{"id": "19538c6d-d1fc-4312-914f-287ea82deb8c", "status": "ISSUED", "seat_id": "1129090f-3c21-49d4-b882-b3c62f54be1a", "qr_nonce": "788a4eeb48f14fd3aec1de429f2d4587", "seat_row": "B", "issued_at": "2026-07-30T16:24:54.915754+00:00", "booking_id": "3f3d7716-141f-4302-8093-5a9f1fc46235", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260801012-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c02b30ad-8dcc-4e14-aaf5-c00124ead6c2", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "19538c6d-d1fc-4312-914f-287ea82deb8c", "status": "ISSUED", "seat_id": "1129090f-3c21-49d4-b882-b3c62f54be1a", "qr_nonce": "788a4eeb48f14fd3aec1de429f2d4587", "seat_row": "B", "issued_at": "2026-07-30T16:24:54.915754+00:00", "booking_id": "3f3d7716-141f-4302-8093-5a9f1fc46235", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260801012-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c02b30ad-8dcc-4e14-aaf5-c00124ead6c2", "pricing_details": {}}
d01fbe8c-255d-45eb-8ac3-e0b59a9ffcce	tickets	6ad4fb51-1e12-4deb-bc30-d5302cab3eec	UPDATE	{"id": "6ad4fb51-1e12-4deb-bc30-d5302cab3eec", "status": "ISSUED", "seat_id": "2ed79287-99c4-4923-8aa9-a9e39223ad74", "qr_nonce": "5c57ebc12b034a7e8ee74e4b444ec263", "seat_row": "A", "issued_at": "2026-07-30T18:27:32.166246+00:00", "booking_id": "a4349175-2741-4061-be9a-d488c5fd959d", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260802002-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "fd350b19-ce60-4c65-b5db-f3c49a6e63ad", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "6ad4fb51-1e12-4deb-bc30-d5302cab3eec", "status": "ISSUED", "seat_id": "2ed79287-99c4-4923-8aa9-a9e39223ad74", "qr_nonce": "5c57ebc12b034a7e8ee74e4b444ec263", "seat_row": "A", "issued_at": "2026-07-30T18:27:32.166246+00:00", "booking_id": "a4349175-2741-4061-be9a-d488c5fd959d", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260802002-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "fd350b19-ce60-4c65-b5db-f3c49a6e63ad", "pricing_details": {}}
82ebd4b6-248e-47e0-9c5f-afd71989ac00	tickets	83a3887e-5194-4c66-ba5e-762bc4213af1	UPDATE	{"id": "83a3887e-5194-4c66-ba5e-762bc4213af1", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "990dedbaec3143ed815bba9f6f8287bf", "seat_row": "A", "issued_at": "2026-07-30T18:27:32.166246+00:00", "booking_id": "a4349175-2741-4061-be9a-d488c5fd959d", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260802002-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "74b9c13a-17f2-47a7-b40a-69420dadb411", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "83a3887e-5194-4c66-ba5e-762bc4213af1", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "990dedbaec3143ed815bba9f6f8287bf", "seat_row": "A", "issued_at": "2026-07-30T18:27:32.166246+00:00", "booking_id": "a4349175-2741-4061-be9a-d488c5fd959d", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260802002-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "74b9c13a-17f2-47a7-b40a-69420dadb411", "pricing_details": {}}
5784f859-7ef9-4d10-a270-dff3d566e840	tickets	ec6a34f3-10a5-4f1e-997a-7e64b5ecabcb	UPDATE	{"id": "ec6a34f3-10a5-4f1e-997a-7e64b5ecabcb", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "6a1d68fa2c754a629539e2bdd0bc72e1", "seat_row": "A", "issued_at": "2026-07-30T18:55:04.577309+00:00", "booking_id": "6bbd507d-85d0-4298-ab5f-73845dc0a90a", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731011-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "85aa6f1c-7f02-48e6-8ee7-13ca0489635c", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "ec6a34f3-10a5-4f1e-997a-7e64b5ecabcb", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "6a1d68fa2c754a629539e2bdd0bc72e1", "seat_row": "A", "issued_at": "2026-07-30T18:55:04.577309+00:00", "booking_id": "6bbd507d-85d0-4298-ab5f-73845dc0a90a", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731011-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "85aa6f1c-7f02-48e6-8ee7-13ca0489635c", "pricing_details": {}}
9194703c-c5f6-401f-8047-3128ae24d1fc	tickets	ee08fe06-4050-4782-83cb-bbb98c797617	UPDATE	{"id": "ee08fe06-4050-4782-83cb-bbb98c797617", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "6004a0f603144303b5b581c14f24dc35", "seat_row": "A", "issued_at": "2026-07-30T19:05:28.817411+00:00", "booking_id": "1fcbccd3-6e37-46b3-b44d-4d0f5fed1550", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731012-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "8533ee26-1b29-497e-84a9-29aa227268d7", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "ee08fe06-4050-4782-83cb-bbb98c797617", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "6004a0f603144303b5b581c14f24dc35", "seat_row": "A", "issued_at": "2026-07-30T19:05:28.817411+00:00", "booking_id": "1fcbccd3-6e37-46b3-b44d-4d0f5fed1550", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731012-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "8533ee26-1b29-497e-84a9-29aa227268d7", "pricing_details": {}}
fac24de2-0d85-46c8-9872-d5e1e693998f	tickets	ab4aa497-5a3c-462e-a60a-aae5d0dba7bc	UPDATE	{"id": "ab4aa497-5a3c-462e-a60a-aae5d0dba7bc", "status": "ISSUED", "seat_id": "03efca4b-c0a2-45b8-8212-fbc109c90f90", "qr_nonce": "ee6b94e5b1b94058b43941b02bd77bfb", "seat_row": "A", "issued_at": "2026-07-30T19:15:33.916256+00:00", "booking_id": "4ab4de29-b4a0-474b-ac6b-fb4c2ee06d75", "unit_price": 0.00, "seat_number": 6, "ticket_code": "C7260731013-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "38d6ce79-923c-4e86-afdb-d15f0793014b", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "ab4aa497-5a3c-462e-a60a-aae5d0dba7bc", "status": "ISSUED", "seat_id": "03efca4b-c0a2-45b8-8212-fbc109c90f90", "qr_nonce": "ee6b94e5b1b94058b43941b02bd77bfb", "seat_row": "A", "issued_at": "2026-07-30T19:15:33.916256+00:00", "booking_id": "4ab4de29-b4a0-474b-ac6b-fb4c2ee06d75", "unit_price": 0.00, "seat_number": 6, "ticket_code": "C7260731013-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "38d6ce79-923c-4e86-afdb-d15f0793014b", "pricing_details": {}}
9ce27170-7c5a-48b9-b053-9417a43b5786	tickets	d1fccd97-c073-46a5-b175-c2669e48387b	UPDATE	{"id": "d1fccd97-c073-46a5-b175-c2669e48387b", "status": "ISSUED", "seat_id": "e57ad5e9-f5ab-480f-9153-7dfa510e2a70", "qr_nonce": "c704d2bfa8da41648f657ead828171df", "seat_row": "B", "issued_at": "2026-07-30T19:39:25.528573+00:00", "booking_id": "85a22a13-c8ac-48f5-b50c-a8b9a22b2f10", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260801014-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c98be923-4081-4696-b4fc-a7e76ff6dc30", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "d1fccd97-c073-46a5-b175-c2669e48387b", "status": "ISSUED", "seat_id": "e57ad5e9-f5ab-480f-9153-7dfa510e2a70", "qr_nonce": "c704d2bfa8da41648f657ead828171df", "seat_row": "B", "issued_at": "2026-07-30T19:39:25.528573+00:00", "booking_id": "85a22a13-c8ac-48f5-b50c-a8b9a22b2f10", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260801014-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c98be923-4081-4696-b4fc-a7e76ff6dc30", "pricing_details": {}}
48edf450-42d7-4daa-986e-6556b3d2b657	tickets	86576948-5bfe-4725-87f5-59056dcd886d	UPDATE	{"id": "86576948-5bfe-4725-87f5-59056dcd886d", "status": "ISSUED", "seat_id": "1129090f-3c21-49d4-b882-b3c62f54be1a", "qr_nonce": "ce27686e487b410ea8342463e7a51d51", "seat_row": "B", "issued_at": "2026-07-30T19:39:25.528573+00:00", "booking_id": "85a22a13-c8ac-48f5-b50c-a8b9a22b2f10", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260801014-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "b9c64734-2cdf-4f43-981d-9a58c894c219", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "86576948-5bfe-4725-87f5-59056dcd886d", "status": "ISSUED", "seat_id": "1129090f-3c21-49d4-b882-b3c62f54be1a", "qr_nonce": "ce27686e487b410ea8342463e7a51d51", "seat_row": "B", "issued_at": "2026-07-30T19:39:25.528573+00:00", "booking_id": "85a22a13-c8ac-48f5-b50c-a8b9a22b2f10", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260801014-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "b9c64734-2cdf-4f43-981d-9a58c894c219", "pricing_details": {}}
5c578c42-a8f2-4e2f-9274-030d6c85f7b3	tickets	828a7286-9d0c-4277-a1aa-d8ebfd508bb2	UPDATE	{"id": "828a7286-9d0c-4277-a1aa-d8ebfd508bb2", "status": "ISSUED", "seat_id": "2ed79287-99c4-4923-8aa9-a9e39223ad74", "qr_nonce": "bdb08131a2af42aa808fe6f722e65be5", "seat_row": "A", "issued_at": "2026-07-30T19:42:47.515884+00:00", "booking_id": "651d5cb6-a9bd-48ad-9404-09ab5e0ee935", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260731014-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "7a5be13f-e937-493a-b716-fd83929df431", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "828a7286-9d0c-4277-a1aa-d8ebfd508bb2", "status": "ISSUED", "seat_id": "2ed79287-99c4-4923-8aa9-a9e39223ad74", "qr_nonce": "bdb08131a2af42aa808fe6f722e65be5", "seat_row": "A", "issued_at": "2026-07-30T19:42:47.515884+00:00", "booking_id": "651d5cb6-a9bd-48ad-9404-09ab5e0ee935", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260731014-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "7a5be13f-e937-493a-b716-fd83929df431", "pricing_details": {}}
2dc196a1-d9dd-470c-ae81-b776a7ae6cf9	tickets	f264ea85-6d96-4862-9f9a-35d0c44eb5eb	UPDATE	{"id": "f264ea85-6d96-4862-9f9a-35d0c44eb5eb", "status": "ISSUED", "seat_id": "dc6f6ebd-0e3f-4a29-aa3b-52f5535b8029", "qr_nonce": "ef33e13805a54aef9e3051394a88740f", "seat_row": "C", "issued_at": "2026-08-02T12:20:10.50569+00:00", "booking_id": "9ce23bfc-f82f-4df3-bcb0-d520925f6c98", "unit_price": 0.00, "seat_number": 7, "ticket_code": "C7260803001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "5a5e5ff1-06f7-4459-ab3d-20a0462b227c", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "f264ea85-6d96-4862-9f9a-35d0c44eb5eb", "status": "ISSUED", "seat_id": "dc6f6ebd-0e3f-4a29-aa3b-52f5535b8029", "qr_nonce": "ef33e13805a54aef9e3051394a88740f", "seat_row": "C", "issued_at": "2026-08-02T12:20:10.50569+00:00", "booking_id": "9ce23bfc-f82f-4df3-bcb0-d520925f6c98", "unit_price": 0.00, "seat_number": 7, "ticket_code": "C7260803001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "5a5e5ff1-06f7-4459-ab3d-20a0462b227c", "pricing_details": {}}
c6e8f4d3-393c-4330-bbe8-6c949bc90d79	tickets	ff1dc471-18b3-40ad-8330-3703ffcf730b	UPDATE	{"id": "ff1dc471-18b3-40ad-8330-3703ffcf730b", "status": "ISSUED", "seat_id": "ee3f6974-b9a2-4808-9dd5-7ec4d7cfb5fb", "qr_nonce": "d7b27e80fc9944e087b79e0ffb3e216d", "seat_row": "C", "issued_at": "2026-08-02T12:20:10.50569+00:00", "booking_id": "9ce23bfc-f82f-4df3-bcb0-d520925f6c98", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260803001-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "4b91f56f-0e7f-4a46-bc95-2aa778892ad2", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "ff1dc471-18b3-40ad-8330-3703ffcf730b", "status": "ISSUED", "seat_id": "ee3f6974-b9a2-4808-9dd5-7ec4d7cfb5fb", "qr_nonce": "d7b27e80fc9944e087b79e0ffb3e216d", "seat_row": "C", "issued_at": "2026-08-02T12:20:10.50569+00:00", "booking_id": "9ce23bfc-f82f-4df3-bcb0-d520925f6c98", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260803001-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "4b91f56f-0e7f-4a46-bc95-2aa778892ad2", "pricing_details": {}}
eba00a1b-3b8a-40dd-8630-c4ce05f2ed44	tickets	09611a32-e7aa-460b-be1c-d9fb7251d9fb	UPDATE	{"id": "09611a32-e7aa-460b-be1c-d9fb7251d9fb", "status": "USED", "seat_id": "51fe1dd3-cf0f-4858-9f2b-0b548ce8d52e", "qr_nonce": "5121c3a01c96460f8f2f2b9cc68e71f4", "seat_row": "D", "issued_at": "2026-08-04T14:53:28.779915+00:00", "booking_id": "2a5ef731-b92b-4fec-98e0-7ee13ca2bdf2", "unit_price": 0.00, "seat_number": 7, "ticket_code": "C7260807001-01", "checked_in_at": "2026-08-05T16:12:06.206065+00:00", "checked_in_by": "2810314c-85d7-46e5-8449-e69ec5ad3285", "booking_seat_id": "1c8b9577-f22b-4d90-a97a-8cf00344c542", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "09611a32-e7aa-460b-be1c-d9fb7251d9fb", "status": "USED", "seat_id": "51fe1dd3-cf0f-4858-9f2b-0b548ce8d52e", "qr_nonce": "5121c3a01c96460f8f2f2b9cc68e71f4", "seat_row": "D", "issued_at": "2026-08-04T14:53:28.779915+00:00", "booking_id": "2a5ef731-b92b-4fec-98e0-7ee13ca2bdf2", "unit_price": 0.00, "seat_number": 7, "ticket_code": "C7260807001-01", "checked_in_at": "2026-08-05T16:12:06.206065+00:00", "checked_in_by": "2810314c-85d7-46e5-8449-e69ec5ad3285", "booking_seat_id": "1c8b9577-f22b-4d90-a97a-8cf00344c542", "pricing_details": {}}
aa2f9a68-b3d4-4d86-8cdc-3e03da990499	tickets	69c90350-087f-462d-81b6-97984f547b2b	UPDATE	{"id": "69c90350-087f-462d-81b6-97984f547b2b", "status": "ISSUED", "seat_id": "078e8247-f639-442f-9ed8-c10452b93473", "qr_nonce": "a4a4f918a6df4ce19aa48d54688119a1", "seat_row": "E", "issued_at": "2026-07-29T07:21:40.053029+00:00", "scan_code": "Q012FBFCA59A", "booking_id": "ff8333f4-1be5-4a74-9b3d-e3ee400772d9", "unit_price": 0.00, "seat_number": 7, "ticket_code": "C7260730003-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "5273ef67-f2b6-4047-9890-b5fb2b534d34", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "69c90350-087f-462d-81b6-97984f547b2b", "status": "ISSUED", "seat_id": "078e8247-f639-442f-9ed8-c10452b93473", "qr_nonce": "a4a4f918a6df4ce19aa48d54688119a1", "seat_row": "E", "issued_at": "2026-07-29T07:21:40.053029+00:00", "scan_code": null, "booking_id": "ff8333f4-1be5-4a74-9b3d-e3ee400772d9", "unit_price": 0.00, "seat_number": 7, "ticket_code": "C7260730003-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "5273ef67-f2b6-4047-9890-b5fb2b534d34", "pricing_details": {}}
d7714701-4d9b-4548-b414-3c2970248860	tickets	2bf8a8a0-b246-4f6a-a00d-7bac0664c795	UPDATE	{"id": "2bf8a8a0-b246-4f6a-a00d-7bac0664c795", "status": "USED", "seat_id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "qr_nonce": "08b7d8d14c2b4c59aa41c02da8d0a521", "seat_row": "D", "issued_at": "2026-08-04T14:53:28.779915+00:00", "booking_id": "2a5ef731-b92b-4fec-98e0-7ee13ca2bdf2", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260807001-02", "checked_in_at": "2026-08-05T16:12:06.206065+00:00", "checked_in_by": "2810314c-85d7-46e5-8449-e69ec5ad3285", "booking_seat_id": "aba62010-f054-48ff-9a93-6aeed2feacbf", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "2bf8a8a0-b246-4f6a-a00d-7bac0664c795", "status": "USED", "seat_id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "qr_nonce": "08b7d8d14c2b4c59aa41c02da8d0a521", "seat_row": "D", "issued_at": "2026-08-04T14:53:28.779915+00:00", "booking_id": "2a5ef731-b92b-4fec-98e0-7ee13ca2bdf2", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260807001-02", "checked_in_at": "2026-08-05T16:12:06.206065+00:00", "checked_in_by": "2810314c-85d7-46e5-8449-e69ec5ad3285", "booking_seat_id": "aba62010-f054-48ff-9a93-6aeed2feacbf", "pricing_details": {}}
47628a32-d568-494f-bcfa-641c6198ee7f	tickets	2e4c49f8-e6f4-4331-95b2-10fb88427cee	UPDATE	{"id": "2e4c49f8-e6f4-4331-95b2-10fb88427cee", "status": "ISSUED", "seat_id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "qr_nonce": "f4825024f079455f9ae5bbedef06a2bb", "seat_row": "D", "issued_at": "2026-08-06T12:12:36.938116+00:00", "booking_id": "533600da-cf60-4155-b812-c255add2ef45", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260807002-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "55bf09ae-4525-44b1-bf51-cbc90682cd50", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "2e4c49f8-e6f4-4331-95b2-10fb88427cee", "status": "ISSUED", "seat_id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "qr_nonce": "f4825024f079455f9ae5bbedef06a2bb", "seat_row": "D", "issued_at": "2026-08-06T12:12:36.938116+00:00", "booking_id": "533600da-cf60-4155-b812-c255add2ef45", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260807002-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "55bf09ae-4525-44b1-bf51-cbc90682cd50", "pricing_details": {}}
4209cdff-8fa6-47ba-b2bc-c9773bc8c2f8	tickets	75e6d425-42c2-49b7-bf9d-fcad40a2cb75	UPDATE	{"id": "75e6d425-42c2-49b7-bf9d-fcad40a2cb75", "status": "ISSUED", "seat_id": "77e0c246-d4ce-46f5-bc39-c58fa01b46d3", "qr_nonce": "ebdc50b7069f42dc96852ad92f00b5ec", "seat_row": "D", "issued_at": "2026-08-06T12:12:36.938116+00:00", "booking_id": "533600da-cf60-4155-b812-c255add2ef45", "unit_price": 0.00, "seat_number": 9, "ticket_code": "C7260807002-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "44a2a193-fd2f-4aae-b667-6ab7d964fc42", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "75e6d425-42c2-49b7-bf9d-fcad40a2cb75", "status": "ISSUED", "seat_id": "77e0c246-d4ce-46f5-bc39-c58fa01b46d3", "qr_nonce": "ebdc50b7069f42dc96852ad92f00b5ec", "seat_row": "D", "issued_at": "2026-08-06T12:12:36.938116+00:00", "booking_id": "533600da-cf60-4155-b812-c255add2ef45", "unit_price": 0.00, "seat_number": 9, "ticket_code": "C7260807002-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "44a2a193-fd2f-4aae-b667-6ab7d964fc42", "pricing_details": {}}
e0cbf729-3af0-4a43-a005-fac50d74a4cf	tickets	4780f9ba-11aa-4fc6-8f5f-da8c563e01d8	UPDATE	{"id": "4780f9ba-11aa-4fc6-8f5f-da8c563e01d8", "status": "USED", "seat_id": "7191355f-e232-4000-8daa-22c407f8aae5", "qr_nonce": "969697b66c464a0fbafa557211849f01", "seat_row": "D", "issued_at": "2026-08-07T09:02:40.443031+00:00", "booking_id": "b23ea768-02e2-4241-90a7-fcc4c22d1dd2", "unit_price": 0.00, "seat_number": 6, "ticket_code": "C7260808001-01", "checked_in_at": "2026-08-07T09:07:21.172817+00:00", "checked_in_by": "2810314c-85d7-46e5-8449-e69ec5ad3285", "booking_seat_id": "1123d3ff-0e13-4d52-bd19-e60313ba5635", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "4780f9ba-11aa-4fc6-8f5f-da8c563e01d8", "status": "USED", "seat_id": "7191355f-e232-4000-8daa-22c407f8aae5", "qr_nonce": "969697b66c464a0fbafa557211849f01", "seat_row": "D", "issued_at": "2026-08-07T09:02:40.443031+00:00", "booking_id": "b23ea768-02e2-4241-90a7-fcc4c22d1dd2", "unit_price": 0.00, "seat_number": 6, "ticket_code": "C7260808001-01", "checked_in_at": "2026-08-07T09:07:21.172817+00:00", "checked_in_by": "2810314c-85d7-46e5-8449-e69ec5ad3285", "booking_seat_id": "1123d3ff-0e13-4d52-bd19-e60313ba5635", "pricing_details": {}}
1851bff6-5bb0-4976-94bc-816f9e8c1edc	tickets	ce71e6d5-d739-427b-a72c-d96264fa9251	UPDATE	{"id": "ce71e6d5-d739-427b-a72c-d96264fa9251", "status": "ISSUED", "seat_id": "bb7adacc-7a56-450d-8421-ac0d76c60a86", "qr_nonce": "cfd55cf5258d46b8bd15af2656b9e620", "seat_row": "C", "issued_at": "2026-07-28T12:03:33.011302+00:00", "scan_code": "Q236157734A1", "booking_id": "0c6f3ae9-dfaa-4713-91e9-6715e8f3b78d", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260730001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "fc09d9aa-d0b2-44d5-8115-82e83ffcffb2", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "ce71e6d5-d739-427b-a72c-d96264fa9251", "status": "ISSUED", "seat_id": "bb7adacc-7a56-450d-8421-ac0d76c60a86", "qr_nonce": "cfd55cf5258d46b8bd15af2656b9e620", "seat_row": "C", "issued_at": "2026-07-28T12:03:33.011302+00:00", "scan_code": null, "booking_id": "0c6f3ae9-dfaa-4713-91e9-6715e8f3b78d", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260730001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "fc09d9aa-d0b2-44d5-8115-82e83ffcffb2", "pricing_details": {}}
2e2f205b-0608-406a-a710-355dbe7ed7e5	tickets	795636ef-4b39-4212-aea3-cfb77d7e66ae	UPDATE	{"id": "795636ef-4b39-4212-aea3-cfb77d7e66ae", "status": "ISSUED", "seat_id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "qr_nonce": "7e97f3080b3f4fdab8d1c6e343c4a9cf", "seat_row": "D", "issued_at": "2026-07-29T06:45:07.339846+00:00", "scan_code": "Q4F3FD51FE0B", "booking_id": "1860f4e8-918e-4597-a86d-2577be728613", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260730002-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "d2a29c4f-18e1-4880-a101-2c1a57760d38", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "795636ef-4b39-4212-aea3-cfb77d7e66ae", "status": "ISSUED", "seat_id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "qr_nonce": "7e97f3080b3f4fdab8d1c6e343c4a9cf", "seat_row": "D", "issued_at": "2026-07-29T06:45:07.339846+00:00", "scan_code": null, "booking_id": "1860f4e8-918e-4597-a86d-2577be728613", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260730002-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "d2a29c4f-18e1-4880-a101-2c1a57760d38", "pricing_details": {}}
55950d12-5c7d-426e-a14e-1eca1415fe41	booking_seats	20187e40-9bb5-4362-a873-29a6964a9235	INSERT	{"id": "20187e40-9bb5-4362-a873-29a6964a9235", "seat_id": "d6429f22-16aa-431d-bdce-02c74b61037f", "booking_id": "96505b30-69ca-4904-ad53-348258129a4d", "unit_price": 90000.00, "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "pricing_details": {"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1193	2026-08-10 06:26:43.302779+00	\N
85691554-9e34-4a58-9d09-5d21917ca425	tickets	0da25da9-2716-4167-acd3-1fafa1eb137f	UPDATE	{"id": "0da25da9-2716-4167-acd3-1fafa1eb137f", "status": "ISSUED", "seat_id": "5de88e3a-c599-4d7d-b4fb-35c594942a43", "qr_nonce": "c052d83ef66c45458011b1ac10a3f5b0", "seat_row": "E", "issued_at": "2026-07-29T07:21:40.053029+00:00", "scan_code": "QE873C89B619", "booking_id": "ff8333f4-1be5-4a74-9b3d-e3ee400772d9", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260730003-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "d876cb60-941e-4880-9af5-c19d7591769f", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "0da25da9-2716-4167-acd3-1fafa1eb137f", "status": "ISSUED", "seat_id": "5de88e3a-c599-4d7d-b4fb-35c594942a43", "qr_nonce": "c052d83ef66c45458011b1ac10a3f5b0", "seat_row": "E", "issued_at": "2026-07-29T07:21:40.053029+00:00", "scan_code": null, "booking_id": "ff8333f4-1be5-4a74-9b3d-e3ee400772d9", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260730003-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "d876cb60-941e-4880-9af5-c19d7591769f", "pricing_details": {}}
7767d95a-cdac-4ef9-88f5-3c44c53b1fcf	tickets	7168df21-ae2d-46a6-968d-b43757255099	UPDATE	{"id": "7168df21-ae2d-46a6-968d-b43757255099", "status": "ISSUED", "seat_id": "03efca4b-c0a2-45b8-8212-fbc109c90f90", "qr_nonce": "53239c8b6d7d42a8a6362cb4c27a7703", "seat_row": "A", "issued_at": "2026-07-29T13:15:19.439433+00:00", "scan_code": "Q3B3B02FDB5F", "booking_id": "751d1181-addc-4100-a0d6-da785f9468b4", "unit_price": 0.00, "seat_number": 6, "ticket_code": "C7260730004-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "beb2aeff-1947-4af5-b46c-b63400619f95", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "7168df21-ae2d-46a6-968d-b43757255099", "status": "ISSUED", "seat_id": "03efca4b-c0a2-45b8-8212-fbc109c90f90", "qr_nonce": "53239c8b6d7d42a8a6362cb4c27a7703", "seat_row": "A", "issued_at": "2026-07-29T13:15:19.439433+00:00", "scan_code": null, "booking_id": "751d1181-addc-4100-a0d6-da785f9468b4", "unit_price": 0.00, "seat_number": 6, "ticket_code": "C7260730004-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "beb2aeff-1947-4af5-b46c-b63400619f95", "pricing_details": {}}
971c647b-4d82-45be-95c2-8e54eb20cf66	tickets	281fe960-4869-453e-bedd-bb8bb497375a	UPDATE	{"id": "281fe960-4869-453e-bedd-bb8bb497375a", "status": "ISSUED", "seat_id": "25eae2e2-84b0-4afc-b3c9-63c500ea3879", "qr_nonce": "678f6b96f67b4044af97566a1b527271", "seat_row": "A", "issued_at": "2026-07-29T13:38:47.445028+00:00", "scan_code": "Q95298D0067E", "booking_id": "4b3483f4-1f1a-454c-9871-63b55cdf0c73", "unit_price": 0.00, "seat_number": 5, "ticket_code": "C7260730005-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "1ef23726-31b3-49f7-8828-6b173ca3dff9", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "281fe960-4869-453e-bedd-bb8bb497375a", "status": "ISSUED", "seat_id": "25eae2e2-84b0-4afc-b3c9-63c500ea3879", "qr_nonce": "678f6b96f67b4044af97566a1b527271", "seat_row": "A", "issued_at": "2026-07-29T13:38:47.445028+00:00", "scan_code": null, "booking_id": "4b3483f4-1f1a-454c-9871-63b55cdf0c73", "unit_price": 0.00, "seat_number": 5, "ticket_code": "C7260730005-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "1ef23726-31b3-49f7-8828-6b173ca3dff9", "pricing_details": {}}
bbcb1a76-bfce-4035-b38c-bbdc456f47e3	tickets	40d75731-ceb9-4f19-9d4f-eff337c59981	UPDATE	{"id": "40d75731-ceb9-4f19-9d4f-eff337c59981", "status": "ISSUED", "seat_id": "9ba6db82-6e32-4413-8a23-de398df9ffb1", "qr_nonce": "ec4e501067884769b3e7e84af3828883", "seat_row": "A", "issued_at": "2026-07-29T13:58:50.696343+00:00", "scan_code": "Q38009460388", "booking_id": "3e42ae6b-29d8-45ea-b80c-e7b5ddf1053d", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260730006-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "678d012f-0373-496c-a1fb-09070dae79ff", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "40d75731-ceb9-4f19-9d4f-eff337c59981", "status": "ISSUED", "seat_id": "9ba6db82-6e32-4413-8a23-de398df9ffb1", "qr_nonce": "ec4e501067884769b3e7e84af3828883", "seat_row": "A", "issued_at": "2026-07-29T13:58:50.696343+00:00", "scan_code": null, "booking_id": "3e42ae6b-29d8-45ea-b80c-e7b5ddf1053d", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260730006-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "678d012f-0373-496c-a1fb-09070dae79ff", "pricing_details": {}}
26d871a6-f37c-4672-9f71-ceba0972c6c0	tickets	84f60fa0-6a0c-42b9-90f7-eacbaf70270c	UPDATE	{"id": "84f60fa0-6a0c-42b9-90f7-eacbaf70270c", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "da6fae20eaaf493ab0be5d89ed1e124a", "seat_row": "A", "issued_at": "2026-07-30T15:11:33.114885+00:00", "scan_code": "QE829F0DE607", "booking_id": "2a99efd7-7196-4f63-ac4b-f3670caed351", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260801011-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "fd7bf76e-ad46-402e-8fd0-da8475677937", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "84f60fa0-6a0c-42b9-90f7-eacbaf70270c", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "da6fae20eaaf493ab0be5d89ed1e124a", "seat_row": "A", "issued_at": "2026-07-30T15:11:33.114885+00:00", "scan_code": null, "booking_id": "2a99efd7-7196-4f63-ac4b-f3670caed351", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260801011-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "fd7bf76e-ad46-402e-8fd0-da8475677937", "pricing_details": {}}
7da96066-0200-4084-a17e-5549730fe550	tickets	cfacf2f0-2c9f-4226-9d1b-23c26e5a90e7	UPDATE	{"id": "cfacf2f0-2c9f-4226-9d1b-23c26e5a90e7", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "95a622bd4b964c92ab00482e6d059da8", "seat_row": "A", "issued_at": "2026-07-30T15:16:55.81962+00:00", "scan_code": "QDDA5C948151", "booking_id": "9c735dd5-26fc-4ca8-979c-5c529a8681b6", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731005-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c95d3b27-18d3-4277-85af-412b96b2bd34", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "cfacf2f0-2c9f-4226-9d1b-23c26e5a90e7", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "95a622bd4b964c92ab00482e6d059da8", "seat_row": "A", "issued_at": "2026-07-30T15:16:55.81962+00:00", "scan_code": null, "booking_id": "9c735dd5-26fc-4ca8-979c-5c529a8681b6", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731005-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c95d3b27-18d3-4277-85af-412b96b2bd34", "pricing_details": {}}
e5fc59b6-7847-4ed5-bd1b-fe996b041c07	booking_combos	782f4d3b-676e-44c6-977b-c190b89649b6	UPDATE	{"id": "782f4d3b-676e-44c6-977b-c190b89649b6", "combo_id": "9b2db4b2-323b-4b56-9890-661b096fc619", "quantity": 1, "booking_id": "96505b30-69ca-4904-ad53-348258129a4d", "combo_name": "Combo Kids", "line_total": 59000.00, "unit_price": 59000.00, "inventory_status": "RELEASED"}	1196	2026-08-10 06:31:47.505363+00	{"id": "782f4d3b-676e-44c6-977b-c190b89649b6", "combo_id": "9b2db4b2-323b-4b56-9890-661b096fc619", "quantity": 1, "booking_id": "96505b30-69ca-4904-ad53-348258129a4d", "combo_name": "Combo Kids", "line_total": 59000.00, "unit_price": 59000.00, "inventory_status": "RESERVED"}
1e1cf70c-a69f-4bf1-a457-c0a5d1bdbdb2	tickets	9e5a8039-efa3-4546-a3f7-de5bb05f553f	UPDATE	{"id": "9e5a8039-efa3-4546-a3f7-de5bb05f553f", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "f08c6a10a8a64aada0160a33602b20ca", "seat_row": "A", "issued_at": "2026-07-30T15:16:55.81962+00:00", "scan_code": "Q5018C4F67AA", "booking_id": "9c735dd5-26fc-4ca8-979c-5c529a8681b6", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260731005-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "01c0531c-9be8-4e75-80f6-1b952a530abf", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "9e5a8039-efa3-4546-a3f7-de5bb05f553f", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "f08c6a10a8a64aada0160a33602b20ca", "seat_row": "A", "issued_at": "2026-07-30T15:16:55.81962+00:00", "scan_code": null, "booking_id": "9c735dd5-26fc-4ca8-979c-5c529a8681b6", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260731005-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "01c0531c-9be8-4e75-80f6-1b952a530abf", "pricing_details": {}}
fcc8fdd7-473d-4c32-86ec-cc96793dbeb2	tickets	7be39ad5-e5eb-4685-ae1a-956f2e67e894	UPDATE	{"id": "7be39ad5-e5eb-4685-ae1a-956f2e67e894", "status": "ISSUED", "seat_id": "aa2f6757-f430-4564-abf7-5ff595888024", "qr_nonce": "432c7eb597a04523a1703916d6e9c9e9", "seat_row": "A", "issued_at": "2026-07-30T15:22:43.78686+00:00", "scan_code": "QB4C9B00AC18", "booking_id": "bcbddc3f-79b6-4d4b-af86-33a1f1e93904", "unit_price": 0.00, "seat_number": 9, "ticket_code": "C7260731006-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "4233c406-1798-4234-90e8-5ba522f72b5d", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "7be39ad5-e5eb-4685-ae1a-956f2e67e894", "status": "ISSUED", "seat_id": "aa2f6757-f430-4564-abf7-5ff595888024", "qr_nonce": "432c7eb597a04523a1703916d6e9c9e9", "seat_row": "A", "issued_at": "2026-07-30T15:22:43.78686+00:00", "scan_code": null, "booking_id": "bcbddc3f-79b6-4d4b-af86-33a1f1e93904", "unit_price": 0.00, "seat_number": 9, "ticket_code": "C7260731006-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "4233c406-1798-4234-90e8-5ba522f72b5d", "pricing_details": {}}
1e8a8494-5c02-4d90-9878-3b2d916a02f2	tickets	3c1e9158-fc60-41a5-86e4-63c8bfe844e1	UPDATE	{"id": "3c1e9158-fc60-41a5-86e4-63c8bfe844e1", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "fa0773e5d2da451b8c1c4082829acb28", "seat_row": "A", "issued_at": "2026-07-30T15:34:25.251012+00:00", "scan_code": "Q35B03290E43", "booking_id": "ffb77e65-d41f-48b7-a23a-fd0221a6c53c", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260731007-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "38b07830-d184-4376-b567-284552f0e615", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "3c1e9158-fc60-41a5-86e4-63c8bfe844e1", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "fa0773e5d2da451b8c1c4082829acb28", "seat_row": "A", "issued_at": "2026-07-30T15:34:25.251012+00:00", "scan_code": null, "booking_id": "ffb77e65-d41f-48b7-a23a-fd0221a6c53c", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260731007-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "38b07830-d184-4376-b567-284552f0e615", "pricing_details": {}}
a5868f9e-dc5a-407a-bb0c-082d9ec42a3a	tickets	3ccc4d92-e73a-46f9-bc78-2d880c95a370	UPDATE	{"id": "3ccc4d92-e73a-46f9-bc78-2d880c95a370", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "ccc4353362d74400a23fcefe779c5697", "seat_row": "A", "issued_at": "2026-07-30T15:44:52.380195+00:00", "scan_code": "Q4526E15C0FF", "booking_id": "fa5e723c-4c12-4fd5-8708-e23052f2cee8", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260802001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "35afc7d4-81ed-4e1b-9652-df2e67b53752", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "3ccc4d92-e73a-46f9-bc78-2d880c95a370", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "ccc4353362d74400a23fcefe779c5697", "seat_row": "A", "issued_at": "2026-07-30T15:44:52.380195+00:00", "scan_code": null, "booking_id": "fa5e723c-4c12-4fd5-8708-e23052f2cee8", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260802001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "35afc7d4-81ed-4e1b-9652-df2e67b53752", "pricing_details": {}}
6b8f43cb-d82c-4434-9849-bafe166e6cbb	tickets	5e78c323-d594-4845-bfc8-813643a8e6fe	UPDATE	{"id": "5e78c323-d594-4845-bfc8-813643a8e6fe", "status": "ISSUED", "seat_id": "1129090f-3c21-49d4-b882-b3c62f54be1a", "qr_nonce": "b37d821829b44c7fa674bb286599420b", "seat_row": "B", "issued_at": "2026-07-30T15:49:20.942537+00:00", "scan_code": "Q855FD594042", "booking_id": "d210f403-2fdd-4583-8e18-8cb7034c1a7d", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731008-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c45ad659-7b0d-4f71-8d1e-e374b3ebd603", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "5e78c323-d594-4845-bfc8-813643a8e6fe", "status": "ISSUED", "seat_id": "1129090f-3c21-49d4-b882-b3c62f54be1a", "qr_nonce": "b37d821829b44c7fa674bb286599420b", "seat_row": "B", "issued_at": "2026-07-30T15:49:20.942537+00:00", "scan_code": null, "booking_id": "d210f403-2fdd-4583-8e18-8cb7034c1a7d", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731008-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c45ad659-7b0d-4f71-8d1e-e374b3ebd603", "pricing_details": {}}
9ae4ea9e-a437-493d-98e0-3128bda5eb12	tickets	21042024-b534-4b59-a9cb-4dbf9011de88	UPDATE	{"id": "21042024-b534-4b59-a9cb-4dbf9011de88", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "ee1ab763544243dc979c794b649fe23c", "seat_row": "A", "issued_at": "2026-07-30T16:14:39.110867+00:00", "scan_code": "Q0292FBCB2D7", "booking_id": "8eb7e27f-5167-4c41-81a0-cde73361f10f", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260731009-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "8a8620dd-a9f7-4a4b-ad5e-915c57332708", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "21042024-b534-4b59-a9cb-4dbf9011de88", "status": "ISSUED", "seat_id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "qr_nonce": "ee1ab763544243dc979c794b649fe23c", "seat_row": "A", "issued_at": "2026-07-30T16:14:39.110867+00:00", "scan_code": null, "booking_id": "8eb7e27f-5167-4c41-81a0-cde73361f10f", "unit_price": 0.00, "seat_number": 12, "ticket_code": "C7260731009-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "8a8620dd-a9f7-4a4b-ad5e-915c57332708", "pricing_details": {}}
f675ebb4-01ba-4058-8722-79155e1e9238	booking_seats	20187e40-9bb5-4362-a873-29a6964a9235	DELETE	\N	1196	2026-08-10 06:31:47.505363+00	{"id": "20187e40-9bb5-4362-a873-29a6964a9235", "seat_id": "d6429f22-16aa-431d-bdce-02c74b61037f", "booking_id": "96505b30-69ca-4904-ad53-348258129a4d", "unit_price": 90000.00, "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "pricing_details": {"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}
9919a633-dedd-4a46-957b-a0a54045e025	tickets	19538c6d-d1fc-4312-914f-287ea82deb8c	UPDATE	{"id": "19538c6d-d1fc-4312-914f-287ea82deb8c", "status": "ISSUED", "seat_id": "1129090f-3c21-49d4-b882-b3c62f54be1a", "qr_nonce": "788a4eeb48f14fd3aec1de429f2d4587", "seat_row": "B", "issued_at": "2026-07-30T16:24:54.915754+00:00", "scan_code": "Q2EA27B4FB67", "booking_id": "3f3d7716-141f-4302-8093-5a9f1fc46235", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260801012-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c02b30ad-8dcc-4e14-aaf5-c00124ead6c2", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "19538c6d-d1fc-4312-914f-287ea82deb8c", "status": "ISSUED", "seat_id": "1129090f-3c21-49d4-b882-b3c62f54be1a", "qr_nonce": "788a4eeb48f14fd3aec1de429f2d4587", "seat_row": "B", "issued_at": "2026-07-30T16:24:54.915754+00:00", "scan_code": null, "booking_id": "3f3d7716-141f-4302-8093-5a9f1fc46235", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260801012-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c02b30ad-8dcc-4e14-aaf5-c00124ead6c2", "pricing_details": {}}
13d9e0eb-da1e-49e3-a436-49039889caf7	tickets	6ad4fb51-1e12-4deb-bc30-d5302cab3eec	UPDATE	{"id": "6ad4fb51-1e12-4deb-bc30-d5302cab3eec", "status": "ISSUED", "seat_id": "2ed79287-99c4-4923-8aa9-a9e39223ad74", "qr_nonce": "5c57ebc12b034a7e8ee74e4b444ec263", "seat_row": "A", "issued_at": "2026-07-30T18:27:32.166246+00:00", "scan_code": "QD43F0F0F9BB", "booking_id": "a4349175-2741-4061-be9a-d488c5fd959d", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260802002-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "fd350b19-ce60-4c65-b5db-f3c49a6e63ad", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "6ad4fb51-1e12-4deb-bc30-d5302cab3eec", "status": "ISSUED", "seat_id": "2ed79287-99c4-4923-8aa9-a9e39223ad74", "qr_nonce": "5c57ebc12b034a7e8ee74e4b444ec263", "seat_row": "A", "issued_at": "2026-07-30T18:27:32.166246+00:00", "scan_code": null, "booking_id": "a4349175-2741-4061-be9a-d488c5fd959d", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260802002-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "fd350b19-ce60-4c65-b5db-f3c49a6e63ad", "pricing_details": {}}
e7b218dc-9848-4a58-b62e-6eb1ebf7d623	tickets	83a3887e-5194-4c66-ba5e-762bc4213af1	UPDATE	{"id": "83a3887e-5194-4c66-ba5e-762bc4213af1", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "990dedbaec3143ed815bba9f6f8287bf", "seat_row": "A", "issued_at": "2026-07-30T18:27:32.166246+00:00", "scan_code": "QF25435B26E0", "booking_id": "a4349175-2741-4061-be9a-d488c5fd959d", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260802002-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "74b9c13a-17f2-47a7-b40a-69420dadb411", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "83a3887e-5194-4c66-ba5e-762bc4213af1", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "990dedbaec3143ed815bba9f6f8287bf", "seat_row": "A", "issued_at": "2026-07-30T18:27:32.166246+00:00", "scan_code": null, "booking_id": "a4349175-2741-4061-be9a-d488c5fd959d", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260802002-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "74b9c13a-17f2-47a7-b40a-69420dadb411", "pricing_details": {}}
118e438d-919f-4f26-9124-c55736a897d4	tickets	ec6a34f3-10a5-4f1e-997a-7e64b5ecabcb	UPDATE	{"id": "ec6a34f3-10a5-4f1e-997a-7e64b5ecabcb", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "6a1d68fa2c754a629539e2bdd0bc72e1", "seat_row": "A", "issued_at": "2026-07-30T18:55:04.577309+00:00", "scan_code": "QA032D033A82", "booking_id": "6bbd507d-85d0-4298-ab5f-73845dc0a90a", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731011-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "85aa6f1c-7f02-48e6-8ee7-13ca0489635c", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "ec6a34f3-10a5-4f1e-997a-7e64b5ecabcb", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "6a1d68fa2c754a629539e2bdd0bc72e1", "seat_row": "A", "issued_at": "2026-07-30T18:55:04.577309+00:00", "scan_code": null, "booking_id": "6bbd507d-85d0-4298-ab5f-73845dc0a90a", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731011-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "85aa6f1c-7f02-48e6-8ee7-13ca0489635c", "pricing_details": {}}
5c9aa63b-f872-415d-b9b1-510c2170e3cc	tickets	ee08fe06-4050-4782-83cb-bbb98c797617	UPDATE	{"id": "ee08fe06-4050-4782-83cb-bbb98c797617", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "6004a0f603144303b5b581c14f24dc35", "seat_row": "A", "issued_at": "2026-07-30T19:05:28.817411+00:00", "scan_code": "Q8196023D84A", "booking_id": "1fcbccd3-6e37-46b3-b44d-4d0f5fed1550", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731012-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "8533ee26-1b29-497e-84a9-29aa227268d7", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "ee08fe06-4050-4782-83cb-bbb98c797617", "status": "ISSUED", "seat_id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "qr_nonce": "6004a0f603144303b5b581c14f24dc35", "seat_row": "A", "issued_at": "2026-07-30T19:05:28.817411+00:00", "scan_code": null, "booking_id": "1fcbccd3-6e37-46b3-b44d-4d0f5fed1550", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260731012-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "8533ee26-1b29-497e-84a9-29aa227268d7", "pricing_details": {}}
d95021eb-8f37-41b3-ab7b-27ff6d5ce345	tickets	ab4aa497-5a3c-462e-a60a-aae5d0dba7bc	UPDATE	{"id": "ab4aa497-5a3c-462e-a60a-aae5d0dba7bc", "status": "ISSUED", "seat_id": "03efca4b-c0a2-45b8-8212-fbc109c90f90", "qr_nonce": "ee6b94e5b1b94058b43941b02bd77bfb", "seat_row": "A", "issued_at": "2026-07-30T19:15:33.916256+00:00", "scan_code": "Q5133BEDCA61", "booking_id": "4ab4de29-b4a0-474b-ac6b-fb4c2ee06d75", "unit_price": 0.00, "seat_number": 6, "ticket_code": "C7260731013-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "38d6ce79-923c-4e86-afdb-d15f0793014b", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "ab4aa497-5a3c-462e-a60a-aae5d0dba7bc", "status": "ISSUED", "seat_id": "03efca4b-c0a2-45b8-8212-fbc109c90f90", "qr_nonce": "ee6b94e5b1b94058b43941b02bd77bfb", "seat_row": "A", "issued_at": "2026-07-30T19:15:33.916256+00:00", "scan_code": null, "booking_id": "4ab4de29-b4a0-474b-ac6b-fb4c2ee06d75", "unit_price": 0.00, "seat_number": 6, "ticket_code": "C7260731013-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "38d6ce79-923c-4e86-afdb-d15f0793014b", "pricing_details": {}}
54970e47-c20f-4fbb-a9b5-7dfa7080594f	booking_seats	7790d26b-abb7-4eb4-8d7b-654ee850e193	INSERT	{"id": "7790d26b-abb7-4eb4-8d7b-654ee850e193", "seat_id": "5042eca3-dfaa-4f3c-a99b-390eb2bd346f", "booking_id": "9257dcad-0488-420e-a6eb-be52650d2702", "unit_price": 90000.00, "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "pricing_details": {"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1209	2026-08-10 06:44:09.836032+00	\N
54139b6e-df19-4fae-a739-65c13aa1a960	tickets	d1fccd97-c073-46a5-b175-c2669e48387b	UPDATE	{"id": "d1fccd97-c073-46a5-b175-c2669e48387b", "status": "ISSUED", "seat_id": "e57ad5e9-f5ab-480f-9153-7dfa510e2a70", "qr_nonce": "c704d2bfa8da41648f657ead828171df", "seat_row": "B", "issued_at": "2026-07-30T19:39:25.528573+00:00", "scan_code": "Q337F29EB32C", "booking_id": "85a22a13-c8ac-48f5-b50c-a8b9a22b2f10", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260801014-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c98be923-4081-4696-b4fc-a7e76ff6dc30", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "d1fccd97-c073-46a5-b175-c2669e48387b", "status": "ISSUED", "seat_id": "e57ad5e9-f5ab-480f-9153-7dfa510e2a70", "qr_nonce": "c704d2bfa8da41648f657ead828171df", "seat_row": "B", "issued_at": "2026-07-30T19:39:25.528573+00:00", "scan_code": null, "booking_id": "85a22a13-c8ac-48f5-b50c-a8b9a22b2f10", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260801014-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c98be923-4081-4696-b4fc-a7e76ff6dc30", "pricing_details": {}}
6aa448bc-8eb7-480b-ad86-49566e33ea9c	tickets	86576948-5bfe-4725-87f5-59056dcd886d	UPDATE	{"id": "86576948-5bfe-4725-87f5-59056dcd886d", "status": "ISSUED", "seat_id": "1129090f-3c21-49d4-b882-b3c62f54be1a", "qr_nonce": "ce27686e487b410ea8342463e7a51d51", "seat_row": "B", "issued_at": "2026-07-30T19:39:25.528573+00:00", "scan_code": "Q9DBD96BFFDF", "booking_id": "85a22a13-c8ac-48f5-b50c-a8b9a22b2f10", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260801014-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "b9c64734-2cdf-4f43-981d-9a58c894c219", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "86576948-5bfe-4725-87f5-59056dcd886d", "status": "ISSUED", "seat_id": "1129090f-3c21-49d4-b882-b3c62f54be1a", "qr_nonce": "ce27686e487b410ea8342463e7a51d51", "seat_row": "B", "issued_at": "2026-07-30T19:39:25.528573+00:00", "scan_code": null, "booking_id": "85a22a13-c8ac-48f5-b50c-a8b9a22b2f10", "unit_price": 0.00, "seat_number": 11, "ticket_code": "C7260801014-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "b9c64734-2cdf-4f43-981d-9a58c894c219", "pricing_details": {}}
5e5c7fe4-f152-420d-8852-fb570bcbff4b	tickets	828a7286-9d0c-4277-a1aa-d8ebfd508bb2	UPDATE	{"id": "828a7286-9d0c-4277-a1aa-d8ebfd508bb2", "status": "ISSUED", "seat_id": "2ed79287-99c4-4923-8aa9-a9e39223ad74", "qr_nonce": "bdb08131a2af42aa808fe6f722e65be5", "seat_row": "A", "issued_at": "2026-07-30T19:42:47.515884+00:00", "scan_code": "QE80B54F2035", "booking_id": "651d5cb6-a9bd-48ad-9404-09ab5e0ee935", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260731014-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "7a5be13f-e937-493a-b716-fd83929df431", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "828a7286-9d0c-4277-a1aa-d8ebfd508bb2", "status": "ISSUED", "seat_id": "2ed79287-99c4-4923-8aa9-a9e39223ad74", "qr_nonce": "bdb08131a2af42aa808fe6f722e65be5", "seat_row": "A", "issued_at": "2026-07-30T19:42:47.515884+00:00", "scan_code": null, "booking_id": "651d5cb6-a9bd-48ad-9404-09ab5e0ee935", "unit_price": 0.00, "seat_number": 10, "ticket_code": "C7260731014-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "7a5be13f-e937-493a-b716-fd83929df431", "pricing_details": {}}
5ed6d94e-68ef-4431-b3ae-c77d7183a298	tickets	f264ea85-6d96-4862-9f9a-35d0c44eb5eb	UPDATE	{"id": "f264ea85-6d96-4862-9f9a-35d0c44eb5eb", "status": "ISSUED", "seat_id": "dc6f6ebd-0e3f-4a29-aa3b-52f5535b8029", "qr_nonce": "ef33e13805a54aef9e3051394a88740f", "seat_row": "C", "issued_at": "2026-08-02T12:20:10.50569+00:00", "scan_code": "Q69B00E0B080", "booking_id": "9ce23bfc-f82f-4df3-bcb0-d520925f6c98", "unit_price": 0.00, "seat_number": 7, "ticket_code": "C7260803001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "5a5e5ff1-06f7-4459-ab3d-20a0462b227c", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "f264ea85-6d96-4862-9f9a-35d0c44eb5eb", "status": "ISSUED", "seat_id": "dc6f6ebd-0e3f-4a29-aa3b-52f5535b8029", "qr_nonce": "ef33e13805a54aef9e3051394a88740f", "seat_row": "C", "issued_at": "2026-08-02T12:20:10.50569+00:00", "scan_code": null, "booking_id": "9ce23bfc-f82f-4df3-bcb0-d520925f6c98", "unit_price": 0.00, "seat_number": 7, "ticket_code": "C7260803001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "5a5e5ff1-06f7-4459-ab3d-20a0462b227c", "pricing_details": {}}
e44c4e03-cea7-4144-9c6c-638b767979fc	tickets	ff1dc471-18b3-40ad-8330-3703ffcf730b	UPDATE	{"id": "ff1dc471-18b3-40ad-8330-3703ffcf730b", "status": "ISSUED", "seat_id": "ee3f6974-b9a2-4808-9dd5-7ec4d7cfb5fb", "qr_nonce": "d7b27e80fc9944e087b79e0ffb3e216d", "seat_row": "C", "issued_at": "2026-08-02T12:20:10.50569+00:00", "scan_code": "Q340D150F9F0", "booking_id": "9ce23bfc-f82f-4df3-bcb0-d520925f6c98", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260803001-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "4b91f56f-0e7f-4a46-bc95-2aa778892ad2", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "ff1dc471-18b3-40ad-8330-3703ffcf730b", "status": "ISSUED", "seat_id": "ee3f6974-b9a2-4808-9dd5-7ec4d7cfb5fb", "qr_nonce": "d7b27e80fc9944e087b79e0ffb3e216d", "seat_row": "C", "issued_at": "2026-08-02T12:20:10.50569+00:00", "scan_code": null, "booking_id": "9ce23bfc-f82f-4df3-bcb0-d520925f6c98", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260803001-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "4b91f56f-0e7f-4a46-bc95-2aa778892ad2", "pricing_details": {}}
7a917437-65b5-46ce-8a0b-3056fecdd121	tickets	09611a32-e7aa-460b-be1c-d9fb7251d9fb	UPDATE	{"id": "09611a32-e7aa-460b-be1c-d9fb7251d9fb", "status": "USED", "seat_id": "51fe1dd3-cf0f-4858-9f2b-0b548ce8d52e", "qr_nonce": "5121c3a01c96460f8f2f2b9cc68e71f4", "seat_row": "D", "issued_at": "2026-08-04T14:53:28.779915+00:00", "scan_code": "Q2F83AB69ADE", "booking_id": "2a5ef731-b92b-4fec-98e0-7ee13ca2bdf2", "unit_price": 0.00, "seat_number": 7, "ticket_code": "C7260807001-01", "checked_in_at": "2026-08-05T16:12:06.206065+00:00", "checked_in_by": "2810314c-85d7-46e5-8449-e69ec5ad3285", "booking_seat_id": "1c8b9577-f22b-4d90-a97a-8cf00344c542", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "09611a32-e7aa-460b-be1c-d9fb7251d9fb", "status": "USED", "seat_id": "51fe1dd3-cf0f-4858-9f2b-0b548ce8d52e", "qr_nonce": "5121c3a01c96460f8f2f2b9cc68e71f4", "seat_row": "D", "issued_at": "2026-08-04T14:53:28.779915+00:00", "scan_code": null, "booking_id": "2a5ef731-b92b-4fec-98e0-7ee13ca2bdf2", "unit_price": 0.00, "seat_number": 7, "ticket_code": "C7260807001-01", "checked_in_at": "2026-08-05T16:12:06.206065+00:00", "checked_in_by": "2810314c-85d7-46e5-8449-e69ec5ad3285", "booking_seat_id": "1c8b9577-f22b-4d90-a97a-8cf00344c542", "pricing_details": {}}
e4498890-2093-4dfe-9a70-81c4d4ad2ea8	tickets	a65b90fe-f826-4eb8-bf7f-fd6f0f06fe63	INSERT	{"id": "a65b90fe-f826-4eb8-bf7f-fd6f0f06fe63", "status": "ISSUED", "seat_id": "c9583494-ebc9-43df-a5ed-fc88cf553f0e", "qr_nonce": "4e5d9b41d57467fc12878e7abc177fc6", "seat_row": "C", "issued_at": "2026-08-10T08:15:28.126576+00:00", "scan_code": "Q9C10SOZCZAW", "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "unit_price": 120000.00, "seat_number": 6, "ticket_code": "C7260811001-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "9b5d7da7-334f-4d35-9245-7a996473f7ff", "pricing_details": {"surcharge": "0", "base_price": "120000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1243	2026-08-10 08:15:28.126576+00	\N
aaa0c9e4-0f7b-4924-86eb-fc3ea3b7caf5	tickets	2bf8a8a0-b246-4f6a-a00d-7bac0664c795	UPDATE	{"id": "2bf8a8a0-b246-4f6a-a00d-7bac0664c795", "status": "USED", "seat_id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "qr_nonce": "08b7d8d14c2b4c59aa41c02da8d0a521", "seat_row": "D", "issued_at": "2026-08-04T14:53:28.779915+00:00", "scan_code": "Q80EAF878066", "booking_id": "2a5ef731-b92b-4fec-98e0-7ee13ca2bdf2", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260807001-02", "checked_in_at": "2026-08-05T16:12:06.206065+00:00", "checked_in_by": "2810314c-85d7-46e5-8449-e69ec5ad3285", "booking_seat_id": "aba62010-f054-48ff-9a93-6aeed2feacbf", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "2bf8a8a0-b246-4f6a-a00d-7bac0664c795", "status": "USED", "seat_id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "qr_nonce": "08b7d8d14c2b4c59aa41c02da8d0a521", "seat_row": "D", "issued_at": "2026-08-04T14:53:28.779915+00:00", "scan_code": null, "booking_id": "2a5ef731-b92b-4fec-98e0-7ee13ca2bdf2", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260807001-02", "checked_in_at": "2026-08-05T16:12:06.206065+00:00", "checked_in_by": "2810314c-85d7-46e5-8449-e69ec5ad3285", "booking_seat_id": "aba62010-f054-48ff-9a93-6aeed2feacbf", "pricing_details": {}}
cade0e23-c022-4545-80a0-bee0a85fc568	tickets	2e4c49f8-e6f4-4331-95b2-10fb88427cee	UPDATE	{"id": "2e4c49f8-e6f4-4331-95b2-10fb88427cee", "status": "ISSUED", "seat_id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "qr_nonce": "f4825024f079455f9ae5bbedef06a2bb", "seat_row": "D", "issued_at": "2026-08-06T12:12:36.938116+00:00", "scan_code": "QBEAE0687ECA", "booking_id": "533600da-cf60-4155-b812-c255add2ef45", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260807002-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "55bf09ae-4525-44b1-bf51-cbc90682cd50", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "2e4c49f8-e6f4-4331-95b2-10fb88427cee", "status": "ISSUED", "seat_id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "qr_nonce": "f4825024f079455f9ae5bbedef06a2bb", "seat_row": "D", "issued_at": "2026-08-06T12:12:36.938116+00:00", "scan_code": null, "booking_id": "533600da-cf60-4155-b812-c255add2ef45", "unit_price": 0.00, "seat_number": 8, "ticket_code": "C7260807002-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "55bf09ae-4525-44b1-bf51-cbc90682cd50", "pricing_details": {}}
f974e998-a071-4e7f-b87a-905f793d604d	tickets	75e6d425-42c2-49b7-bf9d-fcad40a2cb75	UPDATE	{"id": "75e6d425-42c2-49b7-bf9d-fcad40a2cb75", "status": "ISSUED", "seat_id": "77e0c246-d4ce-46f5-bc39-c58fa01b46d3", "qr_nonce": "ebdc50b7069f42dc96852ad92f00b5ec", "seat_row": "D", "issued_at": "2026-08-06T12:12:36.938116+00:00", "scan_code": "Q73AFA424DCE", "booking_id": "533600da-cf60-4155-b812-c255add2ef45", "unit_price": 0.00, "seat_number": 9, "ticket_code": "C7260807002-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "44a2a193-fd2f-4aae-b667-6ab7d964fc42", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "75e6d425-42c2-49b7-bf9d-fcad40a2cb75", "status": "ISSUED", "seat_id": "77e0c246-d4ce-46f5-bc39-c58fa01b46d3", "qr_nonce": "ebdc50b7069f42dc96852ad92f00b5ec", "seat_row": "D", "issued_at": "2026-08-06T12:12:36.938116+00:00", "scan_code": null, "booking_id": "533600da-cf60-4155-b812-c255add2ef45", "unit_price": 0.00, "seat_number": 9, "ticket_code": "C7260807002-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "44a2a193-fd2f-4aae-b667-6ab7d964fc42", "pricing_details": {}}
ed459412-3e77-4d14-9858-e90f14758031	tickets	4780f9ba-11aa-4fc6-8f5f-da8c563e01d8	UPDATE	{"id": "4780f9ba-11aa-4fc6-8f5f-da8c563e01d8", "status": "USED", "seat_id": "7191355f-e232-4000-8daa-22c407f8aae5", "qr_nonce": "969697b66c464a0fbafa557211849f01", "seat_row": "D", "issued_at": "2026-08-07T09:02:40.443031+00:00", "scan_code": "Q4D4D814D21C", "booking_id": "b23ea768-02e2-4241-90a7-fcc4c22d1dd2", "unit_price": 0.00, "seat_number": 6, "ticket_code": "C7260808001-01", "checked_in_at": "2026-08-07T09:07:21.172817+00:00", "checked_in_by": "2810314c-85d7-46e5-8449-e69ec5ad3285", "booking_seat_id": "1123d3ff-0e13-4d52-bd19-e60313ba5635", "pricing_details": {}}	1169	2026-08-10 05:40:43.310257+00	{"id": "4780f9ba-11aa-4fc6-8f5f-da8c563e01d8", "status": "USED", "seat_id": "7191355f-e232-4000-8daa-22c407f8aae5", "qr_nonce": "969697b66c464a0fbafa557211849f01", "seat_row": "D", "issued_at": "2026-08-07T09:02:40.443031+00:00", "scan_code": null, "booking_id": "b23ea768-02e2-4241-90a7-fcc4c22d1dd2", "unit_price": 0.00, "seat_number": 6, "ticket_code": "C7260808001-01", "checked_in_at": "2026-08-07T09:07:21.172817+00:00", "checked_in_by": "2810314c-85d7-46e5-8449-e69ec5ad3285", "booking_seat_id": "1123d3ff-0e13-4d52-bd19-e60313ba5635", "pricing_details": {}}
2dabd45f-cf49-43db-bdd6-b319f682efe9	bookings	a72593a3-4040-4aa9-a352-3f050a6faf31	INSERT	{"id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "status": "PENDING", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:00:14.761799+00:00", "expires_at": "2026-08-10T06:05:14.826557+00:00", "updated_at": "2026-08-10T06:00:14.761799+00:00", "showtime_id": "ab06927c-77e3-4cc7-8108-cb8789e5c5e7", "ticket_code": null, "total_price": 279000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 279000.00, "discount_amount": 0.00, "idempotency_key": "booking-b7f215d3-9da6-4cdd-b830-88f2ebd8746a", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1181	2026-08-10 06:00:14.761799+00	\N
d654b9b7-1579-4928-be6a-ff5b63562e8b	booking_combos	d7f7c56b-8ffd-4c98-a873-79509fac8c0b	INSERT	{"id": "d7f7c56b-8ffd-4c98-a873-79509fac8c0b", "combo_id": "b351e22a-056e-4553-a991-96080254bf49", "quantity": 1, "booking_id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "combo_name": "Combo Couple", "line_total": 129000.00, "unit_price": 129000.00, "inventory_status": "RESERVED"}	1181	2026-08-10 06:00:14.761799+00	\N
48ac1ba8-0dee-4e52-822b-8476820541df	booking_seats	f839faf8-79b6-4fa9-a3b4-53d763b8b5bd	INSERT	{"id": "f839faf8-79b6-4fa9-a3b4-53d763b8b5bd", "seat_id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "booking_id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "unit_price": 150000.00, "showtime_id": "ab06927c-77e3-4cc7-8108-cb8789e5c5e7", "pricing_details": {"surcharge": "0", "base_price": "120000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.25"}}	1181	2026-08-10 06:00:14.761799+00	\N
8ad6415d-26bd-4383-bfbf-d670d58d8ae0	payments	a6d2bd6f-a050-4101-a034-e6dbdd22c111	INSERT	{"id": "a6d2bd6f-a050-4101-a034-e6dbdd22c111", "amount": 279000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "created_at": "2026-08-10T06:00:14.930387+00:00", "updated_at": "2026-08-10T06:00:14.930387+00:00", "refunded_at": null, "checkout_url": null, "provider_ref": "a6d2bd6fa0504101a034e6dbdd22c111", "refund_error": null, "response_code": null, "payment_method": "VNPAY", "transaction_id": null, "idempotency_key": "payment-b7f215d3-9da6-4cdd-b830-88f2ebd8746a", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}	1182	2026-08-10 06:00:14.930387+00	\N
5aefffef-6462-46e4-8fa9-63ab4de670bc	payments	a6d2bd6f-a050-4101-a034-e6dbdd22c111	UPDATE	{"id": "a6d2bd6f-a050-4101-a034-e6dbdd22c111", "amount": 279000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "created_at": "2026-08-10T06:00:14.930387+00:00", "updated_at": "2026-08-10T06:00:14.930387+00:00", "refunded_at": null, "checkout_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?vnp_Amount=27900000&vnp_Command=pay&vnp_CreateDate=20260810130015&vnp_CurrCode=VND&vnp_ExpireDate=20260810130514&vnp_IpAddr=172.18.0.1&vnp_Locale=vn&vnp_OrderInfo=Thanh+toan+ve+CineAI+a72593a3-4040-4aa9-a352-3f050a6faf31&vnp_OrderType=other&vnp_ReturnUrl=https%3A%2F%2Fexacting-glenda-usurpingly.ngrok-free.dev%2Fcheckout%2Fvnpay-return&vnp_TmnCode=T3X2ZW00&vnp_TxnRef=a6d2bd6fa0504101a034e6dbdd22c111&vnp_Version=2.1.0&vnp_SecureHash=f514f9b4513f11c904991709c8b76355133b6faa1f02e73f819e7a0a41621e0c47aff0acf7bdfc75c9fa633cc9f859b9dd207597804c0e2334e670b7676efd1c", "provider_ref": "a6d2bd6fa0504101a034e6dbdd22c111", "refund_error": null, "response_code": null, "payment_method": "VNPAY", "transaction_id": null, "idempotency_key": "payment-b7f215d3-9da6-4cdd-b830-88f2ebd8746a", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}	1182	2026-08-10 06:00:14.930387+00	{"id": "a6d2bd6f-a050-4101-a034-e6dbdd22c111", "amount": 279000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "created_at": "2026-08-10T06:00:14.930387+00:00", "updated_at": "2026-08-10T06:00:14.930387+00:00", "refunded_at": null, "checkout_url": null, "provider_ref": "a6d2bd6fa0504101a034e6dbdd22c111", "refund_error": null, "response_code": null, "payment_method": "VNPAY", "transaction_id": null, "idempotency_key": "payment-b7f215d3-9da6-4cdd-b830-88f2ebd8746a", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}
fcf1418d-4f30-4462-a0ef-c7670fe9f2cd	bookings	a72593a3-4040-4aa9-a352-3f050a6faf31	UPDATE	{"id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "status": "CONFIRMED", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:00:14.761799+00:00", "expires_at": "2026-08-10T06:05:14.826557+00:00", "updated_at": "2026-08-10T06:00:45.727464+00:00", "showtime_id": "ab06927c-77e3-4cc7-8108-cb8789e5c5e7", "ticket_code": null, "total_price": 279000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 279000.00, "discount_amount": 0.00, "idempotency_key": "booking-b7f215d3-9da6-4cdd-b830-88f2ebd8746a", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1183	2026-08-10 06:00:45.727464+00	{"id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "status": "PENDING", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:00:14.761799+00:00", "expires_at": "2026-08-10T06:05:14.826557+00:00", "updated_at": "2026-08-10T06:00:14.761799+00:00", "showtime_id": "ab06927c-77e3-4cc7-8108-cb8789e5c5e7", "ticket_code": null, "total_price": 279000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 279000.00, "discount_amount": 0.00, "idempotency_key": "booking-b7f215d3-9da6-4cdd-b830-88f2ebd8746a", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}
781996b1-5e4a-42a5-bff0-aa1896d615ba	payments	a6d2bd6f-a050-4101-a034-e6dbdd22c111	UPDATE	{"id": "a6d2bd6f-a050-4101-a034-e6dbdd22c111", "amount": 279000.00, "status": "SUCCESS", "paid_at": "2026-08-10T06:00:45.840138+00:00", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": "NCB", "card_type": "ATM", "booking_id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "created_at": "2026-08-10T06:00:14.930387+00:00", "updated_at": "2026-08-10T06:00:45.727464+00:00", "refunded_at": null, "checkout_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?vnp_Amount=27900000&vnp_Command=pay&vnp_CreateDate=20260810130015&vnp_CurrCode=VND&vnp_ExpireDate=20260810130514&vnp_IpAddr=172.18.0.1&vnp_Locale=vn&vnp_OrderInfo=Thanh+toan+ve+CineAI+a72593a3-4040-4aa9-a352-3f050a6faf31&vnp_OrderType=other&vnp_ReturnUrl=https%3A%2F%2Fexacting-glenda-usurpingly.ngrok-free.dev%2Fcheckout%2Fvnpay-return&vnp_TmnCode=T3X2ZW00&vnp_TxnRef=a6d2bd6fa0504101a034e6dbdd22c111&vnp_Version=2.1.0&vnp_SecureHash=f514f9b4513f11c904991709c8b76355133b6faa1f02e73f819e7a0a41621e0c47aff0acf7bdfc75c9fa633cc9f859b9dd207597804c0e2334e670b7676efd1c", "provider_ref": "a6d2bd6fa0504101a034e6dbdd22c111", "refund_error": null, "response_code": "00", "payment_method": "VNPAY", "transaction_id": "15651555", "idempotency_key": "payment-b7f215d3-9da6-4cdd-b830-88f2ebd8746a", "provider_status": "00", "refund_attempts": 0, "signature_valid": true, "last_verified_at": null, "provider_paid_at": "2026-08-10T06:00:40+00:00", "refund_request_id": null, "bank_transaction_no": "VNP15651555", "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": "15651555"}	1183	2026-08-10 06:00:45.727464+00	{"id": "a6d2bd6f-a050-4101-a034-e6dbdd22c111", "amount": 279000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "created_at": "2026-08-10T06:00:14.930387+00:00", "updated_at": "2026-08-10T06:00:14.930387+00:00", "refunded_at": null, "checkout_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?vnp_Amount=27900000&vnp_Command=pay&vnp_CreateDate=20260810130015&vnp_CurrCode=VND&vnp_ExpireDate=20260810130514&vnp_IpAddr=172.18.0.1&vnp_Locale=vn&vnp_OrderInfo=Thanh+toan+ve+CineAI+a72593a3-4040-4aa9-a352-3f050a6faf31&vnp_OrderType=other&vnp_ReturnUrl=https%3A%2F%2Fexacting-glenda-usurpingly.ngrok-free.dev%2Fcheckout%2Fvnpay-return&vnp_TmnCode=T3X2ZW00&vnp_TxnRef=a6d2bd6fa0504101a034e6dbdd22c111&vnp_Version=2.1.0&vnp_SecureHash=f514f9b4513f11c904991709c8b76355133b6faa1f02e73f819e7a0a41621e0c47aff0acf7bdfc75c9fa633cc9f859b9dd207597804c0e2334e670b7676efd1c", "provider_ref": "a6d2bd6fa0504101a034e6dbdd22c111", "refund_error": null, "response_code": null, "payment_method": "VNPAY", "transaction_id": null, "idempotency_key": "payment-b7f215d3-9da6-4cdd-b830-88f2ebd8746a", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}
5c4e792c-55c4-4703-a35c-6e23b6e11912	booking_combos	d7f7c56b-8ffd-4c98-a873-79509fac8c0b	UPDATE	{"id": "d7f7c56b-8ffd-4c98-a873-79509fac8c0b", "combo_id": "b351e22a-056e-4553-a991-96080254bf49", "quantity": 1, "booking_id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "combo_name": "Combo Couple", "line_total": 129000.00, "unit_price": 129000.00, "inventory_status": "SOLD"}	1183	2026-08-10 06:00:45.727464+00	{"id": "d7f7c56b-8ffd-4c98-a873-79509fac8c0b", "combo_id": "b351e22a-056e-4553-a991-96080254bf49", "quantity": 1, "booking_id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "combo_name": "Combo Couple", "line_total": 129000.00, "unit_price": 129000.00, "inventory_status": "RESERVED"}
21b1de32-547a-40d9-991c-c2ed2b6dcf8a	bookings	a72593a3-4040-4aa9-a352-3f050a6faf31	UPDATE	{"id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "status": "CONFIRMED", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:00:14.761799+00:00", "expires_at": "2026-08-10T06:05:14.826557+00:00", "updated_at": "2026-08-10T06:00:45.727464+00:00", "showtime_id": "ab06927c-77e3-4cc7-8108-cb8789e5c5e7", "ticket_code": "C7260810001", "total_price": 279000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 279000.00, "discount_amount": 0.00, "idempotency_key": "booking-b7f215d3-9da6-4cdd-b830-88f2ebd8746a", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1183	2026-08-10 06:00:45.727464+00	{"id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "status": "CONFIRMED", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:00:14.761799+00:00", "expires_at": "2026-08-10T06:05:14.826557+00:00", "updated_at": "2026-08-10T06:00:45.727464+00:00", "showtime_id": "ab06927c-77e3-4cc7-8108-cb8789e5c5e7", "ticket_code": null, "total_price": 279000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 279000.00, "discount_amount": 0.00, "idempotency_key": "booking-b7f215d3-9da6-4cdd-b830-88f2ebd8746a", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}
86650252-bc63-4f50-b05c-33939904470c	tickets	597a133d-a459-4f13-82ac-addda1405810	INSERT	{"id": "597a133d-a459-4f13-82ac-addda1405810", "status": "ISSUED", "seat_id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "qr_nonce": "e0b1210a6fd3eded5a5b83b5caa4955e", "seat_row": "D", "issued_at": "2026-08-10T06:00:45.727464+00:00", "scan_code": "QXKQCW9SCQEQ", "booking_id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "unit_price": 150000.00, "seat_number": 8, "ticket_code": "C7260810001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "f839faf8-79b6-4fa9-a3b4-53d763b8b5bd", "pricing_details": {"surcharge": "0", "base_price": "120000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.25"}}	1183	2026-08-10 06:00:45.727464+00	\N
b06fbb8d-2d96-4f58-941d-490920c7bd67	bookings	96505b30-69ca-4904-ad53-348258129a4d	INSERT	{"id": "96505b30-69ca-4904-ad53-348258129a4d", "status": "PENDING", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:26:43.302779+00:00", "expires_at": "2026-08-10T06:31:43.471669+00:00", "updated_at": "2026-08-10T06:26:43.302779+00:00", "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "ticket_code": null, "total_price": 149000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 149000.00, "discount_amount": 0.00, "idempotency_key": "booking-11825d2f-bc51-4a80-bcdb-9cabd65deaf3", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1193	2026-08-10 06:26:43.302779+00	\N
35e69d80-a088-4bbe-9456-20847c4ba46e	booking_combos	782f4d3b-676e-44c6-977b-c190b89649b6	INSERT	{"id": "782f4d3b-676e-44c6-977b-c190b89649b6", "combo_id": "9b2db4b2-323b-4b56-9890-661b096fc619", "quantity": 1, "booking_id": "96505b30-69ca-4904-ad53-348258129a4d", "combo_name": "Combo Kids", "line_total": 59000.00, "unit_price": 59000.00, "inventory_status": "RESERVED"}	1193	2026-08-10 06:26:43.302779+00	\N
cbb669d6-fb53-4bc0-9bd6-726d99fe3c04	bookings	96505b30-69ca-4904-ad53-348258129a4d	UPDATE	{"id": "96505b30-69ca-4904-ad53-348258129a4d", "status": "EXPIRED", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:26:43.302779+00:00", "expires_at": "2026-08-10T06:31:43.471669+00:00", "updated_at": "2026-08-10T06:31:47.505363+00:00", "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "ticket_code": null, "total_price": 149000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [{"id": "d6429f22-16aa-431d-bdce-02c74b61037f", "row": "A", "number": 8}], "customer_email": null, "customer_phone": null, "subtotal_price": 149000.00, "discount_amount": 0.00, "idempotency_key": "booking-11825d2f-bc51-4a80-bcdb-9cabd65deaf3", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1196	2026-08-10 06:31:47.505363+00	{"id": "96505b30-69ca-4904-ad53-348258129a4d", "status": "PENDING", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:26:43.302779+00:00", "expires_at": "2026-08-10T06:31:43.471669+00:00", "updated_at": "2026-08-10T06:26:43.302779+00:00", "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "ticket_code": null, "total_price": 149000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 149000.00, "discount_amount": 0.00, "idempotency_key": "booking-11825d2f-bc51-4a80-bcdb-9cabd65deaf3", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}
48d8c976-b546-41c7-b94d-27f3f0ad484f	bookings	2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7	INSERT	{"id": "2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7", "status": "PENDING", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:36:40.928178+00:00", "expires_at": "2026-08-10T06:41:41.105929+00:00", "updated_at": "2026-08-10T06:36:40.928178+00:00", "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "ticket_code": null, "total_price": 90000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 90000.00, "discount_amount": 0.00, "idempotency_key": "booking-b2469d28-f2d3-4edf-9f53-d5d848da5bb8", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1200	2026-08-10 06:36:40.928178+00	\N
365c11b8-f0a5-4c25-bd25-6cf14f7ae5e7	booking_seats	fea69643-4b6a-4ea1-be4e-6b380ba56845	INSERT	{"id": "fea69643-4b6a-4ea1-be4e-6b380ba56845", "seat_id": "d9cc21ac-906f-467c-8b48-d1cc107c03d6", "booking_id": "2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7", "unit_price": 90000.00, "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "pricing_details": {"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1200	2026-08-10 06:36:40.928178+00	\N
c0a47000-156c-4b1a-bc01-f9a59af54367	payments	714ec43c-14d2-4ff2-b138-ad80b163c92f	INSERT	{"id": "714ec43c-14d2-4ff2-b138-ad80b163c92f", "amount": 90000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7", "created_at": "2026-08-10T06:36:43.330425+00:00", "updated_at": "2026-08-10T06:36:43.330425+00:00", "refunded_at": null, "checkout_url": null, "provider_ref": null, "refund_error": null, "response_code": null, "payment_method": "PAYPAL", "transaction_id": null, "idempotency_key": "payment-b2469d28-f2d3-4edf-9f53-d5d848da5bb8", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}	1201	2026-08-10 06:36:43.330425+00	\N
cafe6b3c-58a6-46cf-a079-5e5d94e74e6e	payments	714ec43c-14d2-4ff2-b138-ad80b163c92f	UPDATE	{"id": "714ec43c-14d2-4ff2-b138-ad80b163c92f", "amount": 90000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7", "created_at": "2026-08-10T06:36:43.330425+00:00", "updated_at": "2026-08-10T06:36:43.330425+00:00", "refunded_at": null, "checkout_url": "https://www.sandbox.paypal.com/checkoutnow?token=2VS37002Y1970705T", "provider_ref": "2VS37002Y1970705T", "refund_error": null, "response_code": null, "payment_method": "PAYPAL", "transaction_id": null, "idempotency_key": "payment-b2469d28-f2d3-4edf-9f53-d5d848da5bb8", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}	1201	2026-08-10 06:36:43.330425+00	{"id": "714ec43c-14d2-4ff2-b138-ad80b163c92f", "amount": 90000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7", "created_at": "2026-08-10T06:36:43.330425+00:00", "updated_at": "2026-08-10T06:36:43.330425+00:00", "refunded_at": null, "checkout_url": null, "provider_ref": null, "refund_error": null, "response_code": null, "payment_method": "PAYPAL", "transaction_id": null, "idempotency_key": "payment-b2469d28-f2d3-4edf-9f53-d5d848da5bb8", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}
f085bf07-6865-4d74-be32-ecc3422267bd	payments	da813a90-6678-41b5-ba6f-0c44059028ad	INSERT	{"id": "da813a90-6678-41b5-ba6f-0c44059028ad", "amount": 149000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "9257dcad-0488-420e-a6eb-be52650d2702", "created_at": "2026-08-10T06:44:10.391398+00:00", "updated_at": "2026-08-10T06:44:10.391398+00:00", "refunded_at": null, "checkout_url": null, "provider_ref": null, "refund_error": null, "response_code": null, "payment_method": "PAYPAL", "transaction_id": null, "idempotency_key": "payment-f928b367-b647-4259-b63a-19aaee8c807b", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}	1210	2026-08-10 06:44:10.391398+00	\N
de2b0af4-45e3-4f66-8a55-c1e14a6e8f96	bookings	2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7	UPDATE	{"id": "2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7", "status": "CONFIRMED", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:36:40.928178+00:00", "expires_at": "2026-08-10T06:41:41.105929+00:00", "updated_at": "2026-08-10T06:37:09.001952+00:00", "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "ticket_code": null, "total_price": 90000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 90000.00, "discount_amount": 0.00, "idempotency_key": "booking-b2469d28-f2d3-4edf-9f53-d5d848da5bb8", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1202	2026-08-10 06:37:09.001952+00	{"id": "2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7", "status": "PENDING", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:36:40.928178+00:00", "expires_at": "2026-08-10T06:41:41.105929+00:00", "updated_at": "2026-08-10T06:36:40.928178+00:00", "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "ticket_code": null, "total_price": 90000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 90000.00, "discount_amount": 0.00, "idempotency_key": "booking-b2469d28-f2d3-4edf-9f53-d5d848da5bb8", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}
93755f19-6914-4e5a-a99b-7650ddcad3ec	payments	714ec43c-14d2-4ff2-b138-ad80b163c92f	UPDATE	{"id": "714ec43c-14d2-4ff2-b138-ad80b163c92f", "amount": 90000.00, "status": "SUCCESS", "paid_at": "2026-08-10T06:37:10.827648+00:00", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7", "created_at": "2026-08-10T06:36:43.330425+00:00", "updated_at": "2026-08-10T06:37:09.001952+00:00", "refunded_at": null, "checkout_url": "https://www.sandbox.paypal.com/checkoutnow?token=2VS37002Y1970705T", "provider_ref": "2VS37002Y1970705T", "refund_error": null, "response_code": "COMPLETED", "payment_method": "PAYPAL", "transaction_id": "1CX51277C0098293D", "idempotency_key": "payment-b2469d28-f2d3-4edf-9f53-d5d848da5bb8", "provider_status": "COMPLETED", "refund_attempts": 0, "signature_valid": true, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": "1CX51277C0098293D"}	1202	2026-08-10 06:37:09.001952+00	{"id": "714ec43c-14d2-4ff2-b138-ad80b163c92f", "amount": 90000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7", "created_at": "2026-08-10T06:36:43.330425+00:00", "updated_at": "2026-08-10T06:36:43.330425+00:00", "refunded_at": null, "checkout_url": "https://www.sandbox.paypal.com/checkoutnow?token=2VS37002Y1970705T", "provider_ref": "2VS37002Y1970705T", "refund_error": null, "response_code": null, "payment_method": "PAYPAL", "transaction_id": null, "idempotency_key": "payment-b2469d28-f2d3-4edf-9f53-d5d848da5bb8", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}
0853f6c3-8087-4732-9d50-0b561b819a26	bookings	2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7	UPDATE	{"id": "2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7", "status": "CONFIRMED", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:36:40.928178+00:00", "expires_at": "2026-08-10T06:41:41.105929+00:00", "updated_at": "2026-08-10T06:37:09.001952+00:00", "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "ticket_code": "C8260810001", "total_price": 90000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 90000.00, "discount_amount": 0.00, "idempotency_key": "booking-b2469d28-f2d3-4edf-9f53-d5d848da5bb8", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1202	2026-08-10 06:37:09.001952+00	{"id": "2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7", "status": "CONFIRMED", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:36:40.928178+00:00", "expires_at": "2026-08-10T06:41:41.105929+00:00", "updated_at": "2026-08-10T06:37:09.001952+00:00", "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "ticket_code": null, "total_price": 90000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 90000.00, "discount_amount": 0.00, "idempotency_key": "booking-b2469d28-f2d3-4edf-9f53-d5d848da5bb8", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}
14fc622c-e6d2-451c-a2c5-1ebac71ae8cb	tickets	c054c36b-2504-4dae-a52b-87f85c82e81a	INSERT	{"id": "c054c36b-2504-4dae-a52b-87f85c82e81a", "status": "ISSUED", "seat_id": "d9cc21ac-906f-467c-8b48-d1cc107c03d6", "qr_nonce": "f22a7f747e35cc61636900a6a70e4f75", "seat_row": "A", "issued_at": "2026-08-10T06:37:09.001952+00:00", "scan_code": "QZN5NXDMFA6M", "booking_id": "2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7", "unit_price": 90000.00, "seat_number": 12, "ticket_code": "C8260810001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "fea69643-4b6a-4ea1-be4e-6b380ba56845", "pricing_details": {"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1202	2026-08-10 06:37:09.001952+00	\N
df0d315e-3395-44dd-9f9d-cee418e60e1a	bookings	9257dcad-0488-420e-a6eb-be52650d2702	INSERT	{"id": "9257dcad-0488-420e-a6eb-be52650d2702", "status": "PENDING", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:44:09.836032+00:00", "expires_at": "2026-08-10T06:49:10.102872+00:00", "updated_at": "2026-08-10T06:44:09.836032+00:00", "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "ticket_code": null, "total_price": 149000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 149000.00, "discount_amount": 0.00, "idempotency_key": "booking-f928b367-b647-4259-b63a-19aaee8c807b", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1209	2026-08-10 06:44:09.836032+00	\N
fe070968-6ea3-471d-8a78-412b356c840e	booking_combos	2882c03f-fa14-4ee0-8754-88a66517b163	INSERT	{"id": "2882c03f-fa14-4ee0-8754-88a66517b163", "combo_id": "9b2db4b2-323b-4b56-9890-661b096fc619", "quantity": 1, "booking_id": "9257dcad-0488-420e-a6eb-be52650d2702", "combo_name": "Combo Kids", "line_total": 59000.00, "unit_price": 59000.00, "inventory_status": "RESERVED"}	1209	2026-08-10 06:44:09.836032+00	\N
7d4bc3e2-ee72-4beb-a0d1-3b4ed9513421	payments	da813a90-6678-41b5-ba6f-0c44059028ad	UPDATE	{"id": "da813a90-6678-41b5-ba6f-0c44059028ad", "amount": 149000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "9257dcad-0488-420e-a6eb-be52650d2702", "created_at": "2026-08-10T06:44:10.391398+00:00", "updated_at": "2026-08-10T06:44:10.391398+00:00", "refunded_at": null, "checkout_url": "https://www.sandbox.paypal.com/checkoutnow?token=7Y595838H1888335F", "provider_ref": "7Y595838H1888335F", "refund_error": null, "response_code": null, "payment_method": "PAYPAL", "transaction_id": null, "idempotency_key": "payment-f928b367-b647-4259-b63a-19aaee8c807b", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}	1210	2026-08-10 06:44:10.391398+00	{"id": "da813a90-6678-41b5-ba6f-0c44059028ad", "amount": 149000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "9257dcad-0488-420e-a6eb-be52650d2702", "created_at": "2026-08-10T06:44:10.391398+00:00", "updated_at": "2026-08-10T06:44:10.391398+00:00", "refunded_at": null, "checkout_url": null, "provider_ref": null, "refund_error": null, "response_code": null, "payment_method": "PAYPAL", "transaction_id": null, "idempotency_key": "payment-f928b367-b647-4259-b63a-19aaee8c807b", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}
307a92ec-2c2b-4b8a-b7fc-ca705f435f0e	bookings	9257dcad-0488-420e-a6eb-be52650d2702	UPDATE	{"id": "9257dcad-0488-420e-a6eb-be52650d2702", "status": "CONFIRMED", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:44:09.836032+00:00", "expires_at": "2026-08-10T06:49:10.102872+00:00", "updated_at": "2026-08-10T06:44:28.853279+00:00", "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "ticket_code": null, "total_price": 149000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 149000.00, "discount_amount": 0.00, "idempotency_key": "booking-f928b367-b647-4259-b63a-19aaee8c807b", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1211	2026-08-10 06:44:28.853279+00	{"id": "9257dcad-0488-420e-a6eb-be52650d2702", "status": "PENDING", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:44:09.836032+00:00", "expires_at": "2026-08-10T06:49:10.102872+00:00", "updated_at": "2026-08-10T06:44:09.836032+00:00", "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "ticket_code": null, "total_price": 149000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 149000.00, "discount_amount": 0.00, "idempotency_key": "booking-f928b367-b647-4259-b63a-19aaee8c807b", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}
067e7d07-661b-4176-ae00-d7a520db8734	payments	da813a90-6678-41b5-ba6f-0c44059028ad	UPDATE	{"id": "da813a90-6678-41b5-ba6f-0c44059028ad", "amount": 149000.00, "status": "SUCCESS", "paid_at": "2026-08-10T06:44:31.043389+00:00", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "9257dcad-0488-420e-a6eb-be52650d2702", "created_at": "2026-08-10T06:44:10.391398+00:00", "updated_at": "2026-08-10T06:44:28.853279+00:00", "refunded_at": null, "checkout_url": "https://www.sandbox.paypal.com/checkoutnow?token=7Y595838H1888335F", "provider_ref": "7Y595838H1888335F", "refund_error": null, "response_code": "COMPLETED", "payment_method": "PAYPAL", "transaction_id": "3K613791WD3687918", "idempotency_key": "payment-f928b367-b647-4259-b63a-19aaee8c807b", "provider_status": "COMPLETED", "refund_attempts": 0, "signature_valid": true, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": "3K613791WD3687918"}	1211	2026-08-10 06:44:28.853279+00	{"id": "da813a90-6678-41b5-ba6f-0c44059028ad", "amount": 149000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "9257dcad-0488-420e-a6eb-be52650d2702", "created_at": "2026-08-10T06:44:10.391398+00:00", "updated_at": "2026-08-10T06:44:10.391398+00:00", "refunded_at": null, "checkout_url": "https://www.sandbox.paypal.com/checkoutnow?token=7Y595838H1888335F", "provider_ref": "7Y595838H1888335F", "refund_error": null, "response_code": null, "payment_method": "PAYPAL", "transaction_id": null, "idempotency_key": "payment-f928b367-b647-4259-b63a-19aaee8c807b", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}
55c8d681-7532-4d27-a9b9-9dcfbfca5472	booking_combos	2882c03f-fa14-4ee0-8754-88a66517b163	UPDATE	{"id": "2882c03f-fa14-4ee0-8754-88a66517b163", "combo_id": "9b2db4b2-323b-4b56-9890-661b096fc619", "quantity": 1, "booking_id": "9257dcad-0488-420e-a6eb-be52650d2702", "combo_name": "Combo Kids", "line_total": 59000.00, "unit_price": 59000.00, "inventory_status": "SOLD"}	1211	2026-08-10 06:44:28.853279+00	{"id": "2882c03f-fa14-4ee0-8754-88a66517b163", "combo_id": "9b2db4b2-323b-4b56-9890-661b096fc619", "quantity": 1, "booking_id": "9257dcad-0488-420e-a6eb-be52650d2702", "combo_name": "Combo Kids", "line_total": 59000.00, "unit_price": 59000.00, "inventory_status": "RESERVED"}
ed4d1314-b811-4440-a3db-3307628ca637	payments	99dcdbe1-a87c-4f2c-8c32-7a4840440175	INSERT	{"id": "99dcdbe1-a87c-4f2c-8c32-7a4840440175", "amount": 270000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "created_at": "2026-08-10T06:45:32.004295+00:00", "updated_at": "2026-08-10T06:45:32.004295+00:00", "refunded_at": null, "checkout_url": null, "provider_ref": "99dcdbe1a87c4f2c8c327a4840440175", "refund_error": null, "response_code": null, "payment_method": "VNPAY", "transaction_id": null, "idempotency_key": "payment-b1652b29-bd04-4244-9d4a-7f7fae563227", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}	1217	2026-08-10 06:45:32.004295+00	\N
dfc0676a-383e-4434-a2dd-235e4b51ce28	bookings	9257dcad-0488-420e-a6eb-be52650d2702	UPDATE	{"id": "9257dcad-0488-420e-a6eb-be52650d2702", "status": "CONFIRMED", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:44:09.836032+00:00", "expires_at": "2026-08-10T06:49:10.102872+00:00", "updated_at": "2026-08-10T06:44:28.853279+00:00", "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "ticket_code": "C8260810002", "total_price": 149000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 149000.00, "discount_amount": 0.00, "idempotency_key": "booking-f928b367-b647-4259-b63a-19aaee8c807b", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1211	2026-08-10 06:44:28.853279+00	{"id": "9257dcad-0488-420e-a6eb-be52650d2702", "status": "CONFIRMED", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:44:09.836032+00:00", "expires_at": "2026-08-10T06:49:10.102872+00:00", "updated_at": "2026-08-10T06:44:28.853279+00:00", "showtime_id": "0aa29023-0b8d-4bdd-8b0f-ec030ec72823", "ticket_code": null, "total_price": 149000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 149000.00, "discount_amount": 0.00, "idempotency_key": "booking-f928b367-b647-4259-b63a-19aaee8c807b", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}
5184bd7f-17fa-4408-840e-77584827f77e	tickets	9cefc1a9-3836-4251-a0b8-aeecea36b495	INSERT	{"id": "9cefc1a9-3836-4251-a0b8-aeecea36b495", "status": "ISSUED", "seat_id": "5042eca3-dfaa-4f3c-a99b-390eb2bd346f", "qr_nonce": "9bd679fedd41268b5ceb9bae5ad53b9e", "seat_row": "A", "issued_at": "2026-08-10T06:44:28.853279+00:00", "scan_code": "Q9IZJSRT9P4C", "booking_id": "9257dcad-0488-420e-a6eb-be52650d2702", "unit_price": 90000.00, "seat_number": 11, "ticket_code": "C8260810002-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "7790d26b-abb7-4eb4-8d7b-654ee850e193", "pricing_details": {"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1211	2026-08-10 06:44:28.853279+00	\N
7466761c-7206-45dc-876e-69b8c5de7d9b	bookings	dfae2120-2fcd-4778-8f30-76b37f599e56	INSERT	{"id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "status": "PENDING", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:45:31.739374+00:00", "expires_at": "2026-08-10T06:50:31.861405+00:00", "updated_at": "2026-08-10T06:45:31.739374+00:00", "showtime_id": "3f7f4214-cd34-4e7f-b8fc-9295532599f6", "ticket_code": null, "total_price": 270000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 270000.00, "discount_amount": 0.00, "idempotency_key": "booking-b1652b29-bd04-4244-9d4a-7f7fae563227", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1216	2026-08-10 06:45:31.739374+00	\N
3ac857ab-41b2-4440-92fd-40599a07785e	booking_seats	c52c8929-a997-4a0c-8071-ca5dd545dad7	INSERT	{"id": "c52c8929-a997-4a0c-8071-ca5dd545dad7", "seat_id": "efc80c2a-90f1-40d3-bda8-4664d2e29853", "booking_id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "unit_price": 90000.00, "showtime_id": "3f7f4214-cd34-4e7f-b8fc-9295532599f6", "pricing_details": {"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1216	2026-08-10 06:45:31.739374+00	\N
445d9c8f-ed9b-49f2-a6cc-ed54b06bc490	booking_seats	29d05e98-841a-4785-b35c-530f88e8d16f	INSERT	{"id": "29d05e98-841a-4785-b35c-530f88e8d16f", "seat_id": "9ba6db82-6e32-4413-8a23-de398df9ffb1", "booking_id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "unit_price": 90000.00, "showtime_id": "3f7f4214-cd34-4e7f-b8fc-9295532599f6", "pricing_details": {"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1216	2026-08-10 06:45:31.739374+00	\N
62d3427c-1a1e-421d-ba55-c131a909a852	booking_seats	0b86af4b-6fbf-41c3-bd0f-8eb8c5561d69	INSERT	{"id": "0b86af4b-6fbf-41c3-bd0f-8eb8c5561d69", "seat_id": "aa2f6757-f430-4564-abf7-5ff595888024", "booking_id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "unit_price": 90000.00, "showtime_id": "3f7f4214-cd34-4e7f-b8fc-9295532599f6", "pricing_details": {"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1216	2026-08-10 06:45:31.739374+00	\N
a5cfc1c1-3492-4cd9-bd16-c5307a0a41d9	bookings	dfae2120-2fcd-4778-8f30-76b37f599e56	UPDATE	{"id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "status": "CONFIRMED", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:45:31.739374+00:00", "expires_at": "2026-08-10T06:50:31.861405+00:00", "updated_at": "2026-08-10T06:46:19.622465+00:00", "showtime_id": "3f7f4214-cd34-4e7f-b8fc-9295532599f6", "ticket_code": null, "total_price": 270000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 270000.00, "discount_amount": 0.00, "idempotency_key": "booking-b1652b29-bd04-4244-9d4a-7f7fae563227", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1218	2026-08-10 06:46:19.622465+00	{"id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "status": "PENDING", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:45:31.739374+00:00", "expires_at": "2026-08-10T06:50:31.861405+00:00", "updated_at": "2026-08-10T06:45:31.739374+00:00", "showtime_id": "3f7f4214-cd34-4e7f-b8fc-9295532599f6", "ticket_code": null, "total_price": 270000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 270000.00, "discount_amount": 0.00, "idempotency_key": "booking-b1652b29-bd04-4244-9d4a-7f7fae563227", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}
d2958851-9e6c-49d1-ba59-3a94f3130ec2	booking_seats	34243790-93e6-40ed-90a8-8f53e9859489	INSERT	{"id": "34243790-93e6-40ed-90a8-8f53e9859489", "seat_id": "dc6f6ebd-0e3f-4a29-aa3b-52f5535b8029", "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "unit_price": 120000.00, "showtime_id": "bc517e46-993b-492e-ad1a-5ae9aecd371e", "pricing_details": {"surcharge": "0", "base_price": "120000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1241	2026-08-10 08:14:49.068627+00	\N
ba0fe6e9-5d28-4524-aeb8-dbb6fa81799c	payments	99dcdbe1-a87c-4f2c-8c32-7a4840440175	UPDATE	{"id": "99dcdbe1-a87c-4f2c-8c32-7a4840440175", "amount": 270000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "created_at": "2026-08-10T06:45:32.004295+00:00", "updated_at": "2026-08-10T06:45:32.004295+00:00", "refunded_at": null, "checkout_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?vnp_Amount=27000000&vnp_Command=pay&vnp_CreateDate=20260810134532&vnp_CurrCode=VND&vnp_ExpireDate=20260810135031&vnp_IpAddr=172.18.0.1&vnp_Locale=vn&vnp_OrderInfo=Thanh+toan+ve+CineAI+dfae2120-2fcd-4778-8f30-76b37f599e56&vnp_OrderType=other&vnp_ReturnUrl=https%3A%2F%2Fexacting-glenda-usurpingly.ngrok-free.dev%2Fcheckout%2Fvnpay-return&vnp_TmnCode=T3X2ZW00&vnp_TxnRef=99dcdbe1a87c4f2c8c327a4840440175&vnp_Version=2.1.0&vnp_SecureHash=f73434ca9e76414c7b740d23e0e17ff86f6169ab58a96d98eae5e31e9a4d7a01550f00226c61ad829fa7208c1723f93a48daf0d7acf71d4f365fa8459db736ef", "provider_ref": "99dcdbe1a87c4f2c8c327a4840440175", "refund_error": null, "response_code": null, "payment_method": "VNPAY", "transaction_id": null, "idempotency_key": "payment-b1652b29-bd04-4244-9d4a-7f7fae563227", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}	1217	2026-08-10 06:45:32.004295+00	{"id": "99dcdbe1-a87c-4f2c-8c32-7a4840440175", "amount": 270000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "created_at": "2026-08-10T06:45:32.004295+00:00", "updated_at": "2026-08-10T06:45:32.004295+00:00", "refunded_at": null, "checkout_url": null, "provider_ref": "99dcdbe1a87c4f2c8c327a4840440175", "refund_error": null, "response_code": null, "payment_method": "VNPAY", "transaction_id": null, "idempotency_key": "payment-b1652b29-bd04-4244-9d4a-7f7fae563227", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}
fa34b54e-325a-4053-8ce0-8bed848a01c7	payments	99dcdbe1-a87c-4f2c-8c32-7a4840440175	UPDATE	{"id": "99dcdbe1-a87c-4f2c-8c32-7a4840440175", "amount": 270000.00, "status": "SUCCESS", "paid_at": "2026-08-10T06:46:19.904261+00:00", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": "NCB", "card_type": "ATM", "booking_id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "created_at": "2026-08-10T06:45:32.004295+00:00", "updated_at": "2026-08-10T06:46:19.622465+00:00", "refunded_at": null, "checkout_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?vnp_Amount=27000000&vnp_Command=pay&vnp_CreateDate=20260810134532&vnp_CurrCode=VND&vnp_ExpireDate=20260810135031&vnp_IpAddr=172.18.0.1&vnp_Locale=vn&vnp_OrderInfo=Thanh+toan+ve+CineAI+dfae2120-2fcd-4778-8f30-76b37f599e56&vnp_OrderType=other&vnp_ReturnUrl=https%3A%2F%2Fexacting-glenda-usurpingly.ngrok-free.dev%2Fcheckout%2Fvnpay-return&vnp_TmnCode=T3X2ZW00&vnp_TxnRef=99dcdbe1a87c4f2c8c327a4840440175&vnp_Version=2.1.0&vnp_SecureHash=f73434ca9e76414c7b740d23e0e17ff86f6169ab58a96d98eae5e31e9a4d7a01550f00226c61ad829fa7208c1723f93a48daf0d7acf71d4f365fa8459db736ef", "provider_ref": "99dcdbe1a87c4f2c8c327a4840440175", "refund_error": null, "response_code": "00", "payment_method": "VNPAY", "transaction_id": "15651608", "idempotency_key": "payment-b1652b29-bd04-4244-9d4a-7f7fae563227", "provider_status": "00", "refund_attempts": 0, "signature_valid": true, "last_verified_at": null, "provider_paid_at": "2026-08-10T06:46:10+00:00", "refund_request_id": null, "bank_transaction_no": "VNP15651608", "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": "15651608"}	1218	2026-08-10 06:46:19.622465+00	{"id": "99dcdbe1-a87c-4f2c-8c32-7a4840440175", "amount": 270000.00, "status": "PENDING", "paid_at": null, "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "bank_code": null, "card_type": null, "booking_id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "created_at": "2026-08-10T06:45:32.004295+00:00", "updated_at": "2026-08-10T06:45:32.004295+00:00", "refunded_at": null, "checkout_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?vnp_Amount=27000000&vnp_Command=pay&vnp_CreateDate=20260810134532&vnp_CurrCode=VND&vnp_ExpireDate=20260810135031&vnp_IpAddr=172.18.0.1&vnp_Locale=vn&vnp_OrderInfo=Thanh+toan+ve+CineAI+dfae2120-2fcd-4778-8f30-76b37f599e56&vnp_OrderType=other&vnp_ReturnUrl=https%3A%2F%2Fexacting-glenda-usurpingly.ngrok-free.dev%2Fcheckout%2Fvnpay-return&vnp_TmnCode=T3X2ZW00&vnp_TxnRef=99dcdbe1a87c4f2c8c327a4840440175&vnp_Version=2.1.0&vnp_SecureHash=f73434ca9e76414c7b740d23e0e17ff86f6169ab58a96d98eae5e31e9a4d7a01550f00226c61ad829fa7208c1723f93a48daf0d7acf71d4f365fa8459db736ef", "provider_ref": "99dcdbe1a87c4f2c8c327a4840440175", "refund_error": null, "response_code": null, "payment_method": "VNPAY", "transaction_id": null, "idempotency_key": "payment-b1652b29-bd04-4244-9d4a-7f7fae563227", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}
714480d4-ea1d-4239-bb0e-cf34a2c6d685	bookings	dfae2120-2fcd-4778-8f30-76b37f599e56	UPDATE	{"id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "status": "CONFIRMED", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:45:31.739374+00:00", "expires_at": "2026-08-10T06:50:31.861405+00:00", "updated_at": "2026-08-10T06:46:19.622465+00:00", "showtime_id": "3f7f4214-cd34-4e7f-b8fc-9295532599f6", "ticket_code": "C7260810002", "total_price": 270000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 270000.00, "discount_amount": 0.00, "idempotency_key": "booking-b1652b29-bd04-4244-9d4a-7f7fae563227", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1218	2026-08-10 06:46:19.622465+00	{"id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "status": "CONFIRMED", "user_id": "5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9", "created_at": "2026-08-10T06:45:31.739374+00:00", "expires_at": "2026-08-10T06:50:31.861405+00:00", "updated_at": "2026-08-10T06:46:19.622465+00:00", "showtime_id": "3f7f4214-cd34-4e7f-b8fc-9295532599f6", "ticket_code": null, "total_price": 270000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 270000.00, "discount_amount": 0.00, "idempotency_key": "booking-b1652b29-bd04-4244-9d4a-7f7fae563227", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}
ac7a936c-aa3a-4d6f-9c36-15641dbf4e9e	tickets	0210a849-5a67-4bf8-84df-83533dddcff7	INSERT	{"id": "0210a849-5a67-4bf8-84df-83533dddcff7", "status": "ISSUED", "seat_id": "aa2f6757-f430-4564-abf7-5ff595888024", "qr_nonce": "28b37e8b2f8d67eeafdc453f6309beeb", "seat_row": "A", "issued_at": "2026-08-10T06:46:19.622465+00:00", "scan_code": "QBMFF0E9RHCK", "booking_id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "unit_price": 90000.00, "seat_number": 9, "ticket_code": "C7260810002-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "0b86af4b-6fbf-41c3-bd0f-8eb8c5561d69", "pricing_details": {"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1218	2026-08-10 06:46:19.622465+00	\N
9ef487c3-0f68-49c5-8f43-7f478d37c719	tickets	e8218081-f95a-46ab-ba50-71afa5e04086	INSERT	{"id": "e8218081-f95a-46ab-ba50-71afa5e04086", "status": "ISSUED", "seat_id": "9ba6db82-6e32-4413-8a23-de398df9ffb1", "qr_nonce": "af49027bff1c19cb4245fbe7abd53e65", "seat_row": "A", "issued_at": "2026-08-10T06:46:19.622465+00:00", "scan_code": "QLZZLERNU9BZ", "booking_id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "unit_price": 90000.00, "seat_number": 8, "ticket_code": "C7260810002-02", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "29d05e98-841a-4785-b35c-530f88e8d16f", "pricing_details": {"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1218	2026-08-10 06:46:19.622465+00	\N
d845427c-264b-4cac-85fd-1b11fd66d267	tickets	bfa45ecd-5bc0-41b6-a435-841eadd174c4	INSERT	{"id": "bfa45ecd-5bc0-41b6-a435-841eadd174c4", "status": "ISSUED", "seat_id": "efc80c2a-90f1-40d3-bda8-4664d2e29853", "qr_nonce": "1ba47f9c388508f30cbedee977928a70", "seat_row": "A", "issued_at": "2026-08-10T06:46:19.622465+00:00", "scan_code": "QK1BDTKO0ES6", "booking_id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "unit_price": 90000.00, "seat_number": 7, "ticket_code": "C7260810002-03", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "c52c8929-a997-4a0c-8071-ca5dd545dad7", "pricing_details": {"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1218	2026-08-10 06:46:19.622465+00	\N
5f52bee5-d133-4fbf-af95-ecc2996628b1	bookings	3c845d97-791d-45d8-9c7e-86213bd6ee02	INSERT	{"id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "status": "PENDING", "user_id": "a91cb727-754e-42ba-a15c-8a1466e8ef0a", "created_at": "2026-08-10T08:14:49.068627+00:00", "expires_at": "2026-08-10T08:19:49.307004+00:00", "updated_at": "2026-08-10T08:14:49.068627+00:00", "showtime_id": "bc517e46-993b-492e-ad1a-5ae9aecd371e", "ticket_code": null, "total_price": 516000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 516000.00, "discount_amount": 0.00, "idempotency_key": "booking-6a84e4fb-dab3-4c1c-b408-bebd0c12bdea", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1241	2026-08-10 08:14:49.068627+00	\N
3e664b8a-d020-49ed-8f85-8315fedb10cd	booking_combos	ac27a289-96c4-4f93-a1a9-53bbab2e0a4e	INSERT	{"id": "ac27a289-96c4-4f93-a1a9-53bbab2e0a4e", "combo_id": "b351e22a-056e-4553-a991-96080254bf49", "quantity": 2, "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "combo_name": "Combo Couple", "line_total": 258000.00, "unit_price": 129000.00, "inventory_status": "RESERVED"}	1241	2026-08-10 08:14:49.068627+00	\N
b4339ad3-b005-42c8-9979-11ae8f67b9c5	booking_combos	1c9f7136-e556-413b-8401-901458845785	INSERT	{"id": "1c9f7136-e556-413b-8401-901458845785", "combo_id": "f4d25681-217e-4e5b-bfe7-95c9dda90e34", "quantity": 2, "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "combo_name": "COMBO BẮP ĐỒNG GIÁ 9.000Đ", "line_total": 18000.00, "unit_price": 9000.00, "inventory_status": "RESERVED"}	1241	2026-08-10 08:14:49.068627+00	\N
f4f59f36-4301-4348-a4ba-a68f285669df	booking_seats	9b5d7da7-334f-4d35-9245-7a996473f7ff	INSERT	{"id": "9b5d7da7-334f-4d35-9245-7a996473f7ff", "seat_id": "c9583494-ebc9-43df-a5ed-fc88cf553f0e", "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "unit_price": 120000.00, "showtime_id": "bc517e46-993b-492e-ad1a-5ae9aecd371e", "pricing_details": {"surcharge": "0", "base_price": "120000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1241	2026-08-10 08:14:49.068627+00	\N
23951a2d-d7d4-474d-903f-9a38559e9329	payments	eed68eff-4761-470d-9008-8c10596e0c77	INSERT	{"id": "eed68eff-4761-470d-9008-8c10596e0c77", "amount": 516000.00, "status": "PENDING", "paid_at": null, "user_id": "a91cb727-754e-42ba-a15c-8a1466e8ef0a", "bank_code": null, "card_type": null, "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "created_at": "2026-08-10T08:14:49.661083+00:00", "updated_at": "2026-08-10T08:14:49.661083+00:00", "refunded_at": null, "checkout_url": null, "provider_ref": null, "refund_error": null, "response_code": null, "payment_method": "PAYPAL", "transaction_id": null, "idempotency_key": "payment-6a84e4fb-dab3-4c1c-b408-bebd0c12bdea", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}	1242	2026-08-10 08:14:49.661083+00	\N
d2b911c7-cab0-45dd-914c-3bf8d70831e8	payments	eed68eff-4761-470d-9008-8c10596e0c77	UPDATE	{"id": "eed68eff-4761-470d-9008-8c10596e0c77", "amount": 516000.00, "status": "PENDING", "paid_at": null, "user_id": "a91cb727-754e-42ba-a15c-8a1466e8ef0a", "bank_code": null, "card_type": null, "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "created_at": "2026-08-10T08:14:49.661083+00:00", "updated_at": "2026-08-10T08:14:49.661083+00:00", "refunded_at": null, "checkout_url": "https://www.sandbox.paypal.com/checkoutnow?token=84Y92654AM489625J", "provider_ref": "84Y92654AM489625J", "refund_error": null, "response_code": null, "payment_method": "PAYPAL", "transaction_id": null, "idempotency_key": "payment-6a84e4fb-dab3-4c1c-b408-bebd0c12bdea", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}	1242	2026-08-10 08:14:49.661083+00	{"id": "eed68eff-4761-470d-9008-8c10596e0c77", "amount": 516000.00, "status": "PENDING", "paid_at": null, "user_id": "a91cb727-754e-42ba-a15c-8a1466e8ef0a", "bank_code": null, "card_type": null, "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "created_at": "2026-08-10T08:14:49.661083+00:00", "updated_at": "2026-08-10T08:14:49.661083+00:00", "refunded_at": null, "checkout_url": null, "provider_ref": null, "refund_error": null, "response_code": null, "payment_method": "PAYPAL", "transaction_id": null, "idempotency_key": "payment-6a84e4fb-dab3-4c1c-b408-bebd0c12bdea", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}
8e7dd3c3-cc33-4456-8a0e-842898383df3	bookings	3c845d97-791d-45d8-9c7e-86213bd6ee02	UPDATE	{"id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "status": "CONFIRMED", "user_id": "a91cb727-754e-42ba-a15c-8a1466e8ef0a", "created_at": "2026-08-10T08:14:49.068627+00:00", "expires_at": "2026-08-10T08:19:49.307004+00:00", "updated_at": "2026-08-10T08:15:28.126576+00:00", "showtime_id": "bc517e46-993b-492e-ad1a-5ae9aecd371e", "ticket_code": null, "total_price": 516000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 516000.00, "discount_amount": 0.00, "idempotency_key": "booking-6a84e4fb-dab3-4c1c-b408-bebd0c12bdea", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1243	2026-08-10 08:15:28.126576+00	{"id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "status": "PENDING", "user_id": "a91cb727-754e-42ba-a15c-8a1466e8ef0a", "created_at": "2026-08-10T08:14:49.068627+00:00", "expires_at": "2026-08-10T08:19:49.307004+00:00", "updated_at": "2026-08-10T08:14:49.068627+00:00", "showtime_id": "bc517e46-993b-492e-ad1a-5ae9aecd371e", "ticket_code": null, "total_price": 516000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 516000.00, "discount_amount": 0.00, "idempotency_key": "booking-6a84e4fb-dab3-4c1c-b408-bebd0c12bdea", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}
8e67a04a-5633-481c-a933-c908a2156e73	payments	eed68eff-4761-470d-9008-8c10596e0c77	UPDATE	{"id": "eed68eff-4761-470d-9008-8c10596e0c77", "amount": 516000.00, "status": "SUCCESS", "paid_at": "2026-08-10T08:15:29.721951+00:00", "user_id": "a91cb727-754e-42ba-a15c-8a1466e8ef0a", "bank_code": null, "card_type": null, "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "created_at": "2026-08-10T08:14:49.661083+00:00", "updated_at": "2026-08-10T08:15:28.126576+00:00", "refunded_at": null, "checkout_url": "https://www.sandbox.paypal.com/checkoutnow?token=84Y92654AM489625J", "provider_ref": "84Y92654AM489625J", "refund_error": null, "response_code": "COMPLETED", "payment_method": "PAYPAL", "transaction_id": "7KJ106380R0551117", "idempotency_key": "payment-6a84e4fb-dab3-4c1c-b408-bebd0c12bdea", "provider_status": "COMPLETED", "refund_attempts": 0, "signature_valid": true, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": "7KJ106380R0551117"}	1243	2026-08-10 08:15:28.126576+00	{"id": "eed68eff-4761-470d-9008-8c10596e0c77", "amount": 516000.00, "status": "PENDING", "paid_at": null, "user_id": "a91cb727-754e-42ba-a15c-8a1466e8ef0a", "bank_code": null, "card_type": null, "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "created_at": "2026-08-10T08:14:49.661083+00:00", "updated_at": "2026-08-10T08:14:49.661083+00:00", "refunded_at": null, "checkout_url": "https://www.sandbox.paypal.com/checkoutnow?token=84Y92654AM489625J", "provider_ref": "84Y92654AM489625J", "refund_error": null, "response_code": null, "payment_method": "PAYPAL", "transaction_id": null, "idempotency_key": "payment-6a84e4fb-dab3-4c1c-b408-bebd0c12bdea", "provider_status": null, "refund_attempts": 0, "signature_valid": null, "last_verified_at": null, "provider_paid_at": null, "refund_request_id": null, "bank_transaction_no": null, "refund_requested_at": null, "refund_response_code": null, "refund_transaction_no": null, "refund_provider_status": null, "provider_transaction_no": null}
5edaae5a-0b98-46c3-9c0b-5b03c8478070	booking_combos	1c9f7136-e556-413b-8401-901458845785	UPDATE	{"id": "1c9f7136-e556-413b-8401-901458845785", "combo_id": "f4d25681-217e-4e5b-bfe7-95c9dda90e34", "quantity": 2, "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "combo_name": "COMBO BẮP ĐỒNG GIÁ 9.000Đ", "line_total": 18000.00, "unit_price": 9000.00, "inventory_status": "SOLD"}	1243	2026-08-10 08:15:28.126576+00	{"id": "1c9f7136-e556-413b-8401-901458845785", "combo_id": "f4d25681-217e-4e5b-bfe7-95c9dda90e34", "quantity": 2, "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "combo_name": "COMBO BẮP ĐỒNG GIÁ 9.000Đ", "line_total": 18000.00, "unit_price": 9000.00, "inventory_status": "RESERVED"}
b4d903cb-9fdb-4151-b82e-210cd84a5e3e	booking_combos	ac27a289-96c4-4f93-a1a9-53bbab2e0a4e	UPDATE	{"id": "ac27a289-96c4-4f93-a1a9-53bbab2e0a4e", "combo_id": "b351e22a-056e-4553-a991-96080254bf49", "quantity": 2, "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "combo_name": "Combo Couple", "line_total": 258000.00, "unit_price": 129000.00, "inventory_status": "SOLD"}	1243	2026-08-10 08:15:28.126576+00	{"id": "ac27a289-96c4-4f93-a1a9-53bbab2e0a4e", "combo_id": "b351e22a-056e-4553-a991-96080254bf49", "quantity": 2, "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "combo_name": "Combo Couple", "line_total": 258000.00, "unit_price": 129000.00, "inventory_status": "RESERVED"}
34868e42-222e-4457-a9cc-c4f6f3e6d819	bookings	3c845d97-791d-45d8-9c7e-86213bd6ee02	UPDATE	{"id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "status": "CONFIRMED", "user_id": "a91cb727-754e-42ba-a15c-8a1466e8ef0a", "created_at": "2026-08-10T08:14:49.068627+00:00", "expires_at": "2026-08-10T08:19:49.307004+00:00", "updated_at": "2026-08-10T08:15:28.126576+00:00", "showtime_id": "bc517e46-993b-492e-ad1a-5ae9aecd371e", "ticket_code": "C7260811001", "total_price": 516000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 516000.00, "discount_amount": 0.00, "idempotency_key": "booking-6a84e4fb-dab3-4c1c-b408-bebd0c12bdea", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}	1243	2026-08-10 08:15:28.126576+00	{"id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "status": "CONFIRMED", "user_id": "a91cb727-754e-42ba-a15c-8a1466e8ef0a", "created_at": "2026-08-10T08:14:49.068627+00:00", "expires_at": "2026-08-10T08:19:49.307004+00:00", "updated_at": "2026-08-10T08:15:28.126576+00:00", "showtime_id": "bc517e46-993b-492e-ad1a-5ae9aecd371e", "ticket_code": null, "total_price": 516000.00, "cancelled_at": null, "cancelled_by": null, "promotion_id": null, "checked_in_at": null, "checked_in_by": null, "customer_name": null, "sales_channel": "ONLINE", "seat_snapshot": [], "customer_email": null, "customer_phone": null, "subtotal_price": 516000.00, "discount_amount": 0.00, "idempotency_key": "booking-6a84e4fb-dab3-4c1c-b408-bebd0c12bdea", "cancellation_reason": null, "cancellation_review_note": null, "cancellation_reviewed_at": null, "cancellation_reviewed_by": null, "cancellation_requested_at": null}
9d8f5f2b-2292-4745-bba9-1b645ed3eede	tickets	0e408774-95b4-468a-b438-1fecf2ec59ab	INSERT	{"id": "0e408774-95b4-468a-b438-1fecf2ec59ab", "status": "ISSUED", "seat_id": "dc6f6ebd-0e3f-4a29-aa3b-52f5535b8029", "qr_nonce": "8ef1f53aea9686dd201852c2a4fe1ff7", "seat_row": "C", "issued_at": "2026-08-10T08:15:28.126576+00:00", "scan_code": "QNV3STQWH58H", "booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "unit_price": 120000.00, "seat_number": 7, "ticket_code": "C7260811001-01", "checked_in_at": null, "checked_in_by": null, "booking_seat_id": "34243790-93e6-40ed-90a8-8f53e9859489", "pricing_details": {"surcharge": "0", "base_price": "120000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}}	1243	2026-08-10 08:15:28.126576+00	\N
\.


--
-- Data for Name: auditoriums; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.auditoriums (id, branch_id, code, name, total_seats, screen_type, is_active) FROM stdin;
7daf46fc-c530-4e57-bba8-d786f1c6a2e4	5bb13b55-959e-43ef-9b92-2c8c814424c0	C1	C-1	96	IMAX	t
715df074-412b-441b-b93e-0dfa4f6ee8f9	5becdddd-50e0-47f9-a2b2-2cf297371f5f	C8-1	P-1	96	IMAX	t
69fcd15b-77e6-4ba9-a65a-e5e12019eba0	5becdddd-50e0-47f9-a2b2-2cf297371f5f	C8-2	P-2	77	2D	t
\.


--
-- Data for Name: booking_combos; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.booking_combos (id, booking_id, combo_id, combo_name, unit_price, quantity, line_total, inventory_status) FROM stdin;
dddbbc87-3895-48de-b6cb-4303996b0e9a	533600da-cf60-4155-b812-c255add2ef45	f4d25681-217e-4e5b-bfe7-95c9dda90e34	COMBO BẮP ĐỒNG GIÁ 9.000Đ	9000.00	1	9000.00	SOLD
c0c5e448-0b54-41f4-b510-d476f8eacf7b	b23ea768-02e2-4241-90a7-fcc4c22d1dd2	f4d25681-217e-4e5b-bfe7-95c9dda90e34	COMBO BẮP ĐỒNG GIÁ 9.000Đ	9000.00	1	9000.00	SOLD
d7f7c56b-8ffd-4c98-a873-79509fac8c0b	a72593a3-4040-4aa9-a352-3f050a6faf31	b351e22a-056e-4553-a991-96080254bf49	Combo Couple	129000.00	1	129000.00	SOLD
782f4d3b-676e-44c6-977b-c190b89649b6	96505b30-69ca-4904-ad53-348258129a4d	9b2db4b2-323b-4b56-9890-661b096fc619	Combo Kids	59000.00	1	59000.00	RELEASED
2882c03f-fa14-4ee0-8754-88a66517b163	9257dcad-0488-420e-a6eb-be52650d2702	9b2db4b2-323b-4b56-9890-661b096fc619	Combo Kids	59000.00	1	59000.00	SOLD
1c9f7136-e556-413b-8401-901458845785	3c845d97-791d-45d8-9c7e-86213bd6ee02	f4d25681-217e-4e5b-bfe7-95c9dda90e34	COMBO BẮP ĐỒNG GIÁ 9.000Đ	9000.00	2	18000.00	SOLD
ac27a289-96c4-4f93-a1a9-53bbab2e0a4e	3c845d97-791d-45d8-9c7e-86213bd6ee02	b351e22a-056e-4553-a991-96080254bf49	Combo Couple	129000.00	2	258000.00	SOLD
\.


--
-- Data for Name: booking_seats; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.booking_seats (id, booking_id, showtime_id, seat_id, unit_price, pricing_details) FROM stdin;
fc09d9aa-d0b2-44d5-8115-82e83ffcffb2	0c6f3ae9-dfaa-4713-91e9-6715e8f3b78d	4fb38083-0ca0-4c3c-8467-71f1bbc6947a	bb7adacc-7a56-450d-8421-ac0d76c60a86	0.00	{}
d2a29c4f-18e1-4880-a101-2c1a57760d38	1860f4e8-918e-4597-a86d-2577be728613	4fb38083-0ca0-4c3c-8467-71f1bbc6947a	32ca5abb-3280-46e7-b5c1-053f8169675f	0.00	{}
5273ef67-f2b6-4047-9890-b5fb2b534d34	ff8333f4-1be5-4a74-9b3d-e3ee400772d9	4fb38083-0ca0-4c3c-8467-71f1bbc6947a	078e8247-f639-442f-9ed8-c10452b93473	0.00	{}
d876cb60-941e-4880-9af5-c19d7591769f	ff8333f4-1be5-4a74-9b3d-e3ee400772d9	4fb38083-0ca0-4c3c-8467-71f1bbc6947a	5de88e3a-c599-4d7d-b4fb-35c594942a43	0.00	{}
beb2aeff-1947-4af5-b46c-b63400619f95	751d1181-addc-4100-a0d6-da785f9468b4	4fb38083-0ca0-4c3c-8467-71f1bbc6947a	03efca4b-c0a2-45b8-8212-fbc109c90f90	0.00	{}
1ef23726-31b3-49f7-8828-6b173ca3dff9	4b3483f4-1f1a-454c-9871-63b55cdf0c73	4fb38083-0ca0-4c3c-8467-71f1bbc6947a	25eae2e2-84b0-4afc-b3c9-63c500ea3879	0.00	{}
678d012f-0373-496c-a1fb-09070dae79ff	3e42ae6b-29d8-45ea-b80c-e7b5ddf1053d	4fb38083-0ca0-4c3c-8467-71f1bbc6947a	9ba6db82-6e32-4413-8a23-de398df9ffb1	0.00	{}
fd7bf76e-ad46-402e-8fd0-da8475677937	2a99efd7-7196-4f63-ac4b-f3670caed351	5a71fd06-07be-422a-abac-a322a0b15106	68768715-f9e6-4f9c-a7c0-efbc83edfc75	0.00	{}
c95d3b27-18d3-4277-85af-412b96b2bd34	9c735dd5-26fc-4ca8-979c-5c529a8681b6	2a20eed4-aa19-43a5-9fca-ffddfa6b4102	f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a	0.00	{}
01c0531c-9be8-4e75-80f6-1b952a530abf	9c735dd5-26fc-4ca8-979c-5c529a8681b6	2a20eed4-aa19-43a5-9fca-ffddfa6b4102	68768715-f9e6-4f9c-a7c0-efbc83edfc75	0.00	{}
4233c406-1798-4234-90e8-5ba522f72b5d	bcbddc3f-79b6-4d4b-af86-33a1f1e93904	4727c2f9-7862-4655-902a-01cb760aeded	aa2f6757-f430-4564-abf7-5ff595888024	0.00	{}
38b07830-d184-4376-b567-284552f0e615	ffb77e65-d41f-48b7-a23a-fd0221a6c53c	4727c2f9-7862-4655-902a-01cb760aeded	68768715-f9e6-4f9c-a7c0-efbc83edfc75	0.00	{}
35afc7d4-81ed-4e1b-9652-df2e67b53752	fa5e723c-4c12-4fd5-8708-e23052f2cee8	e94eeec0-a6de-4692-9a60-9b28eeab841c	68768715-f9e6-4f9c-a7c0-efbc83edfc75	0.00	{}
c45ad659-7b0d-4f71-8d1e-e374b3ebd603	d210f403-2fdd-4583-8e18-8cb7034c1a7d	4727c2f9-7862-4655-902a-01cb760aeded	1129090f-3c21-49d4-b882-b3c62f54be1a	0.00	{}
8a8620dd-a9f7-4a4b-ad5e-915c57332708	8eb7e27f-5167-4c41-81a0-cde73361f10f	4321b8d3-113a-466c-ac52-c731a2139a88	68768715-f9e6-4f9c-a7c0-efbc83edfc75	0.00	{}
c02b30ad-8dcc-4e14-aaf5-c00124ead6c2	3f3d7716-141f-4302-8093-5a9f1fc46235	5843102d-f54a-48fb-84a3-179b7faee1ff	1129090f-3c21-49d4-b882-b3c62f54be1a	0.00	{}
fd350b19-ce60-4c65-b5db-f3c49a6e63ad	a4349175-2741-4061-be9a-d488c5fd959d	e94eeec0-a6de-4692-9a60-9b28eeab841c	2ed79287-99c4-4923-8aa9-a9e39223ad74	0.00	{}
74b9c13a-17f2-47a7-b40a-69420dadb411	a4349175-2741-4061-be9a-d488c5fd959d	e94eeec0-a6de-4692-9a60-9b28eeab841c	f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a	0.00	{}
85aa6f1c-7f02-48e6-8ee7-13ca0489635c	6bbd507d-85d0-4298-ab5f-73845dc0a90a	4727c2f9-7862-4655-902a-01cb760aeded	f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a	0.00	{}
8533ee26-1b29-497e-84a9-29aa227268d7	1fcbccd3-6e37-46b3-b44d-4d0f5fed1550	4321b8d3-113a-466c-ac52-c731a2139a88	f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a	0.00	{}
38d6ce79-923c-4e86-afdb-d15f0793014b	4ab4de29-b4a0-474b-ac6b-fb4c2ee06d75	2a20eed4-aa19-43a5-9fca-ffddfa6b4102	03efca4b-c0a2-45b8-8212-fbc109c90f90	0.00	{}
c98be923-4081-4696-b4fc-a7e76ff6dc30	85a22a13-c8ac-48f5-b50c-a8b9a22b2f10	5a71fd06-07be-422a-abac-a322a0b15106	e57ad5e9-f5ab-480f-9153-7dfa510e2a70	0.00	{}
b9c64734-2cdf-4f43-981d-9a58c894c219	85a22a13-c8ac-48f5-b50c-a8b9a22b2f10	5a71fd06-07be-422a-abac-a322a0b15106	1129090f-3c21-49d4-b882-b3c62f54be1a	0.00	{}
7a5be13f-e937-493a-b716-fd83929df431	651d5cb6-a9bd-48ad-9404-09ab5e0ee935	4321b8d3-113a-466c-ac52-c731a2139a88	2ed79287-99c4-4923-8aa9-a9e39223ad74	0.00	{}
5a5e5ff1-06f7-4459-ab3d-20a0462b227c	9ce23bfc-f82f-4df3-bcb0-d520925f6c98	a59a1bba-c013-4e24-9ef7-39a445c10708	dc6f6ebd-0e3f-4a29-aa3b-52f5535b8029	0.00	{}
4b91f56f-0e7f-4a46-bc95-2aa778892ad2	9ce23bfc-f82f-4df3-bcb0-d520925f6c98	a59a1bba-c013-4e24-9ef7-39a445c10708	ee3f6974-b9a2-4808-9dd5-7ec4d7cfb5fb	0.00	{}
1c8b9577-f22b-4d90-a97a-8cf00344c542	2a5ef731-b92b-4fec-98e0-7ee13ca2bdf2	5f8777d0-5cfe-444e-bcf8-94c9a51f3858	51fe1dd3-cf0f-4858-9f2b-0b548ce8d52e	0.00	{}
aba62010-f054-48ff-9a93-6aeed2feacbf	2a5ef731-b92b-4fec-98e0-7ee13ca2bdf2	5f8777d0-5cfe-444e-bcf8-94c9a51f3858	32ca5abb-3280-46e7-b5c1-053f8169675f	0.00	{}
55bf09ae-4525-44b1-bf51-cbc90682cd50	533600da-cf60-4155-b812-c255add2ef45	48f5ac3a-a1dd-4807-9224-c6e7a5b11edd	32ca5abb-3280-46e7-b5c1-053f8169675f	0.00	{}
44a2a193-fd2f-4aae-b667-6ab7d964fc42	533600da-cf60-4155-b812-c255add2ef45	48f5ac3a-a1dd-4807-9224-c6e7a5b11edd	77e0c246-d4ce-46f5-bc39-c58fa01b46d3	0.00	{}
1123d3ff-0e13-4d52-bd19-e60313ba5635	b23ea768-02e2-4241-90a7-fcc4c22d1dd2	f71c608f-ee90-4e7b-856f-92719839c612	7191355f-e232-4000-8daa-22c407f8aae5	0.00	{}
f839faf8-79b6-4fa9-a3b4-53d763b8b5bd	a72593a3-4040-4aa9-a352-3f050a6faf31	ab06927c-77e3-4cc7-8108-cb8789e5c5e7	32ca5abb-3280-46e7-b5c1-053f8169675f	150000.00	{"surcharge": "0", "base_price": "120000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.25"}
fea69643-4b6a-4ea1-be4e-6b380ba56845	2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7	0aa29023-0b8d-4bdd-8b0f-ec030ec72823	d9cc21ac-906f-467c-8b48-d1cc107c03d6	90000.00	{"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}
7790d26b-abb7-4eb4-8d7b-654ee850e193	9257dcad-0488-420e-a6eb-be52650d2702	0aa29023-0b8d-4bdd-8b0f-ec030ec72823	5042eca3-dfaa-4f3c-a99b-390eb2bd346f	90000.00	{"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}
c52c8929-a997-4a0c-8071-ca5dd545dad7	dfae2120-2fcd-4778-8f30-76b37f599e56	3f7f4214-cd34-4e7f-b8fc-9295532599f6	efc80c2a-90f1-40d3-bda8-4664d2e29853	90000.00	{"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}
29d05e98-841a-4785-b35c-530f88e8d16f	dfae2120-2fcd-4778-8f30-76b37f599e56	3f7f4214-cd34-4e7f-b8fc-9295532599f6	9ba6db82-6e32-4413-8a23-de398df9ffb1	90000.00	{"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}
0b86af4b-6fbf-41c3-bd0f-8eb8c5561d69	dfae2120-2fcd-4778-8f30-76b37f599e56	3f7f4214-cd34-4e7f-b8fc-9295532599f6	aa2f6757-f430-4564-abf7-5ff595888024	90000.00	{"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}
9b5d7da7-334f-4d35-9245-7a996473f7ff	3c845d97-791d-45d8-9c7e-86213bd6ee02	bc517e46-993b-492e-ad1a-5ae9aecd371e	c9583494-ebc9-43df-a5ed-fc88cf553f0e	120000.00	{"surcharge": "0", "base_price": "120000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}
34243790-93e6-40ed-90a8-8f53e9859489	3c845d97-791d-45d8-9c7e-86213bd6ee02	bc517e46-993b-492e-ad1a-5ae9aecd371e	dc6f6ebd-0e3f-4a29-aa3b-52f5535b8029	120000.00	{"surcharge": "0", "base_price": "120000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}
\.


--
-- Data for Name: bookings; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.bookings (id, user_id, showtime_id, total_price, status, created_at, updated_at, expires_at, subtotal_price, discount_amount, promotion_id, seat_snapshot, cancellation_reason, cancellation_requested_at, cancelled_at, cancelled_by, cancellation_review_note, cancellation_reviewed_at, cancellation_reviewed_by, ticket_code, checked_in_at, checked_in_by, idempotency_key, sales_channel, customer_name, customer_email, customer_phone) FROM stdin;
533600da-cf60-4155-b812-c255add2ef45	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	48f5ac3a-a1dd-4807-9224-c6e7a5b11edd	279000.00	CONFIRMED	2026-08-06 12:12:36.938116+00	2026-08-06 12:13:05.892086+00	2026-08-06 12:17:37.15375+00	279000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260807002	\N	\N	\N	ONLINE	\N	\N	\N
b23ea768-02e2-4241-90a7-fcc4c22d1dd2	6cb9ebe0-9d8a-49c6-bcce-6669fd5ca41b	f71c608f-ee90-4e7b-856f-92719839c612	121500.00	CONFIRMED	2026-08-07 09:02:40.443031+00	2026-08-07 09:07:21.147112+00	2026-08-07 09:07:40.497255+00	121500.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260808001	2026-08-07 09:07:21.172817+00	2810314c-85d7-46e5-8449-e69ec5ad3285	\N	ONLINE	\N	\N	\N
a72593a3-4040-4aa9-a352-3f050a6faf31	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	ab06927c-77e3-4cc7-8108-cb8789e5c5e7	279000.00	CONFIRMED	2026-08-10 06:00:14.761799+00	2026-08-10 06:00:45.727464+00	2026-08-10 06:05:14.826557+00	279000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260810001	\N	\N	booking-b7f215d3-9da6-4cdd-b830-88f2ebd8746a	ONLINE	\N	\N	\N
96505b30-69ca-4904-ad53-348258129a4d	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	0aa29023-0b8d-4bdd-8b0f-ec030ec72823	149000.00	EXPIRED	2026-08-10 06:26:43.302779+00	2026-08-10 06:31:47.505363+00	2026-08-10 06:31:43.471669+00	149000.00	0.00	\N	[{"id": "d6429f22-16aa-431d-bdce-02c74b61037f", "row": "A", "number": 8}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	booking-11825d2f-bc51-4a80-bcdb-9cabd65deaf3	ONLINE	\N	\N	\N
2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	0aa29023-0b8d-4bdd-8b0f-ec030ec72823	90000.00	CONFIRMED	2026-08-10 06:36:40.928178+00	2026-08-10 06:37:09.001952+00	2026-08-10 06:41:41.105929+00	90000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C8260810001	\N	\N	booking-b2469d28-f2d3-4edf-9f53-d5d848da5bb8	ONLINE	\N	\N	\N
9257dcad-0488-420e-a6eb-be52650d2702	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	0aa29023-0b8d-4bdd-8b0f-ec030ec72823	149000.00	CONFIRMED	2026-08-10 06:44:09.836032+00	2026-08-10 06:44:28.853279+00	2026-08-10 06:49:10.102872+00	149000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C8260810002	\N	\N	booking-f928b367-b647-4259-b63a-19aaee8c807b	ONLINE	\N	\N	\N
3c845d97-791d-45d8-9c7e-86213bd6ee02	a91cb727-754e-42ba-a15c-8a1466e8ef0a	bc517e46-993b-492e-ad1a-5ae9aecd371e	516000.00	CONFIRMED	2026-08-10 08:14:49.068627+00	2026-08-10 08:15:28.126576+00	2026-08-10 08:19:49.307004+00	516000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260811001	\N	\N	booking-6a84e4fb-dab3-4c1c-b408-bebd0c12bdea	ONLINE	\N	\N	\N
dfae2120-2fcd-4778-8f30-76b37f599e56	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	3f7f4214-cd34-4e7f-b8fc-9295532599f6	270000.00	CONFIRMED	2026-08-10 06:45:31.739374+00	2026-08-10 06:46:19.622465+00	2026-08-10 06:50:31.861405+00	270000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260810002	\N	\N	booking-b1652b29-bd04-4244-9d4a-7f7fae563227	ONLINE	\N	\N	\N
8e9cd9c8-484d-41e2-9f8f-b7189880442a	774593d4-5da2-440d-8de6-3ea646880bd1	5843102d-f54a-48fb-84a3-179b7faee1ff	76000.00	EXPIRED	2026-07-30 14:58:10.555362+00	2026-07-30 15:03:26.237836+00	2026-07-30 15:03:10.591659+00	76000.00	0.00	\N	[{"id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "row": "A", "number": 12}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
197f15c6-3442-41cf-b4d9-bda942d5ae61	774593d4-5da2-440d-8de6-3ea646880bd1	5843102d-f54a-48fb-84a3-179b7faee1ff	76000.00	EXPIRED	2026-07-30 15:04:25.869177+00	2026-07-30 15:09:38.392143+00	2026-07-30 15:09:25.900843+00	76000.00	0.00	\N	[{"id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "row": "A", "number": 12}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
c9f07c97-59f5-4dbd-8422-496df3f8f589	774593d4-5da2-440d-8de6-3ea646880bd1	5843102d-f54a-48fb-84a3-179b7faee1ff	76000.00	EXPIRED	2026-07-30 15:08:57.744579+00	2026-07-30 15:14:09.005739+00	2026-07-30 15:13:57.783614+00	76000.00	0.00	\N	[{"id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "row": "A", "number": 11}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
73b8eba5-97fd-4d48-a164-863910d1a5be	774593d4-5da2-440d-8de6-3ea646880bd1	4727c2f9-7862-4655-902a-01cb760aeded	240000.00	EXPIRED	2026-07-30 13:47:52.151846+00	2026-07-30 13:52:55.084284+00	2026-07-30 13:52:52.205018+00	240000.00	0.00	\N	[{"id": "dc6f6ebd-0e3f-4a29-aa3b-52f5535b8029", "row": "C", "number": 7}, {"id": "ee3f6974-b9a2-4808-9dd5-7ec4d7cfb5fb", "row": "C", "number": 8}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
3b9c285f-6412-4029-bc43-ae7b5844fcf3	774593d4-5da2-440d-8de6-3ea646880bd1	2a20eed4-aa19-43a5-9fca-ffddfa6b4102	76000.00	EXPIRED	2026-07-30 13:59:10.640259+00	2026-07-30 14:04:11.49818+00	2026-07-30 14:04:10.690906+00	76000.00	0.00	\N	[{"id": "5bf36aae-d37e-4749-8445-5f55d64645fa", "row": "H", "number": 8}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
1efcbfa4-9403-4e1b-9e14-e1db5c77b3be	774593d4-5da2-440d-8de6-3ea646880bd1	5843102d-f54a-48fb-84a3-179b7faee1ff	76000.00	EXPIRED	2026-07-30 14:09:40.310823+00	2026-07-30 14:14:48.569094+00	2026-07-30 14:14:40.348365+00	76000.00	0.00	\N	[{"id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "row": "A", "number": 12}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
56713ef8-1dca-47a4-ae27-bf32844a5374	774593d4-5da2-440d-8de6-3ea646880bd1	5843102d-f54a-48fb-84a3-179b7faee1ff	76000.00	EXPIRED	2026-07-30 14:15:24.802444+00	2026-07-30 14:20:33.731402+00	2026-07-30 14:20:24.844943+00	76000.00	0.00	\N	[{"id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "row": "A", "number": 12}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
accae566-5f10-4fd1-836e-cb32734387b4	774593d4-5da2-440d-8de6-3ea646880bd1	5843102d-f54a-48fb-84a3-179b7faee1ff	76000.00	EXPIRED	2026-07-30 14:30:35.349097+00	2026-07-30 14:35:36.551421+00	2026-07-30 14:35:35.383424+00	76000.00	0.00	\N	[{"id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "row": "A", "number": 12}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
bdb5e799-58f7-4567-bf28-0e90dd0bf150	774593d4-5da2-440d-8de6-3ea646880bd1	5843102d-f54a-48fb-84a3-179b7faee1ff	76000.00	EXPIRED	2026-07-30 14:41:22.782313+00	2026-07-30 14:46:29.430361+00	2026-07-30 14:46:22.836309+00	76000.00	0.00	\N	[{"id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "row": "A", "number": 12}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
2d68fae4-8230-4979-98fb-29e40c7cb51f	774593d4-5da2-440d-8de6-3ea646880bd1	5843102d-f54a-48fb-84a3-179b7faee1ff	76000.00	EXPIRED	2026-07-30 14:44:47.29587+00	2026-07-30 14:49:55.062497+00	2026-07-30 14:49:47.342831+00	76000.00	0.00	\N	[{"id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "row": "A", "number": 11}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
9c67fe1e-28e4-43c0-8c49-995c5c45c01e	774593d4-5da2-440d-8de6-3ea646880bd1	5843102d-f54a-48fb-84a3-179b7faee1ff	76000.00	EXPIRED	2026-07-30 14:47:46.132032+00	2026-07-30 14:52:47.651998+00	2026-07-30 14:52:46.17142+00	76000.00	0.00	\N	[{"id": "2ed79287-99c4-4923-8aa9-a9e39223ad74", "row": "A", "number": 10}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
8a3d4fcd-517f-40cf-8781-792be6b6cd48	774593d4-5da2-440d-8de6-3ea646880bd1	5843102d-f54a-48fb-84a3-179b7faee1ff	76000.00	EXPIRED	2026-07-30 14:49:55.062497+00	2026-07-30 14:55:07.945312+00	2026-07-30 14:54:55.152372+00	76000.00	0.00	\N	[{"id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "row": "A", "number": 12}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
2a99efd7-7196-4f63-ac4b-f3670caed351	774593d4-5da2-440d-8de6-3ea646880bd1	5a71fd06-07be-422a-abac-a322a0b15106	76000.00	CONFIRMED	2026-07-30 15:11:33.114885+00	2026-07-30 15:12:17.182525+00	2026-07-30 15:16:33.155937+00	76000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260801011	\N	\N	\N	ONLINE	\N	\N	\N
9ce23bfc-f82f-4df3-bcb0-d520925f6c98	774593d4-5da2-440d-8de6-3ea646880bd1	a59a1bba-c013-4e24-9ef7-39a445c10708	152000.00	CONFIRMED	2026-08-02 12:20:10.50569+00	2026-08-02 12:21:00.564159+00	2026-08-02 12:25:10.535561+00	152000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260803001	\N	\N	\N	ONLINE	\N	\N	\N
0c6f3ae9-dfaa-4713-91e9-6715e8f3b78d	774593d4-5da2-440d-8de6-3ea646880bd1	4fb38083-0ca0-4c3c-8467-71f1bbc6947a	120000.00	CONFIRMED	2026-07-28 12:03:33.011302+00	2026-07-28 12:03:33.184941+00	2026-07-28 12:13:33.086562+00	120000.00	0.00	\N	[{"id": "bb7adacc-7a56-450d-8421-ac0d76c60a86", "row": "C", "number": 10}]	\N	\N	\N	\N	\N	\N	\N	C7260730001	\N	\N	\N	ONLINE	\N	\N	\N
1860f4e8-918e-4597-a86d-2577be728613	774593d4-5da2-440d-8de6-3ea646880bd1	4fb38083-0ca0-4c3c-8467-71f1bbc6947a	150000.00	CONFIRMED	2026-07-29 06:45:07.339846+00	2026-07-29 06:45:07.45813+00	2026-07-29 06:50:07.379257+00	150000.00	0.00	\N	[{"id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "row": "D", "number": 8}]	\N	\N	\N	\N	\N	\N	\N	C7260730002	\N	\N	\N	ONLINE	\N	\N	\N
ff8333f4-1be5-4a74-9b3d-e3ee400772d9	774593d4-5da2-440d-8de6-3ea646880bd1	4fb38083-0ca0-4c3c-8467-71f1bbc6947a	216000.00	CONFIRMED	2026-07-29 07:21:40.053029+00	2026-07-29 07:21:40.12972+00	2026-07-29 07:26:40.085602+00	240000.00	24000.00	ad9f692e-1a7a-46fd-914b-825582e0f1a0	[{"id": "078e8247-f639-442f-9ed8-c10452b93473", "row": "E", "number": 7}, {"id": "5de88e3a-c599-4d7d-b4fb-35c594942a43", "row": "E", "number": 8}]	\N	\N	\N	\N	\N	\N	\N	C7260730003	\N	\N	\N	ONLINE	\N	\N	\N
751d1181-addc-4100-a0d6-da785f9468b4	774593d4-5da2-440d-8de6-3ea646880bd1	4fb38083-0ca0-4c3c-8467-71f1bbc6947a	120000.00	CONFIRMED	2026-07-29 13:15:19.439433+00	2026-07-29 13:15:19.656453+00	2026-07-29 13:20:19.539337+00	120000.00	0.00	\N	[{"id": "03efca4b-c0a2-45b8-8212-fbc109c90f90", "row": "A", "number": 6}]	\N	\N	\N	\N	\N	\N	\N	C7260730004	\N	\N	\N	ONLINE	\N	\N	\N
4b3483f4-1f1a-454c-9871-63b55cdf0c73	774593d4-5da2-440d-8de6-3ea646880bd1	4fb38083-0ca0-4c3c-8467-71f1bbc6947a	120000.00	CONFIRMED	2026-07-29 13:38:47.445028+00	2026-07-29 13:38:47.693278+00	2026-07-29 13:43:47.577514+00	120000.00	0.00	\N	[{"id": "25eae2e2-84b0-4afc-b3c9-63c500ea3879", "row": "A", "number": 5}]	\N	\N	\N	\N	\N	\N	\N	C7260730005	\N	\N	\N	ONLINE	\N	\N	\N
3e42ae6b-29d8-45ea-b80c-e7b5ddf1053d	774593d4-5da2-440d-8de6-3ea646880bd1	4fb38083-0ca0-4c3c-8467-71f1bbc6947a	120000.00	CONFIRMED	2026-07-29 13:58:50.696343+00	2026-07-29 13:58:50.835336+00	2026-07-29 14:03:50.747036+00	120000.00	0.00	\N	[{"id": "9ba6db82-6e32-4413-8a23-de398df9ffb1", "row": "A", "number": 8}]	\N	\N	\N	\N	\N	\N	\N	C7260730006	\N	\N	\N	ONLINE	\N	\N	\N
d210f403-2fdd-4583-8e18-8cb7034c1a7d	774593d4-5da2-440d-8de6-3ea646880bd1	4727c2f9-7862-4655-902a-01cb760aeded	120000.00	CONFIRMED	2026-07-30 15:49:20.942537+00	2026-07-30 15:49:53.73538+00	2026-07-30 15:54:20.980866+00	120000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260731008	\N	\N	\N	ONLINE	\N	\N	\N
9c735dd5-26fc-4ca8-979c-5c529a8681b6	774593d4-5da2-440d-8de6-3ea646880bd1	2a20eed4-aa19-43a5-9fca-ffddfa6b4102	152000.00	CONFIRMED	2026-07-30 15:16:55.81962+00	2026-07-30 15:17:29.749811+00	2026-07-30 15:21:55.848051+00	152000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260731005	\N	\N	\N	ONLINE	\N	\N	\N
bcbddc3f-79b6-4d4b-af86-33a1f1e93904	774593d4-5da2-440d-8de6-3ea646880bd1	4727c2f9-7862-4655-902a-01cb760aeded	120000.00	CONFIRMED	2026-07-30 15:22:43.78686+00	2026-07-30 15:23:16.006917+00	2026-07-30 15:27:43.819075+00	120000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260731006	\N	\N	\N	ONLINE	\N	\N	\N
ffb77e65-d41f-48b7-a23a-fd0221a6c53c	774593d4-5da2-440d-8de6-3ea646880bd1	4727c2f9-7862-4655-902a-01cb760aeded	120000.00	CONFIRMED	2026-07-30 15:34:25.251012+00	2026-07-30 15:34:58.344587+00	2026-07-30 15:39:25.311944+00	120000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260731007	\N	\N	\N	ONLINE	\N	\N	\N
fa5e723c-4c12-4fd5-8708-e23052f2cee8	774593d4-5da2-440d-8de6-3ea646880bd1	e94eeec0-a6de-4692-9a60-9b28eeab841c	76000.00	CONFIRMED	2026-07-30 15:44:52.380195+00	2026-07-30 15:45:31.549026+00	2026-07-30 15:49:52.422402+00	76000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260802001	\N	\N	\N	ONLINE	\N	\N	\N
8eb7e27f-5167-4c41-81a0-cde73361f10f	774593d4-5da2-440d-8de6-3ea646880bd1	4321b8d3-113a-466c-ac52-c731a2139a88	120000.00	CONFIRMED	2026-07-30 16:14:39.110867+00	2026-07-30 16:15:14.014148+00	2026-07-30 16:19:39.151108+00	120000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260731009	\N	\N	\N	ONLINE	\N	\N	\N
3f3d7716-141f-4302-8093-5a9f1fc46235	774593d4-5da2-440d-8de6-3ea646880bd1	5843102d-f54a-48fb-84a3-179b7faee1ff	76000.00	CONFIRMED	2026-07-30 16:24:54.915754+00	2026-07-30 16:25:32.756774+00	2026-07-30 16:29:54.950114+00	76000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260801012	\N	\N	\N	ONLINE	\N	\N	\N
a4349175-2741-4061-be9a-d488c5fd959d	774593d4-5da2-440d-8de6-3ea646880bd1	e94eeec0-a6de-4692-9a60-9b28eeab841c	152000.00	CONFIRMED	2026-07-30 18:27:32.166246+00	2026-07-30 18:28:07.074219+00	2026-07-30 18:32:32.292198+00	152000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260802002	\N	\N	\N	ONLINE	\N	\N	\N
6bbd507d-85d0-4298-ab5f-73845dc0a90a	774593d4-5da2-440d-8de6-3ea646880bd1	4727c2f9-7862-4655-902a-01cb760aeded	120000.00	CONFIRMED	2026-07-30 18:55:04.577309+00	2026-07-30 18:55:56.340076+00	2026-07-30 19:00:04.661444+00	120000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260731011	\N	\N	\N	ONLINE	\N	\N	\N
1fcbccd3-6e37-46b3-b44d-4d0f5fed1550	774593d4-5da2-440d-8de6-3ea646880bd1	4321b8d3-113a-466c-ac52-c731a2139a88	120000.00	CONFIRMED	2026-07-30 19:05:28.817411+00	2026-07-30 19:06:37.975348+00	2026-07-30 19:10:28.854962+00	120000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260731012	\N	\N	\N	ONLINE	\N	\N	\N
4ab4de29-b4a0-474b-ac6b-fb4c2ee06d75	774593d4-5da2-440d-8de6-3ea646880bd1	2a20eed4-aa19-43a5-9fca-ffddfa6b4102	76000.00	CONFIRMED	2026-07-30 19:15:33.916256+00	2026-07-30 19:16:07.911242+00	2026-07-30 19:20:34.525007+00	76000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260731013	\N	\N	\N	ONLINE	\N	\N	\N
85a22a13-c8ac-48f5-b50c-a8b9a22b2f10	774593d4-5da2-440d-8de6-3ea646880bd1	5a71fd06-07be-422a-abac-a322a0b15106	152000.00	CONFIRMED	2026-07-30 19:39:25.528573+00	2026-07-30 19:40:05.926877+00	2026-07-30 19:44:25.614027+00	152000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260801014	\N	\N	\N	ONLINE	\N	\N	\N
651d5cb6-a9bd-48ad-9404-09ab5e0ee935	774593d4-5da2-440d-8de6-3ea646880bd1	4321b8d3-113a-466c-ac52-c731a2139a88	120000.00	CONFIRMED	2026-07-30 19:42:47.515884+00	2026-07-30 19:44:16.429214+00	2026-07-30 19:47:47.547673+00	120000.00	0.00	\N	[]	\N	\N	\N	\N	\N	\N	\N	C7260731014	\N	\N	\N	ONLINE	\N	\N	\N
2a5ef731-b92b-4fec-98e0-7ee13ca2bdf2	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	5f8777d0-5cfe-444e-bcf8-94c9a51f3858	190000.00	CONFIRMED	2026-08-04 14:53:28.779915+00	2026-08-05 16:26:27.153347+00	2026-08-04 14:58:28.911963+00	190000.00	0.00	\N	[]	âdadsd	\N	\N	\N	ccccccccc	2026-08-05 16:26:27.229181+00	2810314c-85d7-46e5-8449-e69ec5ad3285	C7260807001	2026-08-05 16:12:06.206065+00	2810314c-85d7-46e5-8449-e69ec5ad3285	\N	ONLINE	\N	\N	\N
49b97e83-6d89-4749-aeb8-538a051382c8	774593d4-5da2-440d-8de6-3ea646880bd1	2a20eed4-aa19-43a5-9fca-ffddfa6b4102	152000.00	EXPIRED	2026-07-30 14:51:59.228414+00	2026-07-30 14:57:08.012443+00	2026-07-30 14:56:59.261286+00	152000.00	0.00	\N	[{"id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "row": "A", "number": 11}, {"id": "68768715-f9e6-4f9c-a7c0-efbc83edfc75", "row": "A", "number": 12}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
03e882eb-80ac-43d1-ac0d-3b9961e38314	774593d4-5da2-440d-8de6-3ea646880bd1	2a20eed4-aa19-43a5-9fca-ffddfa6b4102	76000.00	EXPIRED	2026-07-30 14:54:00.700968+00	2026-07-30 14:59:01.590631+00	2026-07-30 14:59:00.733669+00	76000.00	0.00	\N	[{"id": "2ed79287-99c4-4923-8aa9-a9e39223ad74", "row": "A", "number": 10}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
d409ef5b-72fa-44a8-8a0c-ab68b4f5a8a8	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	cc1d0ca9-9e76-4faa-aec4-b4fdb8771cce	190000.00	EXPIRED	2026-08-04 14:48:19.019909+00	2026-08-04 14:53:22.067877+00	2026-08-04 14:53:19.106341+00	190000.00	0.00	\N	[{"id": "51fe1dd3-cf0f-4858-9f2b-0b548ce8d52e", "row": "D", "number": 7}, {"id": "32ca5abb-3280-46e7-b5c1-053f8169675f", "row": "D", "number": 8}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
00a1564d-774a-48a9-b13f-95f3e521c2e6	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	715fbc9c-f587-45d4-994b-7cb599c874ec	190000.00	EXPIRED	2026-08-04 14:48:44.50818+00	2026-08-04 14:53:57.668316+00	2026-08-04 14:53:44.570276+00	190000.00	0.00	\N	[{"id": "7191355f-e232-4000-8daa-22c407f8aae5", "row": "D", "number": 6}, {"id": "51fe1dd3-cf0f-4858-9f2b-0b548ce8d52e", "row": "D", "number": 7}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
149d1808-0fe7-4c52-9947-4af44f8a9fe6	774593d4-5da2-440d-8de6-3ea646880bd1	4321b8d3-113a-466c-ac52-c731a2139a88	240000.00	EXPIRED	2026-07-30 18:43:58.314453+00	2026-07-30 18:49:11.815343+00	2026-07-30 18:48:58.367865+00	240000.00	0.00	\N	[{"id": "aa2f6757-f430-4564-abf7-5ff595888024", "row": "A", "number": 9}, {"id": "e57ad5e9-f5ab-480f-9153-7dfa510e2a70", "row": "B", "number": 10}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
6dafd69b-5b48-449e-8ffd-c998ec018a13	774593d4-5da2-440d-8de6-3ea646880bd1	c811184a-a868-427d-8390-bf09e5e3c639	360000.00	EXPIRED	2026-07-30 18:51:10.615744+00	2026-07-30 18:56:21.692003+00	2026-07-30 18:56:10.651906+00	360000.00	0.00	\N	[{"id": "aa2f6757-f430-4564-abf7-5ff595888024", "row": "A", "number": 9}, {"id": "2ed79287-99c4-4923-8aa9-a9e39223ad74", "row": "A", "number": 10}, {"id": "f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a", "row": "A", "number": 11}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
24e7dd49-6234-45fb-8a5d-2614ae908010	774593d4-5da2-440d-8de6-3ea646880bd1	2a20eed4-aa19-43a5-9fca-ffddfa6b4102	76000.00	EXPIRED	2026-07-30 19:51:40.523928+00	2026-07-30 19:56:49.662583+00	2026-07-30 19:56:40.555983+00	76000.00	0.00	\N	[{"id": "2ed79287-99c4-4923-8aa9-a9e39223ad74", "row": "A", "number": 10}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
ccfd17f4-d618-4606-a5b6-40d0023eb1ff	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	715fbc9c-f587-45d4-994b-7cb599c874ec	152000.00	EXPIRED	2026-08-04 14:48:57.197521+00	2026-08-04 14:53:57.668316+00	2026-08-04 14:53:57.265403+00	152000.00	0.00	\N	[{"id": "25eae2e2-84b0-4afc-b3c9-63c500ea3879", "row": "A", "number": 5}, {"id": "03efca4b-c0a2-45b8-8212-fbc109c90f90", "row": "A", "number": 6}]	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	ONLINE	\N	\N	\N
\.


--
-- Data for Name: branch_staff; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.branch_staff (branch_id, user_id, staff_role, is_active, assigned_at) FROM stdin;
5becdddd-50e0-47f9-a2b2-2cf297371f5f	dac35bb9-78bf-47c6-bda1-6c991585e958	BRANCH_ADMIN	t	2026-07-29 15:58:33.694462+00
4dc66358-7eab-4703-b21b-7ff6b8de4f4b	5e0114d6-2880-46c2-9c7c-b6cbd2a6aea3	BRANCH_ADMIN	t	2026-08-07 07:19:46.165894+00
5bb13b55-959e-43ef-9b92-2c8c814424c0	2810314c-85d7-46e5-8449-e69ec5ad3285	BRANCH_ADMIN	t	2026-07-28 11:29:12.653868+00
\.


--
-- Data for Name: branches; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.branches (id, vendor_id, code, name, address_line, city, district, latitude, longitude, phone, is_active, created_at) FROM stdin;
4dc66358-7eab-4703-b21b-7ff6b8de4f4b	016b902c-c6c2-4a94-ac24-25d06996a375	CINE-6	Cine Quận 6	Võ Văn Kiệt Bình Hưng 73114 Thành phố Hồ Chí Minh	Hồ Chí Minh	Quận 6	\N	\N	0987567981	t	2026-08-07 07:09:04.370449+00
5bb13b55-959e-43ef-9b92-2c8c814424c0	016b902c-c6c2-4a94-ac24-25d06996a375	C7	Cine Quận 7	469 Nguyễn Hữu Thọ Ho Chi Minh City HCMC	Hồ Chí Minh	Quận 7	\N	\N	098765432111111	t	2026-07-28 11:28:17.170651+00
5becdddd-50e0-47f9-a2b2-2cf297371f5f	016b902c-c6c2-4a94-ac24-25d06996a375	C8	Cine Quận 8	547, Đường Tạ Quang Bửu Bình Hưng 73017 Thành phố Hồ Chí Minh	Hồ Chí Minh	Quận 8	\N	\N	0987654447	t	2026-07-29 15:27:28.417165+00
\.


--
-- Data for Name: combos; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.combos (id, branch_id, name, description, price, image_url, stock_quantity, is_active, created_by, created_at, updated_at) FROM stdin;
4778f97e-c571-488e-86ed-df6656441823	5bb13b55-959e-43ef-9b92-2c8c814424c0	Combo Solo	01 bắp rang cỡ vừa + 01 nước ngọt cỡ vừa	79000.00	\N	\N	t	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-05 16:09:08.392196+00	2026-08-05 16:09:08.392196+00
d3d8ee38-fb9e-43cb-a053-979560af3323	5bb13b55-959e-43ef-9b92-2c8c814424c0	Combo Family	02 bắp rang cỡ lớn + 04 nước ngọt cỡ vừa	239000.00	\N	\N	t	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-05 16:09:08.392196+00	2026-08-05 16:09:08.392196+00
c7cdc3a7-9e61-4f1a-b147-d0dab0b5c5ea	5bb13b55-959e-43ef-9b92-2c8c814424c0	Combo Kids	01 bắp rang cỡ nhỏ + 01 nước ngọt cỡ nhỏ	59000.00	\N	\N	t	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-05 16:09:08.392196+00	2026-08-05 16:09:08.392196+00
b351e22a-056e-4553-a991-96080254bf49	5bb13b55-959e-43ef-9b92-2c8c814424c0	Combo Couple	01 bắp rang cỡ lớn + 02 nước ngọt cỡ vừa	129000.00	https://tse1.mm.bing.net/th/id/OIP.0mVLPRikm5YVri2Q9xP6qQHaLH?r=0&rs=1&pid=ImgDetMain&o=7&rm=3	\N	t	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-05 16:09:08.392196+00	2026-08-05 16:09:34.294437+00
f4d25681-217e-4e5b-bfe7-95c9dda90e34	5bb13b55-959e-43ef-9b92-2c8c814424c0	COMBO BẮP ĐỒNG GIÁ 9.000Đ	Giá siêu tiết kiệm: “Thưởng thức bắp rang thơm giòn với giá chỉ 9.000đ – đồng giá cho mọi lựa chọn!”\n\nCombo tiện lợi: “Một combo nhỏ gọn, ngon miệng, đồng giá 9.000đ – vừa xem phim vừa nhâm nhi cực đã.”\n\nƯu đãi hấp dẫn: “Đồng giá 9.000đ cho combo bắp rang – món ăn vặt không thể thiếu khi đi xem phim.”\n\nTrải nghiệm trọn vẹn: “Xem phim thêm trọn vẹn với combo bắp rang đồng giá 9.000đ, giòn tan từng hạt.”	9000.00	https://static.vecteezy.com/system/resources/previews/028/541/542/large_2x/popcorn-stand-cinema-shot-movie-theatre-popcorn-free-photo.jpg	\N	t	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-05 16:26:12.909595+00	2026-08-05 16:26:12.909595+00
92249cf7-fb58-4c91-94b4-854ee0eeeaa4	5becdddd-50e0-47f9-a2b2-2cf297371f5f	Combo Solo	01 bắp rang cỡ vừa + 01 nước ngọt cỡ vừa	79000.00	\N	\N	t	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:35:04.118352+00	2026-08-07 07:35:04.118352+00
d268266b-b3d6-4812-8ad3-b25a51609d2b	5becdddd-50e0-47f9-a2b2-2cf297371f5f	Combo Couple	01 bắp rang cỡ lớn + 02 nước ngọt cỡ vừa	129000.00	\N	\N	t	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:35:04.118352+00	2026-08-07 07:35:04.118352+00
75e83339-cd13-4d69-a15c-037e3eac7a57	5becdddd-50e0-47f9-a2b2-2cf297371f5f	Combo Family	02 bắp rang cỡ lớn + 04 nước ngọt cỡ vừa	239000.00	\N	\N	t	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:35:04.118352+00	2026-08-07 07:35:04.118352+00
9b2db4b2-323b-4b56-9890-661b096fc619	5becdddd-50e0-47f9-a2b2-2cf297371f5f	Combo Kids	01 bắp rang cỡ nhỏ + 01 nước ngọt cỡ nhỏ	59000.00	\N	\N	t	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:35:04.118352+00	2026-08-07 07:35:04.118352+00
\.


--
-- Data for Name: movie_change_requests; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.movie_change_requests (id, requested_by_id, target_movie_id, request_type, status, payload, review_note, reviewed_by_id, reviewed_at, created_at) FROM stdin;
\.


--
-- Data for Name: movie_genre_map; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.movie_genre_map (movie_id, genre_id) FROM stdin;
f0e326de-897c-4ab1-b55e-a7cc52553cc6	1
f0e326de-897c-4ab1-b55e-a7cc52553cc6	2
f0e326de-897c-4ab1-b55e-a7cc52553cc6	3
c4f6fccc-aec1-4512-9bc4-942c2cb576f4	1
c4f6fccc-aec1-4512-9bc4-942c2cb576f4	4
c4f6fccc-aec1-4512-9bc4-942c2cb576f4	5
e82bd69e-79a2-4c79-a020-5eafd337c553	1
e82bd69e-79a2-4c79-a020-5eafd337c553	4
e82bd69e-79a2-4c79-a020-5eafd337c553	6
cb30ba36-d4fa-4e53-8026-8a97a7a7dd77	2
cb30ba36-d4fa-4e53-8026-8a97a7a7dd77	6
eacb15b1-7a8b-406f-9737-74b13099261b	2
eacb15b1-7a8b-406f-9737-74b13099261b	6
\.


--
-- Data for Name: movie_genres; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.movie_genres (id, code, name) FROM stdin;
1	HANH_ONG	Hành động
2	GIAT_GAN	Giật gân
3	TOI_PHAM	Tội phạm
4	KHOA_HOC_VIEN_TUONG	Khoa học viễn tưởng
5	PHIEU_LUU	Phiêu lưu
6	KINH_DI	Kinh dị
\.


--
-- Data for Name: movie_reviews; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.movie_reviews (id, movie_id, user_id, rating, content, is_visible, created_at, updated_at) FROM stdin;
ee817716-5c08-49cc-9ebc-3eae5103ed05	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	6cb9ebe0-9d8a-49c6-bcce-6669fd5ca41b	1	phim ngu	t	2026-08-07 07:41:52.407669+00	2026-08-07 07:41:52.407669+00
ec74ba39-4db0-47dd-a5d3-e1df735922e7	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	5	Phim hay vậy mà nói ngu	t	2026-08-07 07:43:06.943938+00	2026-08-07 07:43:06.943938+00
\.


--
-- Data for Name: movies; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.movies (id, title, original_title, description, duration_min, release_date, age_rating, language, trailer_url, poster_url, status, created_at, updated_at, tmdb_id, director, cast_names) FROM stdin;
f3c19e6d-c4b7-4411-89c4-75331b6c2a43	The Odyssey	The Odyssey	Câu chuyện theo chân Odysseus trong hành trình kéo dài 10 năm trở về nhà sau cuộc chiến thành Troy, nơi ông phải đối mặt với các vị thần, quái vật và vô vàn thử thách, đồng thời nỗ lực đoàn tụ với vợ và giành lại vương quốc của mình.	173	2026-07-15	P	vi-VN	https://www.themoviedb.org/movie/1368337	https://image.tmdb.org/t/p/w500/7876PK6gosE13Uq1B6nRxf7AJLT.jpg	NOW_SHOWING	2026-07-28 11:48:10.634366+00	2026-07-28 11:48:10.634366+00	\N	\N	[]
8a807d6a-5673-46fc-8549-1111263594a7	He-Man và Những Chiến Binh Vũ Trụ	\N	Thương hiệu huyền thoại trở lại màn ảnh rộng. Sau 15 năm thất lạc, Thanh Gươm Quyền Năng đưa Hoàng tử Adam (Nicholas Galitzine) trở về hành tinh Eternia và phát hiện quê hương đã rơi vào sự cai trị tàn bạo của Skeletor (Jared Leto). Để cứu gia đình và thế giới của mình, Adam phải sát cánh cùng những đồng minh thân cận như Teela (Camila Mendes) và Duncan/Man-At-Arms (Idris Elba), đồng thời chấp nhận định mệnh thật sự của mình: trở thành He-Man - người đàn ông mạnh nhất vũ trụ.	141	2026-06-03	\N	\N	https://www.themoviedb.org/movie/454639	https://image.tmdb.org/t/p/w500/3zJKDkvyTz3g6VpCS6RtaufYV0j.jpg	NOW_SHOWING	2026-07-28 12:02:17.739232+00	2026-07-29 06:47:12.836286+00	\N	\N	[]
f0e326de-897c-4ab1-b55e-a7cc52553cc6	คนเดือดทวงแค้น	คนเดือดทวงแค้น	\N	134	2026-07-20	P	vi-VN	\N	https://image.tmdb.org/t/p/w500/2h4ikWt6TddvIAhMdS3WGVXhaRf.jpg	UPCOMING	2026-08-03 07:09:46.844612+00	2026-08-03 07:09:46.844612+00	1630409	สุรพงษ์ เพลินแสง	["ณเดชน์ คูกิมิยะ", "พิทยา แซ่ฉั่ว", "ชัยวัฒน์ ทองแสง", "Nuanprang Treechit", "Jonathan Holman"]
cb30ba36-d4fa-4e53-8026-8a97a7a7dd77	Ám Ảnh	Obsession	Sau khi bẻ gãy "Liễu Ước Nguyện" thần bí để có được người mình thầm yêu, gã si tình rốt cuộc cũng cầu được ước thấy, để rồi kinh hãi nhận ra cái giá tăm tối phía sau lời ước đó.	109	2026-05-13	P	vi-VN	\N	https://image.tmdb.org/t/p/w500/15qLAM3QM8DoPL9Fps4JOTdqWqt.jpg	UPCOMING	2026-08-07 07:04:34.561045+00	2026-08-07 07:04:34.561045+00	1339713	Curry Barker	["Michael Johnston", "Inde Navarrette", "Cooper Tomlinson", "Megan Lawless", "Andy Richter"]
eacb15b1-7a8b-406f-9737-74b13099261b	The Devil's Mouth	The Devil's Mouth	\N	106	2026-07-29	P	vi-VN	\N	https://image.tmdb.org/t/p/w500/lH8k9uCWYn2b2gsYleqYBDPbWa8.jpg	NOW_SHOWING	2026-08-07 07:05:53.071777+00	2026-08-07 07:05:53.071777+00	1481343	Jeff Wadlow	["Kathryn Newton", "Trần Đồng Lan", "Nico Hiraga", "Gavin Casalegno", "Tommi Rose"]
c4f6fccc-aec1-4512-9bc4-942c2cb576f4	Người Nhện: Khởi Đầu Mới	\N	Không còn Tony Stark, MJ hay Ned kề cận, Peter buộc phải đơn thân độc mã đối diện với phe đối đầu bí ẩn. Tuy nhiên, khi áp lực ngày càng gia tăng, nó kích hoạt một sự biến đổi thể chất bất ngờ, đe dọa chính sự tồn tại của anh. Đồng thời, một chuỗi tội phạm bí ẩn mới xuất hiện, kéo theo một trong những mối đe dọa mạnh mẽ nhất mà Spider-Man từng đối mặt.	150	2026-07-29	\N	\N	\N	https://image.tmdb.org/t/p/w500/wqGZVSCUSXE92WH2zyol2REaqT4.jpg	NOW_SHOWING	2026-08-07 07:04:10.471317+00	2026-08-07 07:29:38.465047+00	969681	Destin Daniel Cretton	["Tom Holland", "Sadie Sink", "Tramell Tillman", "Zendaya", "Jon Bernthal"]
e82bd69e-79a2-4c79-a020-5eafd337c553	Bầy Xác Sống	\N	Giáo sư Se Jeong tham dự một hội nghị công nghệ sinh học, nhưng lại chứng kiến ​​nó biến thành thảm họa khi một loại virus đột biến nhanh chóng được giải phóng. Khi dịch bệnh lan rộng và những người nhiễm bệnh bắt đầu biến đổi, chính quyền đã phong tỏa toàn bộ cơ sở.	123	2026-05-21	\N	\N	\N	https://image.tmdb.org/t/p/w500/lzI70txBtLH5kCUixYMJQffKkL9.jpg	NOW_SHOWING	2026-08-07 07:04:22.731688+00	2026-08-07 07:29:48.192064+00	1375646	연상호	["전지현", "구교환", "지창욱", "김신록", "신현빈"]
\.


--
-- Data for Name: notification_outbox; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.notification_outbox (id, user_id, event_type, channel, payload, status, attempts, available_at, sent_at, last_error, created_at) FROM stdin;
673f6dd0-cfb0-41a3-a60e-437408db07c0	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	TICKET_ISSUED	EMAIL	{"booking_id": "a72593a3-4040-4aa9-a352-3f050a6faf31", "ticket_code": "C7260810001"}	SENT	1	2026-08-10 06:00:45.914026+00	2026-08-10 06:00:54.091375+00	\N	2026-08-10 06:00:45.727464+00
164480bc-3ee8-4a64-8434-8fdfbede942a	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	TICKET_ISSUED	EMAIL	{"booking_id": "2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7", "ticket_code": "C8260810001"}	SENT	1	2026-08-10 06:37:10.994817+00	2026-08-10 06:37:17.790592+00	\N	2026-08-10 06:37:09.001952+00
6ce78004-d3d2-474b-9b5f-e59012ed8fda	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	TICKET_ISSUED	EMAIL	{"booking_id": "9257dcad-0488-420e-a6eb-be52650d2702", "ticket_code": "C8260810002"}	SENT	1	2026-08-10 06:44:31.195204+00	2026-08-10 06:44:42.535407+00	\N	2026-08-10 06:44:28.853279+00
6f6c4ff6-34d1-4c0e-9f3e-af2557d13a83	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	TICKET_ISSUED	EMAIL	{"booking_id": "dfae2120-2fcd-4778-8f30-76b37f599e56", "ticket_code": "C7260810002"}	SENT	1	2026-08-10 06:46:20.037949+00	2026-08-10 06:46:31.548091+00	\N	2026-08-10 06:46:19.622465+00
608c4320-496b-4669-a0c5-c6377e746f7b	a91cb727-754e-42ba-a15c-8a1466e8ef0a	TICKET_ISSUED	EMAIL	{"booking_id": "3c845d97-791d-45d8-9c7e-86213bd6ee02", "ticket_code": "C7260811001"}	SENT	1	2026-08-10 08:15:29.9482+00	2026-08-10 08:15:40.687778+00	\N	2026-08-10 08:15:28.126576+00
\.


--
-- Data for Name: payment_status_history; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.payment_status_history (id, payment_id, old_status, new_status, source, response_code, provider_status, signature_valid, note, raw_payload, created_at) FROM stdin;
d2d9a4c1-b8ac-4bc5-890a-d14ae10b51b9	1b01f32e-8c72-4ca6-b432-0e0d0c529c5e	\N	SUCCESS	LEGACY	\N	\N	\N	Migrated from payment data created before VNPAY integration	{}	2026-07-30 10:47:18.750211+00
fde97618-0e3d-465a-bec0-c9757a426e5d	12c524fc-d99f-433c-850e-d0439d6a2858	\N	SUCCESS	LEGACY	\N	\N	\N	Migrated from payment data created before VNPAY integration	{}	2026-07-30 10:47:18.750211+00
9a431e00-61c8-4de0-8900-140f85a4105b	b208401d-ad2c-4225-beef-97b1d9e55d26	\N	SUCCESS	LEGACY	\N	\N	\N	Migrated from payment data created before VNPAY integration	{}	2026-07-30 10:47:18.750211+00
c2d3cfa3-7c33-44ab-966f-0348c0511347	7545c5fe-63db-4ff5-957c-c7f1fb75a0ec	\N	SUCCESS	LEGACY	\N	\N	\N	Migrated from payment data created before VNPAY integration	{}	2026-07-30 10:47:18.750211+00
d9f9182a-639e-4488-a9d9-4b84919ceda4	96b023ab-02f1-449b-a1bb-af6b1d3e8fce	\N	SUCCESS	LEGACY	\N	\N	\N	Migrated from payment data created before VNPAY integration	{}	2026-07-30 10:47:18.750211+00
91e6652f-d376-4d9e-a4c0-267e09ba1e08	5e1ca009-ad53-4105-89b8-86b4f4e385fe	\N	SUCCESS	LEGACY	\N	\N	\N	Migrated from payment data created before VNPAY integration	{}	2026-07-30 10:47:18.750211+00
d64aeb9f-5c48-4b02-8742-74cd31eb46dd	c2299181-dcca-4009-95f7-d7b884e8f0b2	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "240000.00", "method": "VNPAY"}	2026-07-30 13:47:52.284787+00
4ba9268e-b9cf-4424-9b55-cd1c26287604	3b4769c9-4b20-4330-b695-fc60e66ff2ea	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 13:59:10.738511+00
0b1c5465-e8fd-470a-8bb1-8cc23dc4467e	cef71dea-8768-44ee-bb8b-9cbadbd7cbd2	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 14:09:40.410112+00
109dc9e2-7b59-4809-9a60-07ff5d4c3a24	eae490bd-9dcb-4f0d-b6cd-a5598683d386	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 14:15:24.895616+00
e0b914fe-c5a3-4c96-bcc5-1149c6890982	a9995a73-731b-43a5-8cc5-6a394d19733c	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 14:30:35.451296+00
6cf80f55-b8a9-4685-aef3-2de063238cab	5abe8e3e-470b-475e-b124-75b0099f246d	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 14:41:22.961501+00
93ba04f1-8c4a-44ba-9e0b-efd10b7ebb8f	d7603057-3026-4d8f-add7-de9d51026a0b	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 14:44:47.434261+00
ea2a72d1-2edf-4e9d-9a67-cf35650aec36	ce9da916-dd49-42da-8016-61cfad7e89c8	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 14:47:46.239532+00
a1c2d8bb-6108-4570-af0a-23bd59457820	755c3683-6577-4082-a620-852a731266db	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 14:49:55.224806+00
90a5eaaa-f6f0-4009-a17e-3a6932bea497	3413f116-8244-4beb-8fce-88e88456d8cb	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "152000.00", "method": "VNPAY"}	2026-07-30 14:51:59.322013+00
2ac72baa-94e0-49a4-95fa-953a2aaef781	6ebab602-0b2c-433e-b07c-e48a258e589c	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 14:54:00.790224+00
5b1a8bc0-7e1c-4962-9c75-a8571b736195	d3c012b2-c6ea-4a2a-b88d-a528a622bfc9	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 14:58:10.645723+00
92172f7f-22cf-4564-85ff-c6a91c9d236d	549c3381-7b66-42d7-8ae5-1b4e900ce2a4	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 15:04:25.974217+00
aeaf2ea9-3881-4ed3-a831-54d9265b4a99	c2ee005d-f71b-48bd-9199-ef30bc2d65be	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 15:08:57.858254+00
e2b8b696-2a17-489c-a812-af8073a1e259	2626c50e-4260-43f3-9b71-f2e32c3054e4	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 15:11:33.207188+00
e2e7fb04-d8d8-47c3-9c92-c7d249e0e1b2	2626c50e-4260-43f3-9b71-f2e32c3054e4	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "7600000", "vnp_TxnRef": "CINEAI2626c50e426043f39b71f2e32c3054e4", "vnp_PayDate": "20260730221211", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI 2a99efd7-7196-4f63-ac4b-f3670caed351", "vnp_BankTranNo": "VNP15641736", "vnp_SecureHash": "a72179ffc10deec68e9231dbd38180312f82bed9cdcc82b09d991d8b487f9f9917ddc759502cf5bb8d0dcd609e04fc0f5d1b845515f45c382b19addc398ed5e6", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641736", "vnp_TransactionStatus": "00"}	2026-07-30 15:12:17.182525+00
1c489146-6ed3-4266-a366-28a3eda2b1d1	dbf53924-2aa0-484e-bbb1-3b0c73a221da	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "152000.00", "method": "VNPAY"}	2026-07-30 15:16:55.907954+00
79ea26ba-e59f-4e92-8cf9-98b1de1e12e5	dbf53924-2aa0-484e-bbb1-3b0c73a221da	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "15200000", "vnp_TxnRef": "CINEAIdbf539242aa0484ebbb13b0c73a221da", "vnp_PayDate": "20260730221724", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI 9c735dd5-26fc-4ca8-979c-5c529a8681b6", "vnp_BankTranNo": "VNP15641741", "vnp_SecureHash": "4a778e8fb8a734cd2f233db50781cd239c860442b4ec981340382d97f3c9246607af4d87b361e21f14522696bc6dd092f544b76a0d4327d600046ec27e534167", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641741", "vnp_TransactionStatus": "00"}	2026-07-30 15:17:29.749811+00
390c0980-77d6-4277-932b-a709d171fbec	dbf53924-2aa0-484e-bbb1-3b0c73a221da	SUCCESS	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "15200000", "vnp_TxnRef": "CINEAIdbf539242aa0484ebbb13b0c73a221da", "vnp_PayDate": "20260730221724", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI 9c735dd5-26fc-4ca8-979c-5c529a8681b6", "vnp_BankTranNo": "VNP15641741", "vnp_SecureHash": "4a778e8fb8a734cd2f233db50781cd239c860442b4ec981340382d97f3c9246607af4d87b361e21f14522696bc6dd092f544b76a0d4327d600046ec27e534167", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641741", "vnp_TransactionStatus": "00"}	2026-07-30 15:17:56.842975+00
c15fdd79-eec5-4a2d-acae-e4304a0c8e1f	c4a220f9-4dec-4190-85a6-d98089be24b6	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "120000.00", "method": "VNPAY"}	2026-07-30 15:22:43.882156+00
e616753f-bc1b-406d-b5d1-e0eafca207e2	c4a220f9-4dec-4190-85a6-d98089be24b6	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "12000000", "vnp_TxnRef": "CINEAIc4a220f94dec419085a6d98089be24b6", "vnp_PayDate": "20260730222310", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI bcbddc3f-79b6-4d4b-af86-33a1f1e93904", "vnp_BankTranNo": "VNP15641748", "vnp_SecureHash": "9e00774a0f71184411f2ac1cbe64bb59dcbba3bb18cdf3ad5a9585470dd417ea52a687f0feb8a3674fa6cd1f538ba24ca1960098de21562a84e432e35dcd8c51", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641748", "vnp_TransactionStatus": "00"}	2026-07-30 15:23:16.006917+00
e3e4eb39-a66d-4436-9eb7-c2718aab5c0e	93da291b-a389-4469-8e76-25d2a17b14a1	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "120000.00", "method": "VNPAY"}	2026-07-30 15:34:25.430099+00
2deb8f36-b7f7-4c88-b5f5-e0ef760f18e5	93da291b-a389-4469-8e76-25d2a17b14a1	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "12000000", "vnp_TxnRef": "CINEAI93da291ba38944698e7625d2a17b14a1", "vnp_PayDate": "20260730223453", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI ffb77e65-d41f-48b7-a23a-fd0221a6c53c", "vnp_BankTranNo": "VNP15641756", "vnp_SecureHash": "6e3ae6b56c026dcfcffd4a23b5fd5bae6647917aebcc094c545ca2c60bbbd6c4a435bce798e5fd5e342a191b8dab99ec206a5ba6c8818eb79d5b718cd95dcdce", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641756", "vnp_TransactionStatus": "00"}	2026-07-30 15:34:58.344587+00
06997e02-73e4-4e16-aa21-5c6b128451e1	4d4eb4cf-2ccf-4199-8e93-db441da2a02d	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 15:44:52.503513+00
845fb8a8-fd07-43f5-b353-eb3bc169ad17	4d4eb4cf-2ccf-4199-8e93-db441da2a02d	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "7600000", "vnp_TxnRef": "CINEAI4d4eb4cf2ccf41998e93db441da2a02d", "vnp_PayDate": "20260730224525", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI fa5e723c-4c12-4fd5-8708-e23052f2cee8", "vnp_BankTranNo": "VNP15641760", "vnp_SecureHash": "f281f61f724aa2578d6f4cfa2e6c0261f002e4bf57d39d1d2e3c8d508c9c6ca59e0339d89a69f99b8a9abe004b725b562ce3e831f0dd69b8ec3f8b4c816efe2f", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641760", "vnp_TransactionStatus": "00"}	2026-07-30 15:45:31.549026+00
3ee32620-7123-4dbf-b0f4-f22e2f9e3d91	22dfbc5d-12fe-417f-989e-d937358baa36	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "120000.00", "method": "VNPAY"}	2026-07-30 15:49:21.021364+00
19349c91-207a-450d-980c-6e8785b04c0a	22dfbc5d-12fe-417f-989e-d937358baa36	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "12000000", "vnp_TxnRef": "CINEAI22dfbc5d12fe417f989ed937358baa36", "vnp_PayDate": "20260730224946", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI d210f403-2fdd-4583-8e18-8cb7034c1a7d", "vnp_BankTranNo": "VNP15641765", "vnp_SecureHash": "345430963bbcf14c45b9cf4fb5a707681a66ac6a9110359d177679c03a6a5ae330a6cac279d2d52bfeec3b7dd1fce4a1b48888cbf93bdab113f2e53b44a91172", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641765", "vnp_TransactionStatus": "00"}	2026-07-30 15:49:53.73538+00
0a7032c8-f47e-4c7f-8669-2b2bfe5b9e09	76e6bd46-f888-4c0b-a2b1-bd761650d910	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "120000.00", "method": "VNPAY"}	2026-07-30 16:14:39.281537+00
8d5ac90f-1fff-4ffc-9d79-0104002b92af	76e6bd46-f888-4c0b-a2b1-bd761650d910	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "12000000", "vnp_TxnRef": "CINEAI76e6bd46f8884c0ba2b1bd761650d910", "vnp_PayDate": "20260730231506", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI 8eb7e27f-5167-4c41-81a0-cde73361f10f", "vnp_BankTranNo": "VNP15641787", "vnp_SecureHash": "b59a6e1ac216c5ae02aa3cf39e1f036a346d1956f919e5a7529d2883b2f6e49185e8306ce01803a5a26e6d0a5efebcc676a16fe74d8a2a28ac2a369c0197a378", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641787", "vnp_TransactionStatus": "00"}	2026-07-30 16:15:14.014148+00
e4f15ed5-f1a2-4f12-b66d-f33fa672dc70	43d70deb-9de2-46da-87fd-43ecaac8b004	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 16:24:55.042387+00
2b9f7a7c-4108-4e51-b34c-625242faac90	43d70deb-9de2-46da-87fd-43ecaac8b004	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "7600000", "vnp_TxnRef": "CINEAI43d70deb9de246da87fd43ecaac8b004", "vnp_PayDate": "20260730232528", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI 3f3d7716-141f-4302-8093-5a9f1fc46235", "vnp_BankTranNo": "VNP15641799", "vnp_SecureHash": "c558926bdd0cbe85d58b0f112ecd276866f0dc60f39bfc79bc794cc590c6a6dcf956bdcfe57903b8f15d2d9907a69714729cfec505c0ca1731edda0e920cacba", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641799", "vnp_TransactionStatus": "00"}	2026-07-30 16:25:32.756774+00
e643333c-32d3-48fc-a7b9-c8b176be8fa2	43d70deb-9de2-46da-87fd-43ecaac8b004	SUCCESS	SUCCESS	QUERY_DR	00	00	\N	Matched	{"vnp_Amount": "7600000", "vnp_TxnRef": "CINEAI43d70deb9de246da87fd43ecaac8b004", "vnp_Command": "querydr", "vnp_Message": "QueryDR success", "vnp_PayDate": "20260730232528", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_OrderInfo": "Thanh toan ve CineAI 3f3d7716-141f-4302-8093-5a9f1fc46235", "vnp_ResponseId": "9fa0635a2702461985b750e7197fc7e8", "vnp_SecureHash": "c9f3a8eeccdd5cebf06bb591135baf53ba4f0bfc5e26d027774191a5d93d50488a7849d09558f29363769498485be2dbd49cc13b45e766752deab88ab5383136", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641799", "vnp_TransactionType": "01", "vnp_TransactionStatus": "00"}	2026-07-30 16:42:45.600579+00
cca28e17-8df9-4ea3-b749-28ac3fabc3d3	c7d5e319-e1cd-4f54-b2fd-1cc46657ba55	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "152000.00", "method": "VNPAY"}	2026-07-30 18:27:32.449805+00
56644789-24f6-4bef-9238-f70511a46bf3	c7d5e319-e1cd-4f54-b2fd-1cc46657ba55	PENDING	SUCCESS	RETURN	00	00	t	\N	{"vnp_Amount": "15200000", "vnp_TxnRef": "c7d5e319-e1cd-4f54-b2fd-1cc46657ba55", "vnp_PayDate": "20260731012759", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI a4349175-2741-4061-be9a-d488c5fd959d", "vnp_BankTranNo": "VNP15641885", "vnp_SecureHash": "046dcefd377ad3af6e7c5fbeccafc27f3a97ff1d2daba1ead066db5cc9b033141edb790f01ed3cd01f48aadfd4737382493e4da882db2017ec3439d2f721a701", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641885", "vnp_TransactionStatus": "00"}	2026-07-30 18:28:07.074219+00
29b15023-4dc7-44fb-83ee-b41238f328f8	d8a76cc2-c418-49f4-8b73-2be55eec05b9	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "240000.00", "method": "VNPAY"}	2026-07-30 18:43:58.489785+00
d2536ad6-538a-44ab-a378-171a638fe501	5c335df6-ca1c-40d1-86e8-b15a30d87ae6	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "360000.00", "method": "VNPAY"}	2026-07-30 18:51:10.704496+00
40a3bb9b-2d40-403d-ac5a-19f44382505a	3728a5ed-44ba-4080-b3d5-2d507d45a70e	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "120000.00", "method": "VNPAY"}	2026-07-30 18:55:04.743757+00
2e987dac-d4cd-4f3d-909a-18af864d990c	3728a5ed-44ba-4080-b3d5-2d507d45a70e	PENDING	SUCCESS	RETURN	00	00	t	\N	{"vnp_Amount": "12000000", "vnp_TxnRef": "3728a5ed-44ba-4080-b3d5-2d507d45a70e", "vnp_PayDate": "20260731015549", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI 6bbd507d-85d0-4298-ab5f-73845dc0a90a", "vnp_BankTranNo": "VNP15641901", "vnp_SecureHash": "3ba2a1f8cf0d585babaf02a8d0a631aabc232d0ea746c34bb0d910ff73182b2ea73864dbcac37b60c80fed6711acdbcba834f6e1c0f83e408c5e722ecc7ac643", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641901", "vnp_TransactionStatus": "00"}	2026-07-30 18:55:56.340076+00
9934346b-8619-4347-8adc-e9db25168f57	2c39e29c-4b0a-4bdf-ae34-da03a258e5b2	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "120000.00", "method": "VNPAY"}	2026-07-30 19:05:28.932346+00
4674c407-325e-4461-9d25-f61b8ebb4074	2c39e29c-4b0a-4bdf-ae34-da03a258e5b2	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "12000000", "vnp_TxnRef": "2c39e29c-4b0a-4bdf-ae34-da03a258e5b2", "vnp_PayDate": "20260731020554", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI 1fcbccd3-6e37-46b3-b44d-4d0f5fed1550", "vnp_BankTranNo": "VNP15641903", "vnp_SecureHash": "6a7dc3c394e0506eee973a00a5216b6a88c2ec7f15600c39ad90ec83ed33e8c1e0e27c4f01b60f281dd8e71492626b53c13f88d6869682bbb145ba4166757793", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641903", "vnp_TransactionStatus": "00"}	2026-07-30 19:06:37.975348+00
0d923a9a-e1e4-4bec-9401-c582a96729e5	2c39e29c-4b0a-4bdf-ae34-da03a258e5b2	SUCCESS	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "12000000", "vnp_TxnRef": "2c39e29c-4b0a-4bdf-ae34-da03a258e5b2", "vnp_PayDate": "20260731020554", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI 1fcbccd3-6e37-46b3-b44d-4d0f5fed1550", "vnp_BankTranNo": "VNP15641903", "vnp_SecureHash": "6a7dc3c394e0506eee973a00a5216b6a88c2ec7f15600c39ad90ec83ed33e8c1e0e27c4f01b60f281dd8e71492626b53c13f88d6869682bbb145ba4166757793", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641903", "vnp_TransactionStatus": "00"}	2026-07-30 19:07:18.875356+00
767b552c-a80a-4a62-a4aa-7762bc86a9fb	12c50ea6-c2ab-45ed-8a28-c5e69c461771	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 19:15:34.56222+00
0719c2f5-6c50-457e-a822-0e6b4b9eb28c	12c50ea6-c2ab-45ed-8a28-c5e69c461771	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "7600000", "vnp_TxnRef": "12c50ea6-c2ab-45ed-8a28-c5e69c461771", "vnp_PayDate": "20260731021602", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI 4ab4de29-b4a0-474b-ac6b-fb4c2ee06d75", "vnp_BankTranNo": "VNP15641917", "vnp_SecureHash": "c1e097811ed094e3f943e5cd3f459ef3d23d10c9fd075cd470c20672d5802eda5ca44a14a17ab91ffec64a6545ead9515254cf9390deb22ecb123f50b5eefef3", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641917", "vnp_TransactionStatus": "00"}	2026-07-30 19:16:07.911242+00
d66f5d1b-36fa-41de-bb08-213fe71ec282	9e63ae8e-ff7b-48f8-960f-aa056c258949	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "152000.00", "method": "VNPAY"}	2026-07-30 19:39:25.690697+00
b53ffe0b-8269-482b-a6dd-a41d8de12d51	9e63ae8e-ff7b-48f8-960f-aa056c258949	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "15200000", "vnp_TxnRef": "9e63ae8e-ff7b-48f8-960f-aa056c258949", "vnp_PayDate": "20260731023959", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI 85a22a13-c8ac-48f5-b50c-a8b9a22b2f10", "vnp_BankTranNo": "VNP15641919", "vnp_SecureHash": "8ef0896ad7b4f9549bdb0c5ddf319b53b8d53995102e8dda58821e9d8938003ed76e49c9a069530957b2a148370c6d29e7c0e2bb17f0095a9b89398e8c00981c", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641919", "vnp_TransactionStatus": "00"}	2026-07-30 19:40:05.926877+00
6177e57b-a2c7-436d-b0a1-5aff11bd4b0e	9e63ae8e-ff7b-48f8-960f-aa056c258949	SUCCESS	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "15200000", "vnp_TxnRef": "9e63ae8e-ff7b-48f8-960f-aa056c258949", "vnp_PayDate": "20260731023959", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI 85a22a13-c8ac-48f5-b50c-a8b9a22b2f10", "vnp_BankTranNo": "VNP15641919", "vnp_SecureHash": "8ef0896ad7b4f9549bdb0c5ddf319b53b8d53995102e8dda58821e9d8938003ed76e49c9a069530957b2a148370c6d29e7c0e2bb17f0095a9b89398e8c00981c", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641919", "vnp_TransactionStatus": "00"}	2026-07-30 19:40:33.092538+00
e0ae5df6-8d52-4009-af87-b62c5fcb4e76	465ac0fb-c411-4e47-a3b1-db9a2b10e4fd	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "120000.00", "method": "VNPAY"}	2026-07-30 19:42:47.641558+00
648508a0-c88b-4b1b-ab33-2b4c995f30c6	465ac0fb-c411-4e47-a3b1-db9a2b10e4fd	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "12000000", "vnp_TxnRef": "465ac0fb-c411-4e47-a3b1-db9a2b10e4fd", "vnp_PayDate": "20260731024411", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI 651d5cb6-a9bd-48ad-9404-09ab5e0ee935", "vnp_BankTranNo": "VNP15641920", "vnp_SecureHash": "1d38a39e9fb0e1fc93ea321559ec4b48801a6337a98b1147835c9e5eba27be8f7e26c9d1ca94ed18df69d5adaa640c48bb1558d0d375d04835c7d98840ed0328", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15641920", "vnp_TransactionStatus": "00"}	2026-07-30 19:44:16.429214+00
9e275293-8cb6-473a-9e01-fe536a1ca19c	e57a0346-9648-49e8-abe5-0b784ec4eedd	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "76000.00", "method": "VNPAY"}	2026-07-30 19:51:40.597545+00
25afc003-eb48-409c-9dad-9bd32daf3de9	ed64b01a-d284-4973-a3f3-a4f19b3c38d0	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "152000.00", "method": "VNPAY"}	2026-08-02 12:20:10.595393+00
698a852c-fca0-41ec-9cd9-8203c377903c	ed64b01a-d284-4973-a3f3-a4f19b3c38d0	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "15200000", "vnp_TxnRef": "ed64b01ad2844973a3f3a4f19b3c38d0", "vnp_PayDate": "20260802192054", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI 9ce23bfc-f82f-4df3-bcb0-d520925f6c98", "vnp_BankTranNo": "VNP15644039", "vnp_SecureHash": "872b3b2df0719a054f0675ad64da6f84049970adfe88937e8b4b036a2a4f876f6954ced383466af242e1feb6d49e98ad248e131b685cd3934299e871a4296d5e", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15644039", "vnp_TransactionStatus": "00"}	2026-08-02 12:21:00.564159+00
72737e4a-77cf-4975-a02f-14f46adc96a7	d87f7b58-7a7b-41ee-ac8d-494c121ffe6f	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "190000.00", "method": "PAYPAL"}	2026-08-04 14:53:29.077785+00
4f21371b-148a-46e2-b18e-ebb10816b83b	d87f7b58-7a7b-41ee-ac8d-494c121ffe6f	PENDING	SUCCESS	PAYPAL_RETURN	COMPLETED	COMPLETED	t	\N	{"id": "9U714887HP547382X", "links": "[{'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/9U714887HP547382X', 'rel': 'self', 'method': 'GET'}]", "payer": "{'name': {'given_name': 'John', 'surname': 'Doe'}, 'email_address': 'sb-t4vqv45059846@personal.example.com', 'payer_id': '8M6T7RZJ2WS6Y', 'address': {'country_code': 'VN'}}", "status": "COMPLETED", "payment_source": "{'paypal': {'email_address': 'sb-t4vqv45059846@personal.example.com', 'account_id': '8M6T7RZJ2WS6Y', 'account_status': 'VERIFIED', 'name': {'given_name': 'John', 'surname': 'Doe'}, 'address': {'country_code': 'VN'}}}", "purchase_units": "[{'reference_id': 'd87f7b58-7a7b-41ee-ac8d-494c121ffe6f', 'shipping': {'name': {'full_name': 'John Doe'}, 'address': {'address_line_1': 'Vietnam Main Street', 'admin_area_2': 'Hanoi', 'admin_area_1': 'Vietnam', 'postal_code': '100000', 'country_code': 'VN'}}, 'payments': {'captures': [{'id': '9FK08366RA062743N', 'status': 'COMPLETED', 'amount': {'currency_code': 'USD', 'value': '7.60'}, 'final_capture': True, 'seller_protection': {'status': 'ELIGIBLE', 'dispute_categories': ['ITEM_NOT_RECEIVED', 'UNAUTHORIZED_TRANSACTION']}, 'seller_receivable_breakdown': {'gross_amount': {'currency_code': 'USD', 'value': '7.60'}, 'paypal_fee': {'currency_code': 'USD', 'value': '0.87'}, 'net_amount': {'currency_code': 'USD', 'value': '6.73'}}, 'links': [{'href': 'https://api.sandbox.paypal.com/v2/payments/captures/9FK08366RA062743N', 'rel': 'self', 'method': 'GET'}, {'href': 'https://api.sandbox.paypal.com/v2/payments/captures/9FK08366RA062743N/refund', 'rel': 'refund', 'method': 'POST'}, {'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/9U714887HP547382X', 'rel': 'up', 'method': 'GET'}], 'create_time': '2026-08-04T14:54:01Z', 'update_time': '2026-08-04T14:54:01Z'}]}}]"}	2026-08-04 14:54:00.666748+00
dd751532-acd5-4351-a5b8-0e979487e779	5e626a67-a8ce-457d-b0c9-9bd5e0a3522e	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "279000.00", "method": "VNPAY"}	2026-08-06 12:12:37.549154+00
bd129dfd-43b6-445f-9578-fc04da98862b	5e626a67-a8ce-457d-b0c9-9bd5e0a3522e	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "27900000", "vnp_TxnRef": "5e626a67a8ce457db0c99bd5e0a3522e", "vnp_PayDate": "20260806191259", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI 533600da-cf60-4155-b812-c255add2ef45", "vnp_BankTranNo": "VNP15648800", "vnp_SecureHash": "328635fd15349528b60f91d17508f4384c13eff1b130d16abd96a6702cb0f6fb7126926114e6af5e1840d77cf4195668c94add8bf909250b3583b1a447d7f440", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15648800", "vnp_TransactionStatus": "00"}	2026-08-06 12:13:05.892086+00
c9c4c4e8-e2a0-428f-84d6-a93eeede0db5	f94c0d9e-6e84-4872-8a95-29b629581779	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "121500.00", "method": "VNPAY"}	2026-08-07 09:02:40.587399+00
63a3964b-b222-43f8-8a2a-2121ef422524	f94c0d9e-6e84-4872-8a95-29b629581779	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "12150000", "vnp_TxnRef": "f94c0d9e6e8448728a9529b629581779", "vnp_PayDate": "20260807160332", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI b23ea768-02e2-4241-90a7-fcc4c22d1dd2", "vnp_BankTranNo": "VNP15649648", "vnp_SecureHash": "4b96492547a8cfc8c1f1d7bf1db92d16ac665e90df59e40a3dc420b9ff1fb07ea97f1f3cd1ebdc386259111219f27a94bb1478a2d6b4440021d14e1599a09b32", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15649648", "vnp_TransactionStatus": "00"}	2026-08-07 09:03:35.399937+00
111fd66e-2c06-4cb6-aeed-a912eb5d3d3b	f94c0d9e-6e84-4872-8a95-29b629581779	SUCCESS	SUCCESS	QUERY_DR	00	00	\N	Matched	{"vnp_Amount": "12150000", "vnp_TxnRef": "f94c0d9e6e8448728a9529b629581779", "vnp_Command": "querydr", "vnp_Message": "QueryDR success", "vnp_PayDate": "20260807160332", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_OrderInfo": "Thanh toan ve CineAI b23ea768-02e2-4241-90a7-fcc4c22d1dd2", "vnp_ResponseId": "493416b3007e4a048d11663bf7e1dcf2", "vnp_SecureHash": "f2deb1d82b336911ce88e5ccde97f314a7cf0e960edf434497d5573b7c6ac60495eeaa7c6a55a0495747076ba22e89fbe13a7953914e124db76f34fbbb96e583", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15649648", "vnp_TransactionType": "01", "vnp_TransactionStatus": "00"}	2026-08-07 09:08:16.550053+00
786fd87c-1611-4e5f-877b-4b8b18ac0f01	a6d2bd6f-a050-4101-a034-e6dbdd22c111	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "279000.00", "method": "VNPAY"}	2026-08-10 06:00:14.930387+00
910c5dff-19de-4587-b33a-1e88e1078b7a	a6d2bd6f-a050-4101-a034-e6dbdd22c111	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "27900000", "vnp_TxnRef": "a6d2bd6fa0504101a034e6dbdd22c111", "vnp_PayDate": "20260810130040", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI a72593a3-4040-4aa9-a352-3f050a6faf31", "vnp_BankTranNo": "VNP15651555", "vnp_SecureHash": "f0647be314866f507a574051eaaf8be5c442f31fbca940147a01455b8e97610550f26f2acf6f463ecf1136dfd20e5884ba1498eff125414062332e8a71f0d900", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15651555", "vnp_TransactionStatus": "00"}	2026-08-10 06:00:45.727464+00
b4956372-a411-4062-b152-59b23275d5d4	a6d2bd6f-a050-4101-a034-e6dbdd22c111	SUCCESS	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "27900000", "vnp_TxnRef": "a6d2bd6fa0504101a034e6dbdd22c111", "vnp_PayDate": "20260810130040", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI a72593a3-4040-4aa9-a352-3f050a6faf31", "vnp_BankTranNo": "VNP15651555", "vnp_SecureHash": "f0647be314866f507a574051eaaf8be5c442f31fbca940147a01455b8e97610550f26f2acf6f463ecf1136dfd20e5884ba1498eff125414062332e8a71f0d900", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15651555", "vnp_TransactionStatus": "00"}	2026-08-10 06:00:54.599339+00
bc184b7b-0040-454a-9dd1-dd4777b60e77	714ec43c-14d2-4ff2-b138-ad80b163c92f	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "90000.00", "method": "PAYPAL"}	2026-08-10 06:36:43.330425+00
d98edcf8-3098-4252-9ba1-858cc4f4b283	714ec43c-14d2-4ff2-b138-ad80b163c92f	PENDING	SUCCESS	PAYPAL_RETURN	COMPLETED	COMPLETED	t	\N	{"id": "2VS37002Y1970705T", "links": "[{'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/2VS37002Y1970705T', 'rel': 'self', 'method': 'GET'}]", "payer": "{'name': {'given_name': 'John', 'surname': 'Doe'}, 'email_address': 'sb-t4vqv45059846@personal.example.com', 'payer_id': '8M6T7RZJ2WS6Y', 'address': {'country_code': 'VN'}}", "status": "COMPLETED", "payment_source": "{'paypal': {'email_address': 'sb-t4vqv45059846@personal.example.com', 'account_id': '8M6T7RZJ2WS6Y', 'account_status': 'VERIFIED', 'name': {'given_name': 'John', 'surname': 'Doe'}, 'address': {'country_code': 'VN'}}}", "purchase_units": "[{'reference_id': '714ec43c-14d2-4ff2-b138-ad80b163c92f', 'shipping': {'name': {'full_name': 'John Doe'}, 'address': {'address_line_1': 'Vietnam Main Street', 'admin_area_2': 'Hanoi', 'admin_area_1': 'Vietnam', 'postal_code': '100000', 'country_code': 'VN'}}, 'payments': {'captures': [{'id': '1CX51277C0098293D', 'status': 'COMPLETED', 'amount': {'currency_code': 'USD', 'value': '3.60'}, 'final_capture': True, 'seller_protection': {'status': 'ELIGIBLE', 'dispute_categories': ['ITEM_NOT_RECEIVED', 'UNAUTHORIZED_TRANSACTION']}, 'seller_receivable_breakdown': {'gross_amount': {'currency_code': 'USD', 'value': '3.60'}, 'paypal_fee': {'currency_code': 'USD', 'value': '0.67'}, 'net_amount': {'currency_code': 'USD', 'value': '2.93'}}, 'links': [{'href': 'https://api.sandbox.paypal.com/v2/payments/captures/1CX51277C0098293D', 'rel': 'self', 'method': 'GET'}, {'href': 'https://api.sandbox.paypal.com/v2/payments/captures/1CX51277C0098293D/refund', 'rel': 'refund', 'method': 'POST'}, {'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/2VS37002Y1970705T', 'rel': 'up', 'method': 'GET'}], 'create_time': '2026-08-10T06:37:10Z', 'update_time': '2026-08-10T06:37:10Z'}]}}]"}	2026-08-10 06:37:09.001952+00
158908ae-5bb6-4c80-bddc-7f60b56bf292	da813a90-6678-41b5-ba6f-0c44059028ad	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "149000.00", "method": "PAYPAL"}	2026-08-10 06:44:10.391398+00
c2114396-347d-4918-86bf-849aeaf3ba3b	da813a90-6678-41b5-ba6f-0c44059028ad	PENDING	SUCCESS	PAYPAL_RETURN	COMPLETED	COMPLETED	t	\N	{"id": "7Y595838H1888335F", "links": "[{'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/7Y595838H1888335F', 'rel': 'self', 'method': 'GET'}]", "payer": "{'name': {'given_name': 'John', 'surname': 'Doe'}, 'email_address': 'sb-t4vqv45059846@personal.example.com', 'payer_id': '8M6T7RZJ2WS6Y', 'address': {'country_code': 'VN'}}", "status": "COMPLETED", "payment_source": "{'paypal': {'email_address': 'sb-t4vqv45059846@personal.example.com', 'account_id': '8M6T7RZJ2WS6Y', 'account_status': 'VERIFIED', 'name': {'given_name': 'John', 'surname': 'Doe'}, 'address': {'country_code': 'VN'}}}", "purchase_units": "[{'reference_id': 'da813a90-6678-41b5-ba6f-0c44059028ad', 'shipping': {'name': {'full_name': 'John Doe'}, 'address': {'address_line_1': 'Vietnam Main Street', 'admin_area_2': 'Hanoi', 'admin_area_1': 'Vietnam', 'postal_code': '100000', 'country_code': 'VN'}}, 'payments': {'captures': [{'id': '3K613791WD3687918', 'status': 'COMPLETED', 'amount': {'currency_code': 'USD', 'value': '5.96'}, 'final_capture': True, 'seller_protection': {'status': 'ELIGIBLE', 'dispute_categories': ['ITEM_NOT_RECEIVED', 'UNAUTHORIZED_TRANSACTION']}, 'seller_receivable_breakdown': {'gross_amount': {'currency_code': 'USD', 'value': '5.96'}, 'paypal_fee': {'currency_code': 'USD', 'value': '0.79'}, 'net_amount': {'currency_code': 'USD', 'value': '5.17'}}, 'links': [{'href': 'https://api.sandbox.paypal.com/v2/payments/captures/3K613791WD3687918', 'rel': 'self', 'method': 'GET'}, {'href': 'https://api.sandbox.paypal.com/v2/payments/captures/3K613791WD3687918/refund', 'rel': 'refund', 'method': 'POST'}, {'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/7Y595838H1888335F', 'rel': 'up', 'method': 'GET'}], 'create_time': '2026-08-10T06:44:30Z', 'update_time': '2026-08-10T06:44:30Z'}]}}]"}	2026-08-10 06:44:28.853279+00
291dea1b-263d-4d0b-a844-79d056a66570	99dcdbe1-a87c-4f2c-8c32-7a4840440175	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "270000.00", "method": "VNPAY"}	2026-08-10 06:45:32.004295+00
e9b74fa4-53fe-4e04-986a-090019710c1e	99dcdbe1-a87c-4f2c-8c32-7a4840440175	PENDING	SUCCESS	CALLBACK	00	00	t	\N	{"vnp_Amount": "27000000", "vnp_TxnRef": "99dcdbe1a87c4f2c8c327a4840440175", "vnp_PayDate": "20260810134610", "vnp_TmnCode": "T3X2ZW00", "vnp_BankCode": "NCB", "vnp_CardType": "ATM", "vnp_OrderInfo": "Thanh toan ve CineAI dfae2120-2fcd-4778-8f30-76b37f599e56", "vnp_BankTranNo": "VNP15651608", "vnp_SecureHash": "d989f5296c1b690c057bc38844d7c6a25602e830eee91535b8433089e19b0cd7b7ea71ccb8b9e3b2188512222bbb20eea0db3a8ed98981ba0ef27e80d055536d", "vnp_ResponseCode": "00", "vnp_TransactionNo": "15651608", "vnp_TransactionStatus": "00"}	2026-08-10 06:46:19.622465+00
a26581f9-5c44-4d1b-ae66-2b65d5970b1d	eed68eff-4761-470d-9008-8c10596e0c77	\N	PENDING	CREATE	\N	\N	\N	\N	{"amount": "516000.00", "method": "PAYPAL"}	2026-08-10 08:14:49.661083+00
610d6bec-53d6-4c6e-902f-8bd014a67afd	eed68eff-4761-470d-9008-8c10596e0c77	PENDING	SUCCESS	PAYPAL_RETURN	COMPLETED	COMPLETED	t	\N	{"id": "84Y92654AM489625J", "links": "[{'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/84Y92654AM489625J', 'rel': 'self', 'method': 'GET'}]", "payer": "{'name': {'given_name': 'John', 'surname': 'Doe'}, 'email_address': 'sb-t4vqv45059846@personal.example.com', 'payer_id': '8M6T7RZJ2WS6Y', 'address': {'country_code': 'VN'}}", "status": "COMPLETED", "payment_source": "{'paypal': {'email_address': 'sb-t4vqv45059846@personal.example.com', 'account_id': '8M6T7RZJ2WS6Y', 'account_status': 'VERIFIED', 'name': {'given_name': 'John', 'surname': 'Doe'}, 'address': {'country_code': 'VN'}}}", "purchase_units": "[{'reference_id': 'eed68eff-4761-470d-9008-8c10596e0c77', 'shipping': {'name': {'full_name': 'John Doe'}, 'address': {'address_line_1': 'Vietnam Main Street', 'admin_area_2': 'Hanoi', 'admin_area_1': 'Vietnam', 'postal_code': '100000', 'country_code': 'VN'}}, 'payments': {'captures': [{'id': '7KJ106380R0551117', 'status': 'COMPLETED', 'amount': {'currency_code': 'USD', 'value': '20.64'}, 'final_capture': True, 'seller_protection': {'status': 'ELIGIBLE', 'dispute_categories': ['ITEM_NOT_RECEIVED', 'UNAUTHORIZED_TRANSACTION']}, 'seller_receivable_breakdown': {'gross_amount': {'currency_code': 'USD', 'value': '20.64'}, 'paypal_fee': {'currency_code': 'USD', 'value': '1.52'}, 'net_amount': {'currency_code': 'USD', 'value': '19.12'}}, 'links': [{'href': 'https://api.sandbox.paypal.com/v2/payments/captures/7KJ106380R0551117', 'rel': 'self', 'method': 'GET'}, {'href': 'https://api.sandbox.paypal.com/v2/payments/captures/7KJ106380R0551117/refund', 'rel': 'refund', 'method': 'POST'}, {'href': 'https://api.sandbox.paypal.com/v2/checkout/orders/84Y92654AM489625J', 'rel': 'up', 'method': 'GET'}], 'create_time': '2026-08-10T08:15:29Z', 'update_time': '2026-08-10T08:15:29Z'}]}}]"}	2026-08-10 08:15:28.126576+00
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.payments (id, booking_id, user_id, amount, payment_method, status, transaction_id, paid_at, created_at, updated_at, provider_ref, provider_transaction_no, bank_transaction_no, bank_code, card_type, response_code, provider_status, signature_valid, provider_paid_at, last_verified_at, refund_request_id, refund_transaction_no, refund_response_code, refund_provider_status, refund_error, refund_attempts, refund_requested_at, refunded_at, idempotency_key, checkout_url) FROM stdin;
1b01f32e-8c72-4ca6-b432-0e0d0c529c5e	0c6f3ae9-dfaa-4713-91e9-6715e8f3b78d	774593d4-5da2-440d-8de6-3ea646880bd1	120000.00	Ví Momo	SUCCESS	\N	2026-07-28 12:03:33.266793+00	2026-07-28 12:03:33.184941+00	2026-07-28 12:03:33.184941+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
12c524fc-d99f-433c-850e-d0439d6a2858	1860f4e8-918e-4597-a86d-2577be728613	774593d4-5da2-440d-8de6-3ea646880bd1	150000.00	Thẻ ATM/Tín Dụng	SUCCESS	\N	2026-07-29 06:45:07.501548+00	2026-07-29 06:45:07.45813+00	2026-07-29 06:45:07.45813+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
b208401d-ad2c-4225-beef-97b1d9e55d26	ff8333f4-1be5-4a74-9b3d-e3ee400772d9	774593d4-5da2-440d-8de6-3ea646880bd1	216000.00	Ví Momo	SUCCESS	\N	2026-07-29 07:21:40.168468+00	2026-07-29 07:21:40.12972+00	2026-07-29 07:21:40.12972+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
7545c5fe-63db-4ff5-957c-c7f1fb75a0ec	751d1181-addc-4100-a0d6-da785f9468b4	774593d4-5da2-440d-8de6-3ea646880bd1	120000.00	Ví Momo	SUCCESS	\N	2026-07-29 13:15:19.741631+00	2026-07-29 13:15:19.656453+00	2026-07-29 13:15:19.656453+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
96b023ab-02f1-449b-a1bb-af6b1d3e8fce	4b3483f4-1f1a-454c-9871-63b55cdf0c73	774593d4-5da2-440d-8de6-3ea646880bd1	120000.00	Ví Momo	SUCCESS	\N	2026-07-29 13:38:47.803683+00	2026-07-29 13:38:47.693278+00	2026-07-29 13:38:47.693278+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
5e1ca009-ad53-4105-89b8-86b4f4e385fe	3e42ae6b-29d8-45ea-b80c-e7b5ddf1053d	774593d4-5da2-440d-8de6-3ea646880bd1	120000.00	Ví Momo	SUCCESS	\N	2026-07-29 13:58:50.867656+00	2026-07-29 13:58:50.835336+00	2026-07-29 13:58:50.835336+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
c2299181-dcca-4009-95f7-d7b884e8f0b2	73b8eba5-97fd-4d48-a164-863910d1a5be	774593d4-5da2-440d-8de6-3ea646880bd1	240000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 13:47:52.284787+00	2026-07-30 13:52:55.084284+00	CINEAIc2299181dcca400995f7d7b884e8f0b2	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
3b4769c9-4b20-4330-b695-fc60e66ff2ea	3b9c285f-6412-4029-bc43-ae7b5844fcf3	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 13:59:10.738511+00	2026-07-30 14:04:11.49818+00	CINEAI3b4769c94b204330b695fc60e66ff2ea	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
cef71dea-8768-44ee-bb8b-9cbadbd7cbd2	1efcbfa4-9403-4e1b-9e14-e1db5c77b3be	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 14:09:40.410112+00	2026-07-30 14:14:48.569094+00	CINEAIcef71dea876844eebb8b9cbadbd7cbd2	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
eae490bd-9dcb-4f0d-b6cd-a5598683d386	56713ef8-1dca-47a4-ae27-bf32844a5374	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 14:15:24.895616+00	2026-07-30 14:20:33.731402+00	CINEAIeae490bd9dcb4f0db6cda5598683d386	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
a9995a73-731b-43a5-8cc5-6a394d19733c	accae566-5f10-4fd1-836e-cb32734387b4	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 14:30:35.451296+00	2026-07-30 14:35:36.551421+00	CINEAIa9995a73731b43a58cc56a394d19733c	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
5abe8e3e-470b-475e-b124-75b0099f246d	bdb5e799-58f7-4567-bf28-0e90dd0bf150	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 14:41:22.961501+00	2026-07-30 14:46:29.430361+00	CINEAI5abe8e3e470b475eb12475b0099f246d	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
d7603057-3026-4d8f-add7-de9d51026a0b	2d68fae4-8230-4979-98fb-29e40c7cb51f	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 14:44:47.434261+00	2026-07-30 14:49:55.062497+00	CINEAId760305730264d8fadd7de9d51026a0b	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
ce9da916-dd49-42da-8016-61cfad7e89c8	9c67fe1e-28e4-43c0-8c49-995c5c45c01e	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 14:47:46.239532+00	2026-07-30 14:52:47.651998+00	CINEAIce9da916dd4942da801661cfad7e89c8	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
755c3683-6577-4082-a620-852a731266db	8a3d4fcd-517f-40cf-8781-792be6b6cd48	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 14:49:55.224806+00	2026-07-30 14:55:07.945312+00	CINEAI755c368365774082a620852a731266db	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
3413f116-8244-4beb-8fce-88e88456d8cb	49b97e83-6d89-4749-aeb8-538a051382c8	774593d4-5da2-440d-8de6-3ea646880bd1	152000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 14:51:59.322013+00	2026-07-30 14:57:08.012443+00	CINEAI3413f11682444beb8fce88e88456d8cb	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
6ebab602-0b2c-433e-b07c-e48a258e589c	03e882eb-80ac-43d1-ac0d-3b9961e38314	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 14:54:00.790224+00	2026-07-30 14:59:01.590631+00	CINEAI6ebab6020b2c433eb07ce48a258e589c	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
d3c012b2-c6ea-4a2a-b88d-a528a622bfc9	8e9cd9c8-484d-41e2-9f8f-b7189880442a	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 14:58:10.645723+00	2026-07-30 15:03:26.237836+00	CINEAId3c012b2c6ea4a2ab88da528a622bfc9	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
549c3381-7b66-42d7-8ae5-1b4e900ce2a4	197f15c6-3442-41cf-b4d9-bda942d5ae61	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 15:04:25.974217+00	2026-07-30 15:09:38.392143+00	CINEAI549c33817b6642d78ae51b4e900ce2a4	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
2626c50e-4260-43f3-9b71-f2e32c3054e4	2a99efd7-7196-4f63-ac4b-f3670caed351	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	SUCCESS	15641736	2026-07-30 15:12:17.241709+00	2026-07-30 15:11:33.207188+00	2026-07-30 15:12:17.182525+00	CINEAI2626c50e426043f39b71f2e32c3054e4	15641736	VNP15641736	NCB	ATM	00	00	t	2026-07-30 15:12:11+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
c2ee005d-f71b-48bd-9199-ef30bc2d65be	c9f07c97-59f5-4dbd-8422-496df3f8f589	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 15:08:57.858254+00	2026-07-30 15:14:09.005739+00	CINEAIc2ee005df71b48bd9199ef30bc2d65be	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
dbf53924-2aa0-484e-bbb1-3b0c73a221da	9c735dd5-26fc-4ca8-979c-5c529a8681b6	774593d4-5da2-440d-8de6-3ea646880bd1	152000.00	VNPAY	SUCCESS	15641741	2026-07-30 15:17:29.830796+00	2026-07-30 15:16:55.907954+00	2026-07-30 15:17:29.749811+00	CINEAIdbf539242aa0484ebbb13b0c73a221da	15641741	VNP15641741	NCB	ATM	00	00	t	2026-07-30 15:17:24+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
c4a220f9-4dec-4190-85a6-d98089be24b6	bcbddc3f-79b6-4d4b-af86-33a1f1e93904	774593d4-5da2-440d-8de6-3ea646880bd1	120000.00	VNPAY	SUCCESS	15641748	2026-07-30 15:23:16.065945+00	2026-07-30 15:22:43.882156+00	2026-07-30 15:23:16.006917+00	CINEAIc4a220f94dec419085a6d98089be24b6	15641748	VNP15641748	NCB	ATM	00	00	t	2026-07-30 15:23:10+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
93da291b-a389-4469-8e76-25d2a17b14a1	ffb77e65-d41f-48b7-a23a-fd0221a6c53c	774593d4-5da2-440d-8de6-3ea646880bd1	120000.00	VNPAY	SUCCESS	15641756	2026-07-30 15:34:58.38969+00	2026-07-30 15:34:25.430099+00	2026-07-30 15:34:58.344587+00	CINEAI93da291ba38944698e7625d2a17b14a1	15641756	VNP15641756	NCB	ATM	00	00	t	2026-07-30 15:34:53+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
4d4eb4cf-2ccf-4199-8e93-db441da2a02d	fa5e723c-4c12-4fd5-8708-e23052f2cee8	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	SUCCESS	15641760	2026-07-30 15:45:31.675164+00	2026-07-30 15:44:52.503513+00	2026-07-30 15:45:31.549026+00	CINEAI4d4eb4cf2ccf41998e93db441da2a02d	15641760	VNP15641760	NCB	ATM	00	00	t	2026-07-30 15:45:25+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
22dfbc5d-12fe-417f-989e-d937358baa36	d210f403-2fdd-4583-8e18-8cb7034c1a7d	774593d4-5da2-440d-8de6-3ea646880bd1	120000.00	VNPAY	SUCCESS	15641765	2026-07-30 15:49:53.783663+00	2026-07-30 15:49:21.021364+00	2026-07-30 15:49:53.73538+00	CINEAI22dfbc5d12fe417f989ed937358baa36	15641765	VNP15641765	NCB	ATM	00	00	t	2026-07-30 15:49:46+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
76e6bd46-f888-4c0b-a2b1-bd761650d910	8eb7e27f-5167-4c41-81a0-cde73361f10f	774593d4-5da2-440d-8de6-3ea646880bd1	120000.00	VNPAY	SUCCESS	15641787	2026-07-30 16:15:14.17514+00	2026-07-30 16:14:39.281537+00	2026-07-30 16:15:14.014148+00	CINEAI76e6bd46f8884c0ba2b1bd761650d910	15641787	VNP15641787	NCB	ATM	00	00	t	2026-07-30 16:15:06+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
43d70deb-9de2-46da-87fd-43ecaac8b004	3f3d7716-141f-4302-8093-5a9f1fc46235	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	SUCCESS	15641799	2026-07-30 16:25:32.808989+00	2026-07-30 16:24:55.042387+00	2026-07-30 16:42:45.600579+00	CINEAI43d70deb9de246da87fd43ecaac8b004	15641799	VNP15641799	NCB	ATM	00	00	t	2026-07-30 16:25:28+00	2026-07-30 16:42:45.936706+00	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
c7d5e319-e1cd-4f54-b2fd-1cc46657ba55	a4349175-2741-4061-be9a-d488c5fd959d	774593d4-5da2-440d-8de6-3ea646880bd1	152000.00	VNPAY	SUCCESS	15641885	2026-07-30 18:28:07.16613+00	2026-07-30 18:27:32.449805+00	2026-07-30 18:28:07.074219+00	c7d5e319-e1cd-4f54-b2fd-1cc46657ba55	15641885	VNP15641885	NCB	ATM	00	00	t	2026-07-30 18:27:59+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
d8a76cc2-c418-49f4-8b73-2be55eec05b9	149d1808-0fe7-4c52-9947-4af44f8a9fe6	774593d4-5da2-440d-8de6-3ea646880bd1	240000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 18:43:58.489785+00	2026-07-30 18:49:11.815343+00	d8a76cc2-c418-49f4-8b73-2be55eec05b9	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
3728a5ed-44ba-4080-b3d5-2d507d45a70e	6bbd507d-85d0-4298-ab5f-73845dc0a90a	774593d4-5da2-440d-8de6-3ea646880bd1	120000.00	VNPAY	SUCCESS	15641901	2026-07-30 18:55:56.453815+00	2026-07-30 18:55:04.743757+00	2026-07-30 18:55:56.340076+00	3728a5ed-44ba-4080-b3d5-2d507d45a70e	15641901	VNP15641901	NCB	ATM	00	00	t	2026-07-30 18:55:49+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
5c335df6-ca1c-40d1-86e8-b15a30d87ae6	6dafd69b-5b48-449e-8ffd-c998ec018a13	774593d4-5da2-440d-8de6-3ea646880bd1	360000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 18:51:10.704496+00	2026-07-30 18:56:21.692003+00	5c335df6-ca1c-40d1-86e8-b15a30d87ae6	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
2c39e29c-4b0a-4bdf-ae34-da03a258e5b2	1fcbccd3-6e37-46b3-b44d-4d0f5fed1550	774593d4-5da2-440d-8de6-3ea646880bd1	120000.00	VNPAY	SUCCESS	15641903	2026-07-30 19:06:38.049828+00	2026-07-30 19:05:28.932346+00	2026-07-30 19:06:37.975348+00	2c39e29c-4b0a-4bdf-ae34-da03a258e5b2	15641903	VNP15641903	NCB	ATM	00	00	t	2026-07-30 19:05:54+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
12c50ea6-c2ab-45ed-8a28-c5e69c461771	4ab4de29-b4a0-474b-ac6b-fb4c2ee06d75	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	SUCCESS	15641917	2026-07-30 19:16:07.943227+00	2026-07-30 19:15:34.56222+00	2026-07-30 19:16:07.911242+00	12c50ea6-c2ab-45ed-8a28-c5e69c461771	15641917	VNP15641917	NCB	ATM	00	00	t	2026-07-30 19:16:02+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
9e63ae8e-ff7b-48f8-960f-aa056c258949	85a22a13-c8ac-48f5-b50c-a8b9a22b2f10	774593d4-5da2-440d-8de6-3ea646880bd1	152000.00	VNPAY	SUCCESS	15641919	2026-07-30 19:40:06.049282+00	2026-07-30 19:39:25.690697+00	2026-07-30 19:40:05.926877+00	9e63ae8e-ff7b-48f8-960f-aa056c258949	15641919	VNP15641919	NCB	ATM	00	00	t	2026-07-30 19:39:59+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
465ac0fb-c411-4e47-a3b1-db9a2b10e4fd	651d5cb6-a9bd-48ad-9404-09ab5e0ee935	774593d4-5da2-440d-8de6-3ea646880bd1	120000.00	VNPAY	SUCCESS	15641920	2026-07-30 19:44:16.484394+00	2026-07-30 19:42:47.641558+00	2026-07-30 19:44:16.429214+00	465ac0fb-c411-4e47-a3b1-db9a2b10e4fd	15641920	VNP15641920	NCB	ATM	00	00	t	2026-07-30 19:44:11+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
e57a0346-9648-49e8-abe5-0b784ec4eedd	24e7dd49-6234-45fb-8a5d-2614ae908010	774593d4-5da2-440d-8de6-3ea646880bd1	76000.00	VNPAY	EXPIRED	\N	\N	2026-07-30 19:51:40.597545+00	2026-07-30 19:56:49.662583+00	e57a0346-9648-49e8-abe5-0b784ec4eedd	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
ed64b01a-d284-4973-a3f3-a4f19b3c38d0	9ce23bfc-f82f-4df3-bcb0-d520925f6c98	774593d4-5da2-440d-8de6-3ea646880bd1	152000.00	VNPAY	SUCCESS	15644039	2026-08-02 12:21:00.599836+00	2026-08-02 12:20:10.595393+00	2026-08-02 12:21:00.564159+00	ed64b01ad2844973a3f3a4f19b3c38d0	15644039	VNP15644039	NCB	ATM	00	00	t	2026-08-02 12:20:54+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
d87f7b58-7a7b-41ee-ac8d-494c121ffe6f	2a5ef731-b92b-4fec-98e0-7ee13ca2bdf2	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	190000.00	PAYPAL	SUCCESS	9FK08366RA062743N	2026-08-04 14:54:02.277851+00	2026-08-04 14:53:29.077785+00	2026-08-04 14:54:00.666748+00	9U714887HP547382X	9FK08366RA062743N	\N	\N	\N	COMPLETED	COMPLETED	t	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
5e626a67-a8ce-457d-b0c9-9bd5e0a3522e	533600da-cf60-4155-b812-c255add2ef45	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	279000.00	VNPAY	SUCCESS	15648800	2026-08-06 12:13:06.217019+00	2026-08-06 12:12:37.549154+00	2026-08-06 12:13:05.892086+00	5e626a67a8ce457db0c99bd5e0a3522e	15648800	VNP15648800	NCB	ATM	00	00	t	2026-08-06 12:12:59+00	\N	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
f94c0d9e-6e84-4872-8a95-29b629581779	b23ea768-02e2-4241-90a7-fcc4c22d1dd2	6cb9ebe0-9d8a-49c6-bcce-6669fd5ca41b	121500.00	VNPAY	SUCCESS	15649648	2026-08-07 09:03:35.458604+00	2026-08-07 09:02:40.587399+00	2026-08-07 09:08:16.550053+00	f94c0d9e6e8448728a9529b629581779	15649648	VNP15649648	NCB	ATM	00	00	t	2026-08-07 09:03:32+00	2026-08-07 09:08:16.977439+00	\N	\N	\N	\N	\N	0	\N	\N	\N	\N
a6d2bd6f-a050-4101-a034-e6dbdd22c111	a72593a3-4040-4aa9-a352-3f050a6faf31	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	279000.00	VNPAY	SUCCESS	15651555	2026-08-10 06:00:45.840138+00	2026-08-10 06:00:14.930387+00	2026-08-10 06:00:45.727464+00	a6d2bd6fa0504101a034e6dbdd22c111	15651555	VNP15651555	NCB	ATM	00	00	t	2026-08-10 06:00:40+00	\N	\N	\N	\N	\N	\N	0	\N	\N	payment-b7f215d3-9da6-4cdd-b830-88f2ebd8746a	https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?vnp_Amount=27900000&vnp_Command=pay&vnp_CreateDate=20260810130015&vnp_CurrCode=VND&vnp_ExpireDate=20260810130514&vnp_IpAddr=172.18.0.1&vnp_Locale=vn&vnp_OrderInfo=Thanh+toan+ve+CineAI+a72593a3-4040-4aa9-a352-3f050a6faf31&vnp_OrderType=other&vnp_ReturnUrl=https%3A%2F%2Fexacting-glenda-usurpingly.ngrok-free.dev%2Fcheckout%2Fvnpay-return&vnp_TmnCode=T3X2ZW00&vnp_TxnRef=a6d2bd6fa0504101a034e6dbdd22c111&vnp_Version=2.1.0&vnp_SecureHash=f514f9b4513f11c904991709c8b76355133b6faa1f02e73f819e7a0a41621e0c47aff0acf7bdfc75c9fa633cc9f859b9dd207597804c0e2334e670b7676efd1c
714ec43c-14d2-4ff2-b138-ad80b163c92f	2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	90000.00	PAYPAL	SUCCESS	1CX51277C0098293D	2026-08-10 06:37:10.827648+00	2026-08-10 06:36:43.330425+00	2026-08-10 06:37:09.001952+00	2VS37002Y1970705T	1CX51277C0098293D	\N	\N	\N	COMPLETED	COMPLETED	t	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	payment-b2469d28-f2d3-4edf-9f53-d5d848da5bb8	https://www.sandbox.paypal.com/checkoutnow?token=2VS37002Y1970705T
da813a90-6678-41b5-ba6f-0c44059028ad	9257dcad-0488-420e-a6eb-be52650d2702	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	149000.00	PAYPAL	SUCCESS	3K613791WD3687918	2026-08-10 06:44:31.043389+00	2026-08-10 06:44:10.391398+00	2026-08-10 06:44:28.853279+00	7Y595838H1888335F	3K613791WD3687918	\N	\N	\N	COMPLETED	COMPLETED	t	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	payment-f928b367-b647-4259-b63a-19aaee8c807b	https://www.sandbox.paypal.com/checkoutnow?token=7Y595838H1888335F
99dcdbe1-a87c-4f2c-8c32-7a4840440175	dfae2120-2fcd-4778-8f30-76b37f599e56	5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	270000.00	VNPAY	SUCCESS	15651608	2026-08-10 06:46:19.904261+00	2026-08-10 06:45:32.004295+00	2026-08-10 06:46:19.622465+00	99dcdbe1a87c4f2c8c327a4840440175	15651608	VNP15651608	NCB	ATM	00	00	t	2026-08-10 06:46:10+00	\N	\N	\N	\N	\N	\N	0	\N	\N	payment-b1652b29-bd04-4244-9d4a-7f7fae563227	https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?vnp_Amount=27000000&vnp_Command=pay&vnp_CreateDate=20260810134532&vnp_CurrCode=VND&vnp_ExpireDate=20260810135031&vnp_IpAddr=172.18.0.1&vnp_Locale=vn&vnp_OrderInfo=Thanh+toan+ve+CineAI+dfae2120-2fcd-4778-8f30-76b37f599e56&vnp_OrderType=other&vnp_ReturnUrl=https%3A%2F%2Fexacting-glenda-usurpingly.ngrok-free.dev%2Fcheckout%2Fvnpay-return&vnp_TmnCode=T3X2ZW00&vnp_TxnRef=99dcdbe1a87c4f2c8c327a4840440175&vnp_Version=2.1.0&vnp_SecureHash=f73434ca9e76414c7b740d23e0e17ff86f6169ab58a96d98eae5e31e9a4d7a01550f00226c61ad829fa7208c1723f93a48daf0d7acf71d4f365fa8459db736ef
eed68eff-4761-470d-9008-8c10596e0c77	3c845d97-791d-45d8-9c7e-86213bd6ee02	a91cb727-754e-42ba-a15c-8a1466e8ef0a	516000.00	PAYPAL	SUCCESS	7KJ106380R0551117	2026-08-10 08:15:29.721951+00	2026-08-10 08:14:49.661083+00	2026-08-10 08:15:28.126576+00	84Y92654AM489625J	7KJ106380R0551117	\N	\N	\N	COMPLETED	COMPLETED	t	\N	\N	\N	\N	\N	\N	\N	0	\N	\N	payment-6a84e4fb-dab3-4c1c-b408-bebd0c12bdea	https://www.sandbox.paypal.com/checkoutnow?token=84Y92654AM489625J
\.


--
-- Data for Name: pricing_rules; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.pricing_rules (id, name, branch_id, screen_type, day_of_week, starts_on, ends_on, time_from, time_to, multiplier, surcharge, priority, is_active) FROM stdin;
\.


--
-- Data for Name: promotion_redemptions; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.promotion_redemptions (id, promotion_id, user_id, booking_id, payment_id, discount_amount, status, created_at) FROM stdin;
\.


--
-- Data for Name: promotions; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.promotions (id, code, name, discount_type, discount_value, max_discount, min_order_amount, starts_at, ends_at, usage_limit, used_count, is_active, created_by, created_at, updated_at, per_user_limit, budget_amount, used_amount, branch_ids, movie_ids, payment_methods, excluded_dates) FROM stdin;
ad9f692e-1a7a-46fd-914b-825582e0f1a0	CINEABC	Lần đầu đến với CineAI	PERCENT	10.00	\N	0.00	2026-07-29 07:17:00+00	2026-08-18 07:17:00+00	1	1	t	e7288ffc-c117-4eb5-a137-6011c94c0b5c	2026-07-29 07:20:40.941535+00	2026-07-29 15:27:53.769129+00	\N	\N	0.00	[]	[]	[]	[]
95b75f20-e277-464f-99ef-23bc8422c302	SCHOOLCINE2026	Khuyến mãi tựu trường	PERCENT	10.00	200000.00	0.00	2026-08-06 13:12:00+00	2026-09-05 13:12:00+00	100	0	t	e7288ffc-c117-4eb5-a137-6011c94c0b5c	2026-08-06 13:14:16.637516+00	2026-08-06 13:14:16.637516+00	\N	\N	0.00	[]	[]	[]	[]
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.roles (id, code, name) FROM stdin;
3	BRANCH_ADMIN	Branch Administrator
1	CUSTOMER	Khách hàng
2	SUPER_ADMIN	Quản trị viên
\.


--
-- Data for Name: seat_holds; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.seat_holds (id, showtime_id, seat_id, user_id, expires_at, created_at) FROM stdin;
\.


--
-- Data for Name: seat_types; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.seat_types (id, code, name, price_multiplier) FROM stdin;
1	STANDARD	Standard	1.00
2	VIP	VIP	1.25
3	COUPLE	Couple	2.00
\.


--
-- Data for Name: seats; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.seats (id, auditorium_id, seat_row, seat_number, seat_type_id, is_active) FROM stdin;
3f5f8c3c-ad1d-4b0b-bba3-0695bbb2e2e8	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	A	1	1	t
0ab2cfd0-91af-406e-bab4-b0d686cc9080	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	A	2	1	t
5cf2d14b-717b-4c12-a992-020be91992b0	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	A	3	1	t
d48821d4-15d5-44ac-a983-c01222f6df3f	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	A	4	1	t
25eae2e2-84b0-4afc-b3c9-63c500ea3879	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	A	5	1	t
03efca4b-c0a2-45b8-8212-fbc109c90f90	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	A	6	1	t
efc80c2a-90f1-40d3-bda8-4664d2e29853	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	A	7	1	t
9ba6db82-6e32-4413-8a23-de398df9ffb1	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	A	8	1	t
aa2f6757-f430-4564-abf7-5ff595888024	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	A	9	1	t
2ed79287-99c4-4923-8aa9-a9e39223ad74	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	A	10	1	t
f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	A	11	1	t
68768715-f9e6-4f9c-a7c0-efbc83edfc75	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	A	12	1	t
2197365a-110a-4b65-bc3f-5ed49d37e40f	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	B	1	1	t
20113a87-6559-4599-8994-605d0dd1fd0b	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	B	2	1	t
b3626270-7582-4dd8-9cea-e1900f7a57b3	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	B	3	1	t
d2da06a2-22b4-4e90-81f6-86e76409d10b	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	B	4	1	t
fee8040f-9977-4c28-8468-416233221d55	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	B	5	1	t
d883f4cb-f686-4dfc-9377-3889444cc346	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	B	6	1	t
90b77238-2a33-4b2f-acbe-491ffe39a0f0	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	B	7	1	t
2a8708c6-a4dc-483a-9294-cc483b9ed18c	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	B	8	1	t
dfb53ce2-0638-4e72-95e3-26ee25c77007	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	B	9	1	t
e57ad5e9-f5ab-480f-9153-7dfa510e2a70	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	B	10	1	t
1129090f-3c21-49d4-b882-b3c62f54be1a	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	B	11	1	t
9d63a83c-2e1b-40cd-b62d-fbc0028609c4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	B	12	1	t
98927e1f-7ef3-4e88-97ea-2417fbb8cae1	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	C	1	1	t
05fc7ad9-cb5c-4142-835a-63d50b447c87	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	C	2	1	t
7abba9a5-c2df-40ed-b2a7-b5f070d3bbcf	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	C	3	1	t
2009776c-e12c-4a34-a025-acb076d79d10	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	C	4	1	t
a369113e-3140-40bb-b73d-ff62147d766a	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	C	5	1	t
c9583494-ebc9-43df-a5ed-fc88cf553f0e	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	C	6	1	t
dc6f6ebd-0e3f-4a29-aa3b-52f5535b8029	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	C	7	1	t
ee3f6974-b9a2-4808-9dd5-7ec4d7cfb5fb	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	C	8	1	t
e78680bf-22c8-4b74-96f9-4edf359128d6	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	C	9	1	t
bb7adacc-7a56-450d-8421-ac0d76c60a86	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	C	10	1	t
e10cbc04-83d6-482e-b535-2c008791413d	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	C	11	1	t
72b6e982-6edd-48e6-9fd3-b347db50741a	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	C	12	1	t
10211a40-ed2c-4421-884c-04997428a230	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	D	1	1	t
fd982bff-9109-466e-92e0-9547b04df1b3	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	D	2	1	t
18d2c349-bb32-4dcd-9a97-7e0ea739b9d3	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	D	3	1	t
41e2f54f-5488-4c12-96be-fafee510617c	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	D	4	1	t
77e0c246-d4ce-46f5-bc39-c58fa01b46d3	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	D	9	1	t
424551de-17dc-4bd4-bce7-5884f68e42a8	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	D	10	1	t
9a6f14b2-d714-4f55-992c-a72eba90b296	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	D	11	1	t
219c3ea8-69c7-4346-9556-dff045486c47	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	D	12	1	t
56d69467-b789-4ff7-b6e8-9ebae933c985	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	E	1	1	t
9044f9da-239a-46ed-9888-2db2020750c5	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	E	2	1	t
829f6306-3bea-4e31-a68d-6de884a350aa	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	E	3	1	t
c46441b3-648b-4195-9cbd-0e1c857cda92	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	E	4	1	t
2caf1e11-6fb7-4cbc-b6ad-88b0416b70be	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	E	5	1	t
d82e7f38-0021-4e11-891b-f89b18ba70db	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	E	6	1	t
078e8247-f639-442f-9ed8-c10452b93473	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	E	7	1	t
5de88e3a-c599-4d7d-b4fb-35c594942a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	E	8	1	t
0ac5fb69-9f31-4daa-b5d3-80c6863eee0b	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	E	9	1	t
68a1825b-91c1-4cdf-a65d-44b968cbcfc9	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	E	10	1	t
95a11841-6c34-470a-a409-016a08f01874	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	E	11	1	t
e4b0bb01-b831-4c49-89da-4acd48f3415a	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	E	12	1	t
6a0049c3-4e9c-41ea-a70b-8d57afad8570	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	F	1	1	t
4890a7b7-9d72-4af3-93f1-4ed0a490801d	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	F	2	1	t
01337a85-d154-410a-beb3-4f792bf40498	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	F	3	1	t
03ac6d00-acb0-4fc3-9f52-2743df80d989	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	F	4	1	t
b7b6cd7a-bbce-479d-aab6-17b22cba6bb8	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	F	5	1	t
1c6f9762-9331-44fd-8b02-f4563deaa9e6	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	F	6	1	t
e1934503-f88d-4161-9eb5-72818e230719	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	F	7	1	t
e7d21236-c236-4673-b175-c923ddac5ab4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	F	8	1	t
2907403d-6523-4cd9-b87f-ccb96d486e63	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	F	9	1	t
5bd7c908-d1ca-47e1-bc91-8b52cfa7e654	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	F	10	1	t
3b02466a-0968-4378-b43c-ca5bae5e7c89	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	F	11	1	t
e9918fae-aaa2-4d58-91d8-fee6808826f7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	F	12	1	t
9877bb48-d791-4144-bcf1-9ce5080fb478	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	G	1	1	t
f6232136-8398-455d-b563-2fb6be1ed3b4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	G	2	1	t
6dbd3a40-1acb-4fa5-8c83-de7cc7e430e5	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	G	3	1	t
2c9e0a0e-b1f3-446e-b4fe-88fd4f52c08c	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	G	4	1	t
089dbd8a-d5bf-44a4-ba7a-78de8df564b7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	G	5	1	t
b8a22a20-32b4-447e-9c75-444e14d30285	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	G	6	1	t
e72c461c-e4fb-4ae6-844b-d0720da99bb0	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	G	7	1	t
7ef72811-dfeb-4ee4-88b4-e9d819d3ed1f	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	G	8	1	t
3bfe097e-cb6a-44bd-a036-969e7f884488	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	G	9	1	t
11cd7ee7-f738-4230-a985-cd63a2a2e7ca	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	G	10	1	t
93e2228c-fd34-4924-9447-e32d906e1a16	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	G	11	1	t
4417d9d4-9169-4f70-9f40-72b88217053a	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	G	12	1	t
9bc96ff9-e694-4289-a32f-50bb86ed6ed0	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	H	4	1	t
8c31a803-9221-4508-8c4b-4b6777ea74d6	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	H	7	1	t
5bf36aae-d37e-4749-8445-5f55d64645fa	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	H	8	1	t
0ce39853-10f9-47a3-ab6f-eff3ae637e0a	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	H	1	3	t
1ac15795-8041-476b-8fb0-9989176fd975	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	H	9	3	t
32ca5abb-3280-46e7-b5c1-053f8169675f	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	D	8	2	t
3f1ba63f-9e5a-4165-b9ae-1bed49578d63	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	H	11	3	t
51fe1dd3-cf0f-4858-9f2b-0b548ce8d52e	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	D	7	2	t
7191355f-e232-4000-8daa-22c407f8aae5	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	D	6	2	t
7b3d1af2-9c3c-495f-a664-3dcecbd71f7a	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	H	3	3	t
80cf8fa9-5fcb-4e82-bfe9-61292bdd7bfb	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	D	5	2	t
943d99d6-c855-40f8-9fbb-bcbb24fe76d4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	H	10	3	t
9cc18b2a-ffd3-4cc6-a50c-598cd0b7e478	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	H	2	3	t
9948fb16-ee7a-407d-b5c0-939c887301cd	715df074-412b-441b-b93e-0dfa4f6ee8f9	A	1	1	t
bed46988-0b41-41dc-9524-89ee3e6417b1	715df074-412b-441b-b93e-0dfa4f6ee8f9	A	2	1	t
5fb1445a-423c-47cf-920b-f4272d2a4085	715df074-412b-441b-b93e-0dfa4f6ee8f9	A	3	1	t
24776ebc-a420-4bba-90ef-1dbd8195de82	715df074-412b-441b-b93e-0dfa4f6ee8f9	A	4	1	t
1581fb75-2708-462e-9a6f-8d8eb60ca9c7	715df074-412b-441b-b93e-0dfa4f6ee8f9	A	5	1	t
1d188b21-37c5-4049-907b-ebf1ecc08b7b	715df074-412b-441b-b93e-0dfa4f6ee8f9	A	6	1	t
66fa5e02-5866-47e5-b849-b741ac9bcc6b	715df074-412b-441b-b93e-0dfa4f6ee8f9	A	7	1	t
d6429f22-16aa-431d-bdce-02c74b61037f	715df074-412b-441b-b93e-0dfa4f6ee8f9	A	8	1	t
f0fa69a1-202a-40ce-939a-6597369ffa8e	715df074-412b-441b-b93e-0dfa4f6ee8f9	A	9	1	t
a50061e9-289f-49a4-b5bd-21f5c132c48e	715df074-412b-441b-b93e-0dfa4f6ee8f9	A	10	1	t
5042eca3-dfaa-4f3c-a99b-390eb2bd346f	715df074-412b-441b-b93e-0dfa4f6ee8f9	A	11	1	t
d9cc21ac-906f-467c-8b48-d1cc107c03d6	715df074-412b-441b-b93e-0dfa4f6ee8f9	A	12	1	t
35b057a5-149e-4788-af00-9b9cdb3ef2e6	715df074-412b-441b-b93e-0dfa4f6ee8f9	B	1	1	t
5374cf8c-c6b2-44f1-b543-a4f4c3436146	715df074-412b-441b-b93e-0dfa4f6ee8f9	B	2	1	t
1ad16442-538f-45b3-8022-155c993c2ec8	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	H	5	3	t
4e1aa614-d9fd-47d7-8b51-a838f09417e9	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	H	6	3	t
d7d85c32-42df-4dba-995e-bafa09ac2afe	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	H	12	3	t
f0da7e9c-a353-424e-a6d5-dd3606272065	715df074-412b-441b-b93e-0dfa4f6ee8f9	B	3	1	t
fa3f3560-1c57-4835-8b52-0929d9a1a0df	715df074-412b-441b-b93e-0dfa4f6ee8f9	B	4	1	t
5ba75e02-50f9-4129-acd6-184962b37ddf	715df074-412b-441b-b93e-0dfa4f6ee8f9	B	5	1	t
494d5677-2670-45ae-89a8-e6d5c647ac28	715df074-412b-441b-b93e-0dfa4f6ee8f9	B	6	1	t
537083a7-f857-4b27-8acf-fef801e08931	715df074-412b-441b-b93e-0dfa4f6ee8f9	B	7	1	t
6252496b-c7eb-44c5-957b-1b928ed5e438	715df074-412b-441b-b93e-0dfa4f6ee8f9	B	8	1	t
9a832afe-026a-4e37-8ae1-3411d66d5c84	715df074-412b-441b-b93e-0dfa4f6ee8f9	B	9	1	t
2dc05986-62ed-4f32-a370-ace16dc78bdc	715df074-412b-441b-b93e-0dfa4f6ee8f9	B	10	1	t
579a1fe3-5c59-4b34-b8c1-20a32084728b	715df074-412b-441b-b93e-0dfa4f6ee8f9	B	11	1	t
2d3dadc4-3b11-4123-97a9-43bd38d87a67	715df074-412b-441b-b93e-0dfa4f6ee8f9	B	12	1	t
56530553-9970-4b10-be51-b6011c868c73	715df074-412b-441b-b93e-0dfa4f6ee8f9	C	1	1	t
89b01a59-a19c-4091-a213-5e1657e77246	715df074-412b-441b-b93e-0dfa4f6ee8f9	C	2	1	t
32f0856a-3807-4a56-9a3d-06d513809fa1	715df074-412b-441b-b93e-0dfa4f6ee8f9	C	3	1	t
c19b61fe-1d1f-4e61-a7de-61b5bdd8c69d	715df074-412b-441b-b93e-0dfa4f6ee8f9	C	4	1	t
ce2faa2d-d8a9-4f70-ba7d-86e02987dce6	715df074-412b-441b-b93e-0dfa4f6ee8f9	C	5	1	t
bebb7495-aa9b-45c8-b349-3fa7592eb86e	715df074-412b-441b-b93e-0dfa4f6ee8f9	C	6	1	t
2ac28256-d44f-4a8c-9cde-8d34ebc6b5d5	715df074-412b-441b-b93e-0dfa4f6ee8f9	C	7	1	t
4acb5b7b-a396-41f6-bf0c-a72261de149e	715df074-412b-441b-b93e-0dfa4f6ee8f9	C	8	1	t
d662778f-64e6-4223-9ee0-8a5840138a91	715df074-412b-441b-b93e-0dfa4f6ee8f9	C	9	1	t
7e2db951-22fb-4c92-b9c1-1bd344f7c807	715df074-412b-441b-b93e-0dfa4f6ee8f9	C	10	1	t
bd47af89-3c7c-41eb-88ed-f8ce5530f977	715df074-412b-441b-b93e-0dfa4f6ee8f9	C	11	1	t
78063d79-a588-448f-b93e-a99d29ad783f	715df074-412b-441b-b93e-0dfa4f6ee8f9	C	12	1	t
71706eef-8359-4a8d-8b27-1c2af9d1877a	715df074-412b-441b-b93e-0dfa4f6ee8f9	D	1	1	t
6bfaa6d6-7288-42f4-b010-84c9d5d228b9	715df074-412b-441b-b93e-0dfa4f6ee8f9	D	2	1	t
4e8ac483-518d-47f1-a589-8216881dfb85	715df074-412b-441b-b93e-0dfa4f6ee8f9	D	3	1	t
e77f7051-a5c3-44f1-9d95-630bdf383c1c	715df074-412b-441b-b93e-0dfa4f6ee8f9	D	4	1	t
95a69e54-42f0-4a9e-8403-2a2fcd4e541c	715df074-412b-441b-b93e-0dfa4f6ee8f9	D	5	1	t
440f9ebb-96d2-47d4-a38d-003ff8389bf8	715df074-412b-441b-b93e-0dfa4f6ee8f9	D	6	1	t
b233c554-c1db-4066-aad7-0d8e1d54cb22	715df074-412b-441b-b93e-0dfa4f6ee8f9	D	7	1	t
e1f8cef9-492c-42cd-a9bf-011ec9f8ba52	715df074-412b-441b-b93e-0dfa4f6ee8f9	D	8	1	t
9008fa2c-d0fd-4659-aa32-cfa9cb8298f2	715df074-412b-441b-b93e-0dfa4f6ee8f9	D	9	1	t
38f747e5-cdf1-4da9-872a-8a36faa36c14	715df074-412b-441b-b93e-0dfa4f6ee8f9	D	10	1	t
0cbd3864-f8f4-4705-8875-29e7159cb792	715df074-412b-441b-b93e-0dfa4f6ee8f9	D	11	1	t
aa21c60c-09e0-497f-a018-fcfeb3f61a07	715df074-412b-441b-b93e-0dfa4f6ee8f9	D	12	1	t
5b2fb6d2-23d3-462d-9598-fe7b12b6ff42	715df074-412b-441b-b93e-0dfa4f6ee8f9	E	1	1	t
46334ce3-6fd1-4728-ad19-4e8002f51b00	715df074-412b-441b-b93e-0dfa4f6ee8f9	E	2	1	t
f419eedf-6008-4894-831e-fdbe105bdb97	715df074-412b-441b-b93e-0dfa4f6ee8f9	E	3	1	t
f7c92f23-7b1b-48d4-a100-223b1e1f50ae	715df074-412b-441b-b93e-0dfa4f6ee8f9	E	4	1	t
b5b1c0ea-5a0c-4307-88ca-a1c8047ff0c1	715df074-412b-441b-b93e-0dfa4f6ee8f9	E	5	1	t
afce9c0a-31fc-4242-8637-673593e0dc38	715df074-412b-441b-b93e-0dfa4f6ee8f9	E	6	1	t
4ef254c7-1eab-4694-8ac4-c5e0dfa78753	715df074-412b-441b-b93e-0dfa4f6ee8f9	E	7	1	t
77bdfa88-638c-47c7-8868-2bdb05863c85	715df074-412b-441b-b93e-0dfa4f6ee8f9	E	8	1	t
31f6701b-cb27-4f22-926e-4bfaa7987231	715df074-412b-441b-b93e-0dfa4f6ee8f9	E	9	1	t
d0a34bb1-5d97-4ae8-82e9-0e9e126cfc3e	715df074-412b-441b-b93e-0dfa4f6ee8f9	E	10	1	t
2c317398-93f8-44aa-afec-538ecb144864	715df074-412b-441b-b93e-0dfa4f6ee8f9	E	11	1	t
10a64b8d-81fa-4bcc-a7c3-e9daee642e6f	715df074-412b-441b-b93e-0dfa4f6ee8f9	E	12	1	t
d364d884-de24-441e-bd73-dedd631c3fbe	715df074-412b-441b-b93e-0dfa4f6ee8f9	F	1	1	t
cea137cb-5335-4eb5-8cf0-391675efb4e2	715df074-412b-441b-b93e-0dfa4f6ee8f9	F	2	1	t
54fe85d5-9420-494f-b38b-12370e662fb9	715df074-412b-441b-b93e-0dfa4f6ee8f9	F	3	1	t
e66bba30-04ac-43fe-b34d-7ee5e9e15b66	715df074-412b-441b-b93e-0dfa4f6ee8f9	F	4	1	t
063f9cc3-6e0e-478e-bd04-c4cee6899f27	715df074-412b-441b-b93e-0dfa4f6ee8f9	F	5	1	t
82b22a21-29ff-4e6a-926b-a8fd9c6e58c4	715df074-412b-441b-b93e-0dfa4f6ee8f9	F	6	1	t
f4927e63-f943-4e4e-be29-a65168863246	715df074-412b-441b-b93e-0dfa4f6ee8f9	F	7	1	t
36165c75-f58a-4bfb-b4d5-f77ea99a270b	715df074-412b-441b-b93e-0dfa4f6ee8f9	F	8	1	t
f90c1e6b-49eb-4e33-a269-3b73cd769cd7	715df074-412b-441b-b93e-0dfa4f6ee8f9	F	9	1	t
5b42ab39-3cd1-4662-b34a-5e9ccd89c567	715df074-412b-441b-b93e-0dfa4f6ee8f9	F	10	1	t
c90b3d01-95ac-4ad9-9f5c-8d13432cc0db	715df074-412b-441b-b93e-0dfa4f6ee8f9	F	11	1	t
1dfcb692-8a04-4127-95fd-ccac321d95db	715df074-412b-441b-b93e-0dfa4f6ee8f9	F	12	1	t
f03fd26e-b997-4259-a44d-ebca99949bd4	715df074-412b-441b-b93e-0dfa4f6ee8f9	G	1	1	t
88bcb81d-da61-4c66-9410-4e48b30c18ac	715df074-412b-441b-b93e-0dfa4f6ee8f9	G	2	1	t
383b71a1-b1ad-44b0-9a5b-a16a266a2e2d	715df074-412b-441b-b93e-0dfa4f6ee8f9	G	3	1	t
76c5dc60-2199-48c3-b7ff-e3c9e5c2fd3f	715df074-412b-441b-b93e-0dfa4f6ee8f9	G	4	1	t
8240dfa1-fd4e-4d02-b331-add3530fe8df	715df074-412b-441b-b93e-0dfa4f6ee8f9	G	5	1	t
b41ba050-2d66-440f-a515-f4a4bf565616	715df074-412b-441b-b93e-0dfa4f6ee8f9	G	6	1	t
8d2c32fa-824b-49d2-9c3e-e7b6a26d4a8c	715df074-412b-441b-b93e-0dfa4f6ee8f9	G	7	1	t
00672400-e9b1-46a4-b77e-b4b04f259f00	715df074-412b-441b-b93e-0dfa4f6ee8f9	G	8	1	t
c0957bf6-9861-451e-95cc-38eb83440cd0	715df074-412b-441b-b93e-0dfa4f6ee8f9	G	9	1	t
2415b542-098d-4341-a1f5-34ba0f9f23bf	715df074-412b-441b-b93e-0dfa4f6ee8f9	G	10	1	t
4a0b1fe7-6bec-487f-80de-14c87834c4b4	715df074-412b-441b-b93e-0dfa4f6ee8f9	G	11	1	t
6d8868e0-f3e2-40e4-9675-a28ada064eeb	715df074-412b-441b-b93e-0dfa4f6ee8f9	G	12	1	t
61dd5faa-5788-4c57-916c-49ca744563b1	715df074-412b-441b-b93e-0dfa4f6ee8f9	H	1	1	t
33e26866-a5e8-4ba9-8985-37378e2764b5	715df074-412b-441b-b93e-0dfa4f6ee8f9	H	4	1	t
c427ab7c-eb56-4997-8de3-46175428501e	715df074-412b-441b-b93e-0dfa4f6ee8f9	H	5	1	t
787f43ac-62b6-4498-89fb-2684d9a89c20	715df074-412b-441b-b93e-0dfa4f6ee8f9	H	8	1	t
afa85580-cc14-41c3-a268-6a14f2a563c7	715df074-412b-441b-b93e-0dfa4f6ee8f9	H	9	1	t
13c3d54f-f0ed-435a-b34d-4747fba88b70	715df074-412b-441b-b93e-0dfa4f6ee8f9	H	12	1	t
07558836-bbad-40a2-93d3-2e855e0b8108	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	A	1	1	t
23644b33-cc61-4fbf-8116-5e08e06f71ff	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	A	2	1	t
b911de91-ef3d-4e5d-8252-eed3ee06d87e	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	A	3	1	t
98a01cd0-7fff-4afe-8482-a735095df802	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	A	4	1	t
ab47de8f-b406-4a09-817a-31affc2c697c	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	A	5	1	t
1c92a6a4-c226-4ca2-a08c-b0d7707b502b	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	A	6	1	t
03798c6d-a206-4bb3-beec-a762d81ee7d9	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	A	7	1	t
e0d08417-1cd8-4520-b703-c49c8f11a078	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	A	8	1	t
24942732-c925-4d8b-8dad-5e85459a3c1d	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	A	9	1	t
aa776a9b-778b-4a48-8d99-9aa320f581be	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	A	10	1	t
aa5e7939-3e0f-4907-8663-979262dd249c	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	A	11	1	t
008b2396-2ce9-4a5d-9db3-92132c9a588c	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	B	1	1	t
785cc1c6-c143-4a74-9a27-b7ef42ffca12	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	B	2	1	t
201535e3-c43f-4df5-af99-32332dc86c8e	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	B	3	1	t
b8946314-44bd-43d1-82d0-5759ae5ebaaa	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	B	4	1	t
0d813206-65c6-422f-8c4e-aa771b243c67	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	B	5	1	t
d3710c1f-5d30-44c2-8422-597762864f40	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	B	6	1	t
d9bae30b-2f2b-4b9d-a830-5ead60337f66	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	B	7	1	t
239b8598-113b-4aa1-b903-3b67bf2512b9	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	B	8	1	t
cecf2a9b-df96-4759-8a5f-4c6cc4ee22c8	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	B	9	1	t
233a0806-4ef5-40b4-a331-c1de4bf1dc48	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	B	10	1	t
3b7908b1-4d20-40a1-a307-827a0d99b07f	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	B	11	1	t
6a098088-2208-461f-bc65-00d884e93b36	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	C	1	1	t
0d0a68b7-e761-436d-adc6-8a729970030a	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	C	2	1	t
16aa12cd-8df1-416e-b425-b83d596fbe81	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	C	3	1	t
ef2b73bd-73fa-4e7f-8c31-0b4d9a7065e3	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	C	4	1	t
789bbbf4-3e9d-49b4-867a-cca744fff803	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	C	5	1	t
c08ebe38-9e39-4550-9375-af4ebb5d2a16	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	C	6	1	t
926f9f71-31f2-4c54-8a07-82e9f77c1165	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	C	7	1	t
ee38bfb6-3505-470f-84bb-6a8b4ed98e06	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	C	8	1	t
86262afa-8c67-490a-86ed-99cd2b865382	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	C	9	1	t
8b6ec5b3-b15b-43cb-b60c-80d75773f684	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	C	10	1	t
5b4b5bcd-febf-46ca-b156-93add89309a2	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	C	11	1	t
5bb797b2-efa7-4197-a084-d5b5a90e33b0	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	D	1	1	t
0903491f-a40b-49c6-b2c4-2d3b6bfdf1e1	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	D	2	1	t
240829a1-1ce1-4359-886d-bfef252debe4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	D	3	1	t
51acfe33-0fda-4c7b-83c3-4dca49f62358	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	D	4	1	t
ecca99f2-b1cf-49f3-969e-e7a37bd711e7	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	D	5	1	t
e1d0a588-8bfb-4d3d-b1bb-8340778c3f28	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	D	6	1	t
a65e9aa1-4f04-42c2-ad51-b5b1db247bec	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	D	7	1	t
968f2430-0fa0-43ea-a712-af958c75d501	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	D	8	1	t
1d43b6d4-f3b1-4a4b-a724-a452d7685272	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	D	9	1	t
3548e92f-1451-4596-af68-433f09b0c1f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	D	10	1	t
cf90d201-c8f2-4279-a3fe-cba91c024098	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	D	11	1	t
39ffdf75-840c-4a24-bf09-a4ba078a20a3	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	E	1	1	t
36209a80-606e-4d15-9fa1-1f3069f93d1f	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	E	2	1	t
ff7da95b-2d9b-4f16-a3a4-00535c8e2036	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	E	3	1	t
b9055eeb-c011-4400-a05b-f45010295b27	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	E	4	1	t
1dd1785a-86dc-45a4-b8fe-709dc9c0de9a	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	E	5	1	t
3f2c1dd0-bffe-4cc5-aa35-79dfbb520b2a	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	E	6	1	t
0e5fb587-af38-447e-89e5-20cc1596b407	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	E	7	1	t
e805187f-5721-4e31-ad6a-b4c94f229210	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	E	8	1	t
56186046-e11f-4976-9775-7ddb3b8abe0c	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	E	9	1	t
924805b3-045a-4cf3-82c1-a084bdff62c1	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	E	10	1	t
53ab19aa-7d8a-428a-9fae-9c2c1ab0e941	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	E	11	1	t
345b493e-c043-4f02-aea0-c7de7b64c47e	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	F	1	1	t
82edc30c-7a27-49ff-badf-aa498418d081	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	F	2	1	t
00657102-336d-4486-ac4b-9d3890856d3e	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	F	3	1	t
540593bc-1e6a-4517-94e7-c686ceb6affa	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	F	4	1	t
58e0b99e-5f15-43d9-b42a-0dc8c1d0829e	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	F	5	1	t
d512cc97-5491-4cf2-b134-29a39637cabe	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	F	6	1	t
d5243cb0-9ec8-4372-ae2d-14232411b5f7	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	F	7	1	t
d8f4a3f4-bd56-44a1-8674-b7350af8d262	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	F	8	1	t
0daa868c-89ce-42e9-85a9-7118c59904b3	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	F	9	1	t
bc648a79-d3c2-4a3c-ac7d-489e6344a31c	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	F	10	1	t
dd7e7f9b-64dd-45b4-b7cc-937a5f37cc17	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	F	11	1	t
da76f530-c86c-4a33-a76f-24ae193c0201	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	G	1	1	t
360c76ac-ea2f-4539-8367-0d343b67a9ed	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	G	2	1	t
1ff2ce40-d920-4035-8aaa-87fe4f61f7f0	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	G	3	1	t
8f73cc81-0297-4c58-828f-10fc3dd45023	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	G	4	1	t
c37fb847-3d12-40b5-814c-c807e718f599	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	G	5	1	t
f4bb689a-ad5c-4153-9241-393bdac08e82	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	G	6	1	t
29a1f4f1-31a8-400d-a499-d2b8fd3637c0	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	G	7	1	t
ab5326a2-ef3a-4d23-b66c-6f16ab735ad3	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	G	8	1	t
d3eec914-d286-484e-9321-d4faf0e2006d	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	G	9	1	t
2277c2e9-21f3-4f5d-956b-19fb3ea440d1	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	G	10	1	t
6fca218a-665a-4c4f-b45c-4f1aeee92842	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	G	11	1	t
4b722838-14a8-491f-b518-a8d925be0968	715df074-412b-441b-b93e-0dfa4f6ee8f9	H	6	3	t
60f6752c-847e-411f-b5e0-ddd77d133f47	715df074-412b-441b-b93e-0dfa4f6ee8f9	H	7	3	t
89abd254-d5ac-44ef-965a-6e871ce30051	715df074-412b-441b-b93e-0dfa4f6ee8f9	H	11	3	t
a7212033-b721-48a5-aa7f-4899dbbc4e85	715df074-412b-441b-b93e-0dfa4f6ee8f9	H	2	3	t
d266b7e8-35f2-4647-96ac-e4264618f545	715df074-412b-441b-b93e-0dfa4f6ee8f9	H	3	3	t
e1c7631b-031b-41f8-8768-f4f31bcb2d1d	715df074-412b-441b-b93e-0dfa4f6ee8f9	H	10	3	t
\.


--
-- Data for Name: showtimes; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.showtimes (id, movie_id, auditorium_id, starts_at, ends_at, status, base_price, created_by, created_at, booking_closes_at, cancellation_reason) FROM stdin;
b3e5cd8c-942a-4d25-8da2-a419d05f8b5f	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-07-28 12:00:00+00	2026-07-28 13:30:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-28 11:48:10.733516+00	2026-07-28 11:45:00+00	\N
4fb38083-0ca0-4c3c-8467-71f1bbc6947a	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-07-30 05:15:00+00	2026-07-30 07:36:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-28 12:02:17.826316+00	2026-07-30 05:00:00+00	\N
1a56fe45-24aa-4eaf-8e87-b66bce04b72e	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-03 05:08:00+00	2026-08-03 07:29:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-03 04:53:00+00	\N
2745ccdd-b914-4e8e-8f4d-2bfd9cbb2e18	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-02 02:00:00+00	2026-08-02 04:21:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-02 01:45:00+00	\N
2a20eed4-aa19-43a5-9fca-ffddfa6b4102	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-07-31 04:36:00+00	2026-07-31 07:29:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-07-31 04:21:00+00	\N
3f02c84f-00ac-4c35-9ac6-244bf1700c2e	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-02 07:44:00+00	2026-08-02 10:05:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-02 07:29:00+00	\N
3ff192ef-99c9-4a8f-8bb6-15c46d8dcc4f	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-04 02:00:00+00	2026-08-04 04:21:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-04 01:45:00+00	\N
4321b8d3-113a-466c-ac52-c731a2139a88	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-07-31 02:00:00+00	2026-07-31 04:21:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-07-31 01:45:00+00	\N
4727c2f9-7862-4655-902a-01cb760aeded	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-07-31 07:44:00+00	2026-07-31 10:05:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-07-31 07:29:00+00	\N
48f5ac3a-a1dd-4807-9224-c6e7a5b11edd	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-07 05:08:00+00	2026-08-07 07:29:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-07 04:53:00+00	\N
5843102d-f54a-48fb-84a3-179b7faee1ff	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-01 07:44:00+00	2026-08-01 10:37:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-01 07:29:00+00	\N
5a71fd06-07be-422a-abac-a322a0b15106	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-01 02:00:00+00	2026-08-01 04:53:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-01 01:45:00+00	\N
5f8777d0-5cfe-444e-bcf8-94c9a51f3858	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-07 07:44:00+00	2026-08-07 10:37:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-07 07:29:00+00	\N
715fbc9c-f587-45d4-994b-7cb599c874ec	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-05 02:00:00+00	2026-08-05 04:53:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-05 01:45:00+00	\N
78367ae2-6a03-439f-8732-5a61f81e00f1	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-04 04:36:00+00	2026-08-04 07:29:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-04 04:21:00+00	\N
7b6246ff-d8b8-4e19-9de1-1376409f6e50	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-06 02:00:00+00	2026-08-06 04:21:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-06 01:45:00+00	\N
7bf4158d-e8c7-41f1-a578-9e494504eca5	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-05 07:44:00+00	2026-08-05 10:37:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-05 07:29:00+00	\N
9f4ad855-27c7-4c1e-96a6-278332060a39	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-05 05:08:00+00	2026-08-05 07:29:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-05 04:53:00+00	\N
a5003ddc-ad21-410c-a966-5be2cb2bc8ae	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-03 02:00:00+00	2026-08-03 04:53:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-03 01:45:00+00	\N
a59a1bba-c013-4e24-9ef7-39a445c10708	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-03 07:44:00+00	2026-08-03 10:37:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-03 07:29:00+00	\N
b9eba26c-bd05-490f-8f19-cae63678b674	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-04 07:44:00+00	2026-08-04 10:05:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-04 07:29:00+00	\N
c811184a-a868-427d-8390-bf09e5e3c639	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-01 05:08:00+00	2026-08-01 07:29:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-01 04:53:00+00	\N
cc1d0ca9-9e76-4faa-aec4-b4fdb8771cce	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-06 04:36:00+00	2026-08-06 07:29:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-06 04:21:00+00	\N
e8b0b1d3-5b85-43dd-96bb-9f649e78bedc	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-06 07:44:00+00	2026-08-06 10:05:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-06 07:29:00+00	\N
e94eeec0-a6de-4692-9a60-9b28eeab841c	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-02 04:36:00+00	2026-08-02 07:29:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-02 04:21:00+00	\N
ffcf37d0-d7ea-4ff7-a20e-68a4e91eeef5	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-07 02:00:00+00	2026-08-07 04:53:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-07-30 13:44:29.381289+00	2026-08-07 01:45:00+00	\N
0d0cc1ba-2845-49f3-bb65-a27526ffc6a9	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-28 07:53:00+00	2026-08-28 10:14:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-28 07:38:00+00	\N
1319d05f-17b2-49e4-a844-741826df9191	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-28 13:14:00+00	2026-08-28 16:07:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-28 12:59:00+00	\N
2d9ad755-ab4a-4f6c-a98a-0c90a053f0a0	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-24 10:29:00+00	2026-08-24 12:50:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-24 10:14:00+00	\N
301fd893-d3e9-4496-82f3-0322f16645b3	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-28 02:00:00+00	2026-08-28 04:30:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-28 01:45:00+00	\N
33f96a3d-bf4f-4b9e-af08-77e55c79a2f5	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-29 13:37:00+00	2026-08-29 15:58:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-29 13:22:00+00	\N
3d82ab46-1867-4e25-ad89-a577f17653d1	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-27 02:00:00+00	2026-08-27 04:21:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-27 01:45:00+00	\N
44a30b68-df4d-4788-b161-349540a2e48f	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-25 04:45:00+00	2026-08-25 07:38:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-25 04:30:00+00	\N
49e77ef3-c270-4093-b225-05ddb401f7a7	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-28 10:29:00+00	2026-08-28 12:59:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-28 10:14:00+00	\N
519e85bb-08ba-42e1-934b-1e3f7afbce11	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-26 10:29:00+00	2026-08-26 13:22:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-26 10:14:00+00	\N
54a5ef72-0dc3-41f2-a804-b88f9ecaeb89	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-25 13:14:00+00	2026-08-25 16:07:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-25 12:59:00+00	\N
57d9b685-5540-420c-bc60-6ff9228e6b98	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-25 10:29:00+00	2026-08-25 12:59:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-25 10:14:00+00	\N
725221ca-2bc7-4f83-b161-29c3a22aaaf1	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-27 04:36:00+00	2026-08-27 07:06:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-27 04:21:00+00	\N
7b96b9b7-2709-47eb-86b8-ef0cb215e47e	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-27 10:29:00+00	2026-08-27 12:50:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-27 10:14:00+00	\N
7edc0c90-e3c2-4ba7-bfee-bdace5b5217e	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-29 07:44:00+00	2026-08-29 10:14:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-29 07:29:00+00	\N
8ec74c46-ad6e-468c-a7ac-8a08ee937964	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-26 07:44:00+00	2026-08-26 10:14:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-26 07:29:00+00	\N
8fea6623-f98d-4fff-be10-52eb5b581e70	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-29 02:00:00+00	2026-08-29 04:53:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-29 01:45:00+00	\N
97d6fca8-9164-4941-8d2d-bf79ef7dedbc	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-26 02:00:00+00	2026-08-26 04:53:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-26 01:45:00+00	\N
981d795c-0e66-4f7c-8962-b5dfa5674162	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-28 04:45:00+00	2026-08-28 07:38:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-28 04:30:00+00	\N
b8e4927b-3168-4d32-a43b-0458d1bd3f93	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-29 10:29:00+00	2026-08-29 13:22:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-29 10:14:00+00	\N
cf9ff6f4-103d-4843-80a5-4857358b09ce	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-26 05:08:00+00	2026-08-26 07:29:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-26 04:53:00+00	\N
d1e6b08e-4671-4b55-ba95-f7b26c276e11	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-25 02:00:00+00	2026-08-25 04:30:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-25 01:45:00+00	\N
d4524395-f4a6-4e30-82b5-b19df15765b5	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-27 07:21:00+00	2026-08-27 10:14:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-27 07:06:00+00	\N
d4809d4b-97ff-44a9-9c7f-46b7f2eaa042	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-29 05:08:00+00	2026-08-29 07:29:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-29 04:53:00+00	\N
da160c45-f6ff-4a0f-b598-d2faed709fdb	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-24 13:05:00+00	2026-08-24 15:35:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-24 12:50:00+00	\N
e302e58f-c7b8-446b-aa35-af5e45f7be35	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-25 07:53:00+00	2026-08-25 10:14:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-25 07:38:00+00	\N
eb089993-bfa9-41e2-b719-9bbdab244ff4	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-27 13:05:00+00	2026-08-27 15:35:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-27 12:50:00+00	\N
f6eb577e-80cf-46ca-87eb-ad4920b4899a	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-26 13:37:00+00	2026-08-26 15:58:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-26 13:22:00+00	\N
06927e19-75d9-4f77-b4f8-841e63077f07	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-23 10:29:00+00	2026-08-23 13:22:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-23 10:14:00+00	\N
0afa917d-c7d3-414e-8e10-b12cc85813eb	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-20 02:00:00+00	2026-08-20 04:53:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-20 01:45:00+00	\N
0d76a9a1-7146-48d9-9f46-9a5db8945eca	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-22 07:53:00+00	2026-08-22 10:14:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-22 07:38:00+00	\N
0e474381-9d31-413e-ac5c-38b04fcc8269	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-21 07:21:00+00	2026-08-21 10:14:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-21 07:06:00+00	\N
19a3d0a2-4312-430c-ae58-1725e0bc7388	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-10 02:00:00+00	2026-08-10 04:30:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-10 01:45:00+00	\N
1b55d521-5a93-459c-a2d4-ed589d73488e	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-18 02:00:00+00	2026-08-18 04:21:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-18 01:45:00+00	\N
1b9d9aef-0a7b-4da4-a82c-71dba499e4f4	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-09 04:36:00+00	2026-08-09 07:06:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-09 04:21:00+00	\N
1c2303da-4cce-4609-b89d-0da4ba63ed44	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-23 02:00:00+00	2026-08-23 04:53:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-23 01:45:00+00	\N
1fc1690d-b0da-4e4c-9296-eec9caa79914	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-24 04:36:00+00	2026-08-24 07:06:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-24 04:21:00+00	\N
20739947-9059-4e3e-b722-f9dd0e013711	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-24 02:00:00+00	2026-08-24 04:21:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-24 01:45:00+00	\N
2274739b-8a63-497b-9959-5c7a95e5c155	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-14 02:00:00+00	2026-08-14 04:53:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-14 01:45:00+00	\N
2526adc1-af42-4a87-b4dd-53103f802dab	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-11 07:44:00+00	2026-08-11 10:14:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-11 07:29:00+00	\N
271bab4f-0ca3-4a87-a91b-94384ade7ab4	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-11 02:00:00+00	2026-08-11 04:53:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-11 01:45:00+00	\N
2f6b37c9-8046-498a-babb-1c62203c09b6	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-10 04:45:00+00	2026-08-10 07:38:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-10 04:30:00+00	\N
32a058e1-7b1c-4c6f-9425-038c99c7bd57	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-19 07:53:00+00	2026-08-19 10:14:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-19 07:38:00+00	\N
32df86b7-4156-4a61-a55f-a786bf55329d	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-13 13:14:00+00	2026-08-13 16:07:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-13 12:59:00+00	\N
3691441b-c498-424e-9248-58741ffbf75f	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-08 10:29:00+00	2026-08-08 13:22:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-08 10:14:00+00	\N
371d7979-31e0-42a0-83fe-c5990c54bc7a	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-12 07:21:00+00	2026-08-12 10:14:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-12 07:06:00+00	\N
3925a7b9-bd87-44ff-8c67-f4038b1fb1fe	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-22 13:14:00+00	2026-08-22 16:07:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-22 12:59:00+00	\N
3ae217d3-dab1-4b4c-8ffb-e94c5f2125f1	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-21 10:29:00+00	2026-08-21 12:50:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-21 10:14:00+00	\N
3e99fdad-02eb-4481-a387-e62229fd36f4	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-09 02:00:00+00	2026-08-09 04:21:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-09 01:45:00+00	\N
3f7f4214-cd34-4e7f-b8fc-9295532599f6	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-10 10:29:00+00	2026-08-10 12:59:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-10 10:14:00+00	\N
40cdb191-faf3-4ca3-8e40-d267a1128444	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-18 07:21:00+00	2026-08-18 10:14:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-18 07:06:00+00	\N
42798e98-5f74-4894-8594-273e07a4832c	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-19 10:29:00+00	2026-08-19 12:59:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-19 10:14:00+00	\N
4e7e314b-0739-4125-9138-04c136c0f848	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-21 04:36:00+00	2026-08-21 07:06:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-21 04:21:00+00	\N
4ed28941-dae7-418f-ab1a-57c6defad110	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-19 13:14:00+00	2026-08-19 16:07:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-19 12:59:00+00	\N
57452913-ff8a-4603-b667-3231d5ed20af	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-19 04:45:00+00	2026-08-19 07:38:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-19 04:30:00+00	\N
5af91cfb-cb74-4312-af74-005015374415	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-08 05:08:00+00	2026-08-08 07:29:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-08 04:53:00+00	\N
5f34beec-c1b6-422f-8515-7f81452cc624	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-13 04:45:00+00	2026-08-13 07:38:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-13 04:30:00+00	\N
5fd0815f-2e2b-4797-b966-1a00d03ab89d	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-14 07:44:00+00	2026-08-14 10:14:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-14 07:29:00+00	\N
60eabc91-322b-4e75-90dc-fbca278d866e	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-17 10:29:00+00	2026-08-17 13:22:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-17 10:14:00+00	\N
61ae09e3-d131-4f82-87f5-f203705ecf90	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-11 05:08:00+00	2026-08-11 07:29:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-11 04:53:00+00	\N
64e7536d-b1f1-40e0-8019-15ac5aae3f37	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-23 05:08:00+00	2026-08-23 07:29:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-23 04:53:00+00	\N
6874cfda-64ee-4bee-945e-72ad778d5bc6	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-20 13:37:00+00	2026-08-20 15:58:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-20 13:22:00+00	\N
6c7ad801-392b-452b-bfc4-bdc5d93ab57c	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-14 05:08:00+00	2026-08-14 07:29:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-14 04:53:00+00	\N
72923397-ca78-4fa8-b2d5-34b83a176e5c	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-12 02:00:00+00	2026-08-12 04:21:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-12 01:45:00+00	\N
7974292a-9f7d-4fde-a6a2-e36202c55260	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-15 02:00:00+00	2026-08-15 04:21:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-15 01:45:00+00	\N
7ae5a263-89dd-4001-bca3-c20d5c82e06b	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-08 02:00:00+00	2026-08-08 04:53:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-08 01:45:00+00	\N
7b92189b-f9eb-44a9-a0aa-13807057d344	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-17 05:08:00+00	2026-08-17 07:29:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-17 04:53:00+00	\N
80f1fd30-845d-45c1-be88-2bb15d9a2599	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-09 07:21:00+00	2026-08-09 10:14:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-09 07:06:00+00	\N
854921b4-85cb-4e1b-bc28-8e51ada0ba8c	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-20 10:29:00+00	2026-08-20 13:22:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-20 10:14:00+00	\N
89765cfb-0eed-4e8e-9891-19dde3726b19	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-12 10:29:00+00	2026-08-12 12:50:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-12 10:14:00+00	\N
89a88e01-7c33-48be-b74e-185318851998	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-22 10:29:00+00	2026-08-22 12:59:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-22 10:14:00+00	\N
89c85a62-9a94-4865-854a-e67bb88cb691	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-09 13:05:00+00	2026-08-09 15:35:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-09 12:50:00+00	\N
90c74df6-6cba-4aca-9b47-dc4f5689bd8a	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-14 13:37:00+00	2026-08-14 15:58:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-14 13:22:00+00	\N
918dc5f0-33f4-4c37-94ce-a9bad7e1f79f	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-16 07:53:00+00	2026-08-16 10:14:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-16 07:38:00+00	\N
928c6e35-4211-46bf-a2d8-c834e850ef5c	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-14 10:29:00+00	2026-08-14 13:22:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-14 10:14:00+00	\N
93491e1e-5995-42e1-93f5-1ef2a859c1eb	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-13 02:00:00+00	2026-08-13 04:30:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-13 01:45:00+00	\N
944e5810-8cbc-457d-a60a-ec2017031770	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-12 04:36:00+00	2026-08-12 07:06:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-12 04:21:00+00	\N
97fe559e-a0d2-418a-a04d-430965ad26d1	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-19 02:00:00+00	2026-08-19 04:30:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-19 01:45:00+00	\N
987389d1-5b1d-4a5f-9cc4-900e5065f3ed	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-18 13:05:00+00	2026-08-18 15:35:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-18 12:50:00+00	\N
99050776-a261-494b-ad79-754059a1a9a6	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-11 10:29:00+00	2026-08-11 13:22:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-11 10:14:00+00	\N
a0491d18-9120-4e6a-a9fe-cf080ee04237	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-12 13:05:00+00	2026-08-12 15:35:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-12 12:50:00+00	\N
a0e6c73f-0ffe-4bb0-85b7-ee4ee2c47d85	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-08 13:37:00+00	2026-08-08 15:58:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-08 13:22:00+00	\N
a23a3510-0b4b-442d-890a-cd0f91b0bd5e	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-21 13:05:00+00	2026-08-21 15:35:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-21 12:50:00+00	\N
a2764ab9-4701-48b7-858a-b0be9c819d23	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-17 07:44:00+00	2026-08-17 10:14:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-17 07:29:00+00	\N
a8832e07-623a-4dc9-8bfc-f49dd02c1e17	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-16 13:14:00+00	2026-08-16 16:07:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-16 12:59:00+00	\N
a920fd78-865b-47fd-8c53-74314e3b3303	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-16 04:45:00+00	2026-08-16 07:38:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-16 04:30:00+00	\N
a9ce18f2-0cbf-493f-b5bd-2fa88acb8567	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-10 13:14:00+00	2026-08-10 16:07:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-10 12:59:00+00	\N
ab06927c-77e3-4cc7-8108-cb8789e5c5e7	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-10 07:53:00+00	2026-08-10 10:14:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-10 07:38:00+00	\N
b4b696ea-0181-48bb-9ec7-92986ce5dd74	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-09 10:29:00+00	2026-08-09 12:50:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-09 10:14:00+00	\N
b568a0eb-b16e-4b10-847a-48de64ad0796	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-15 13:05:00+00	2026-08-15 15:35:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-15 12:50:00+00	\N
b81750fa-79c1-4b84-92a0-bb23bf542482	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-15 07:21:00+00	2026-08-15 10:14:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-15 07:06:00+00	\N
b84d63eb-361c-4c20-af01-768e11d69d71	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-17 02:00:00+00	2026-08-17 04:53:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-17 01:45:00+00	\N
b9a3e6ed-9810-4254-8bdd-cd5413e5d002	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-13 07:53:00+00	2026-08-13 10:14:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-13 07:38:00+00	\N
ba6c9b9e-f2dc-42b1-bfe4-81682e8e6151	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-21 02:00:00+00	2026-08-21 04:21:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-21 01:45:00+00	\N
bc34b071-98cf-4602-8b3f-29c42937cdb7	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-18 04:36:00+00	2026-08-18 07:06:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-18 04:21:00+00	\N
bc517e46-993b-492e-ad1a-5ae9aecd371e	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-11 13:37:00+00	2026-08-11 15:58:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-11 13:22:00+00	\N
c12682ce-e7d8-4256-b5f3-10d17ee7a3c4	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-22 04:45:00+00	2026-08-22 07:38:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-22 04:30:00+00	\N
cb6ad6d7-6b28-425b-ab2f-1dbda75c490a	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-13 10:29:00+00	2026-08-13 12:59:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-13 10:14:00+00	\N
cdc84922-bc1e-411e-a94a-5588a7b7b724	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-15 10:29:00+00	2026-08-15 12:50:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-15 10:14:00+00	\N
014c1386-a9f7-413b-9343-710e15146107	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-15 09:48:00+00	2026-08-15 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-15 09:33:00+00	\N
02748188-4927-4f4b-97df-f559107b6dbf	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-11 12:06:00+00	2026-08-11 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-11 11:51:00+00	\N
03e6bac8-e502-46d5-a1be-63fd8f8b94a8	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-15 04:18:00+00	2026-08-15 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-15 04:03:00+00	\N
04f3e666-4216-45b0-8d87-a5633fc8aa67	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-21 12:06:00+00	2026-08-21 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-21 11:51:00+00	\N
05487d0f-103a-4f17-92d2-126edb838b0f	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-16 02:00:00+00	2026-08-16 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-16 01:45:00+00	\N
061d7596-1ad4-45a5-a1e1-e2230d8f56aa	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-25 02:00:00+00	2026-08-25 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-25 01:45:00+00	\N
0643e227-ad0c-4f74-91ec-c588f1eb6bb8	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-22 12:06:00+00	2026-08-22 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-22 11:51:00+00	\N
06f320fd-4132-4c92-a3b0-b87c1ddafce9	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-20 09:21:00+00	2026-08-20 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-20 09:06:00+00	\N
074e8936-f1c2-4e42-a9f1-e7ae29287c86	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-17 09:21:00+00	2026-08-17 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-17 09:06:00+00	\N
077948d7-40e5-4377-b224-d477fb3311c1	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-23 04:18:00+00	2026-08-23 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-23 04:03:00+00	\N
096c0192-8448-44aa-a2a5-8873667e8030	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-19 04:45:00+00	2026-08-19 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-19 04:30:00+00	\N
0973b3b9-7421-46b0-b71a-f5a8b5bd8115	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-19 07:03:00+00	2026-08-19 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-19 06:48:00+00	\N
0a1b67e1-19e8-40fd-830d-22b8c3bcb0fd	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-23 07:03:00+00	2026-08-23 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-23 06:48:00+00	\N
0aa29023-0b8d-4bdd-8b0f-ec030ec72823	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-10 09:21:00+00	2026-08-10 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-10 09:06:00+00	\N
106ad20d-6eff-46e7-879a-a8f386f7fb0d	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-11 04:18:00+00	2026-08-11 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-11 04:03:00+00	\N
13f27a65-30e5-46d9-ba1d-45a56218b292	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-15 02:00:00+00	2026-08-15 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-15 01:45:00+00	\N
16fc69f7-bf30-451e-9591-6987d7a3c896	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-20 02:00:00+00	2026-08-20 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-20 01:45:00+00	\N
193837b2-c48d-49a4-b8d0-a2c48153d978	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-20 09:48:00+00	2026-08-20 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-20 09:33:00+00	\N
19a1a0e4-af9e-4c6f-a82c-a2c75ecaef94	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-13 09:21:00+00	2026-08-13 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-13 09:06:00+00	\N
1b4a340b-1192-4cd9-8fef-a91239095ca3	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-08 04:18:00+00	2026-08-08 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-08 04:03:00+00	\N
1e331c89-059e-46d7-b15c-d5a844ca32b2	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-10 04:18:00+00	2026-08-10 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-10 04:03:00+00	\N
1ee8e02f-dd37-4fb9-8604-5c0b4ba4daf1	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-21 09:21:00+00	2026-08-21 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-21 09:06:00+00	\N
1fbb719e-742f-42e5-ae9c-03b08f8f1924	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-18 09:21:00+00	2026-08-18 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-18 09:06:00+00	\N
20a3a5f0-a05f-417d-af1f-7435c9570dc6	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-17 12:06:00+00	2026-08-17 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-17 11:51:00+00	\N
21dbca30-f749-459d-a8a6-0583fb197b75	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-20 02:00:00+00	2026-08-20 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-20 01:45:00+00	\N
22c70c1a-5a1b-4663-89a0-891c2ec4d3de	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-19 02:00:00+00	2026-08-19 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-19 01:45:00+00	\N
22cc9881-633a-4759-ac14-c47f50ff1701	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-24 07:03:00+00	2026-08-24 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-24 06:48:00+00	\N
256e50df-2c9d-489f-88aa-5274256d7c00	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-28 09:48:00+00	2026-08-28 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-28 09:33:00+00	\N
25efdf65-1956-43e0-acaa-2fe60f699ccb	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-17 07:03:00+00	2026-08-17 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-17 06:48:00+00	\N
2632b8e8-f5b3-4686-b6bc-0a0edb37f9de	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-22 12:06:00+00	2026-08-22 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-22 11:51:00+00	\N
28111e0e-f3e6-4113-9e1e-3dba7f4b4bb1	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-14 02:00:00+00	2026-08-14 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-14 01:45:00+00	\N
2a3df96e-23c8-47ec-b5dd-bee7fd14ae5a	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-23 12:06:00+00	2026-08-23 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-23 11:51:00+00	\N
2a4d934e-c561-4ecd-b55c-cedc45db895d	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-18 02:00:00+00	2026-08-18 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-18 01:45:00+00	\N
2ad692e9-536a-4a3a-8a50-2c446c7cc721	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-14 12:06:00+00	2026-08-14 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-14 11:51:00+00	\N
2bfbf1f5-890a-4e15-aca9-6d1bc71fd27e	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-10 02:00:00+00	2026-08-10 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-10 01:45:00+00	\N
2cb34bae-c6ff-4b2e-b9d1-c0678180b63d	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-26 09:21:00+00	2026-08-26 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-26 09:06:00+00	\N
3348e718-c4a7-4080-ac1b-b47a7f33c531	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-21 12:06:00+00	2026-08-21 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-21 11:51:00+00	\N
33887481-71e8-4cae-820a-0afa6f5c3f24	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-18 07:03:00+00	2026-08-18 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-18 06:48:00+00	\N
ce5c24a3-eb8f-4c35-931b-1a698f353450	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-20 07:44:00+00	2026-08-20 10:14:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-20 07:29:00+00	\N
3a333a50-3ab1-41da-b3b1-4c14692c62d0	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-20 07:03:00+00	2026-08-20 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-20 06:48:00+00	\N
3b72d759-dcd1-4a2d-8ce4-f197ab9b045f	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-10 07:03:00+00	2026-08-10 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-10 06:48:00+00	\N
3bb9b5e6-a662-4b9d-80bb-e61822619a12	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-13 04:18:00+00	2026-08-13 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-13 04:03:00+00	\N
3cbc2fd1-fb25-46d5-be65-d522d790c20f	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-27 09:48:00+00	2026-08-27 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-27 09:33:00+00	\N
3fe21af7-0604-43ef-90ee-b97b3d79857f	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-08 12:06:00+00	2026-08-08 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-08 11:51:00+00	\N
4057a850-e3a6-4805-a79c-62b97d943277	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-08 12:06:00+00	2026-08-08 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-08 11:51:00+00	\N
40a6741f-84f0-4eeb-bf38-5ed425b91482	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-24 02:00:00+00	2026-08-24 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-24 01:45:00+00	\N
425fe5fb-5aa4-414a-a39c-033d5c902449	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-13 02:00:00+00	2026-08-13 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-13 01:45:00+00	\N
43fb839d-21ef-433d-969b-87a86d87edc3	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-15 12:06:00+00	2026-08-15 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-15 11:51:00+00	\N
4486b609-35d0-460b-b896-74fa0491b72f	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-28 02:00:00+00	2026-08-28 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-28 01:45:00+00	\N
46670c8d-ac0f-40f4-b34d-286fc0add462	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-12 07:03:00+00	2026-08-12 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-12 06:48:00+00	\N
46c860ef-bd16-4b33-bbad-4d789aac2946	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-17 12:06:00+00	2026-08-17 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-17 11:51:00+00	\N
48509a41-4c0b-45f1-97e0-db78ebb53e0b	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-14 02:00:00+00	2026-08-14 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-14 01:45:00+00	\N
4a7dcdaa-d4fd-401f-8733-863466887f0b	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-26 12:06:00+00	2026-08-26 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-26 11:51:00+00	\N
4b645eef-5f4b-4dbc-b5ab-6a8f7aac9f38	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-28 07:03:00+00	2026-08-28 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-28 06:48:00+00	\N
4c41696b-5589-49d7-9004-8bdb8a3f2845	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-16 07:03:00+00	2026-08-16 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-16 06:48:00+00	\N
4e2a505c-2c7b-4b47-b8b5-43b4b9499cfb	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-19 04:18:00+00	2026-08-19 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-19 04:03:00+00	\N
4e4ff917-6478-4f3f-92ac-1e479ad596bf	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-22 04:45:00+00	2026-08-22 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-22 04:30:00+00	\N
4f6cd8f7-795a-49cb-a92d-debccd292b07	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-12 09:48:00+00	2026-08-12 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-12 09:33:00+00	\N
504122fa-ae34-4578-b6ca-5f0a1bb8ad9f	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-27 04:18:00+00	2026-08-27 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-27 04:03:00+00	\N
50f0b408-4dd1-4ee4-ac91-804550aba11d	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-17 02:00:00+00	2026-08-17 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-17 01:45:00+00	\N
52366968-50dc-43d1-9063-6799cf435d81	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-21 02:00:00+00	2026-08-21 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-21 01:45:00+00	\N
53a36e8c-dc2c-4d1b-80da-d6c1001376c5	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-08 07:03:00+00	2026-08-08 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-08 06:48:00+00	\N
55481bcb-3473-4934-b7b7-bbecc0ac58df	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-24 07:03:00+00	2026-08-24 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-24 06:48:00+00	\N
554fd71a-16be-40aa-9fca-1f83dad5951c	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-26 07:03:00+00	2026-08-26 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-26 06:48:00+00	\N
5785ec33-23fc-41b7-b310-aff957b1c53d	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-18 12:06:00+00	2026-08-18 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-18 11:51:00+00	\N
58932828-47c3-4497-a803-65198aee571f	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-24 12:06:00+00	2026-08-24 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-24 11:51:00+00	\N
58e3bc50-d95e-438a-8e97-bcada050dace	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-09 07:03:00+00	2026-08-09 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-09 06:48:00+00	\N
5e3229c4-3fb2-4728-8161-13fef1490c52	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-26 02:00:00+00	2026-08-26 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-26 01:45:00+00	\N
5ea8e598-77d2-41cd-b5f3-4b297e2eef1a	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-26 02:00:00+00	2026-08-26 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-26 01:45:00+00	\N
5ff1794a-e451-45fc-a223-fa4ba1720c35	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-14 04:45:00+00	2026-08-14 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-14 04:30:00+00	\N
61819bbc-8e88-4704-9593-77d41ca046f1	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-14 07:03:00+00	2026-08-14 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-14 06:48:00+00	\N
61862ec7-dde2-46e5-8dc6-56e09425bc11	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-19 07:03:00+00	2026-08-19 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-19 06:48:00+00	\N
637a7886-928b-408c-bf77-0f933dd4bf9c	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-19 12:06:00+00	2026-08-19 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-19 11:51:00+00	\N
63afd3f0-8feb-4872-9b6e-5699ce37a70e	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-10 02:00:00+00	2026-08-10 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-10 01:45:00+00	\N
63fb5639-c278-4094-94f3-8a1ee25ffb01	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-25 12:06:00+00	2026-08-25 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-25 11:51:00+00	\N
65f962db-1147-45cc-94a0-ea99e04c935d	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-25 04:18:00+00	2026-08-25 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-25 04:03:00+00	\N
665d685c-87d1-4f50-9cb3-62f267d48fcc	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-18 04:45:00+00	2026-08-18 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-18 04:30:00+00	\N
668e45e6-8e4a-4a28-ad08-fe73da791e16	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-09 09:21:00+00	2026-08-09 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-09 09:06:00+00	\N
66c4b36f-989f-4505-a44b-3ef95a22b1c4	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-13 04:45:00+00	2026-08-13 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-13 04:30:00+00	\N
67971859-68fd-445c-9c49-6f2406062c62	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-21 07:03:00+00	2026-08-21 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-21 06:48:00+00	\N
6820504a-027d-4846-9dd1-043e49753f02	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-09 12:06:00+00	2026-08-09 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-09 11:51:00+00	\N
697a40e4-665a-4389-a402-825a90b56ae3	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-11 04:45:00+00	2026-08-11 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-11 04:30:00+00	\N
6b352f7e-f19e-40ce-86b1-ca1285c87203	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-25 07:03:00+00	2026-08-25 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-25 06:48:00+00	\N
6b45246d-f112-42a8-ab08-37f58326f172	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-08 04:45:00+00	2026-08-08 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-08 04:30:00+00	\N
6d8bb955-ffc3-4034-90ed-48abcc1b3d65	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-17 07:03:00+00	2026-08-17 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-17 06:48:00+00	\N
72bfd158-6482-48cb-a1a7-5228e547ffb0	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-20 12:06:00+00	2026-08-20 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-20 11:51:00+00	\N
72c226f7-0fd8-4846-a022-415cc14a206c	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-27 04:45:00+00	2026-08-27 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-27 04:30:00+00	\N
74891a7a-6c35-4914-838e-3d1ab10bdc06	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-16 09:21:00+00	2026-08-16 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-16 09:06:00+00	\N
76a4db96-8d7f-4c54-80e9-c9d279b33e49	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-28 12:06:00+00	2026-08-28 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-28 11:51:00+00	\N
77561b1b-fce9-425e-80e4-6232bb8f9b81	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-22 04:18:00+00	2026-08-22 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-22 04:03:00+00	\N
77bc8f59-455d-4af6-b951-f900a78acaca	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-27 12:06:00+00	2026-08-27 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-27 11:51:00+00	\N
7894f85d-1fd4-489e-8d57-d82d2262aa54	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-15 04:45:00+00	2026-08-15 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-15 04:30:00+00	\N
790ae83d-f777-4978-8788-48df5adc3f78	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-23 02:00:00+00	2026-08-23 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-23 01:45:00+00	\N
7aeabd9c-b670-421f-aa6e-e17902c33ca7	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-27 07:03:00+00	2026-08-27 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-27 06:48:00+00	\N
7b5c29d9-0464-447b-a4c2-cf5674644ae0	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-15 12:06:00+00	2026-08-15 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-15 11:51:00+00	\N
7bd52e24-28cf-492a-9b57-4f22070af3ed	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-20 04:18:00+00	2026-08-20 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-20 04:03:00+00	\N
7c69a48e-061e-4553-ab17-d65fb26151f5	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-23 07:03:00+00	2026-08-23 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-23 06:48:00+00	\N
7de902cb-8eec-4daf-ab33-3e2eb622a347	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-12 07:03:00+00	2026-08-12 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-12 06:48:00+00	\N
818fd369-d5a9-4c48-914b-e64a6e600dfe	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-12 02:00:00+00	2026-08-12 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-12 01:45:00+00	\N
82c68551-0437-4cc7-a0ac-96e8cf289582	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-13 12:06:00+00	2026-08-13 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-13 11:51:00+00	\N
8391c27b-cf5b-4611-973c-413bcef1e55b	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-24 12:06:00+00	2026-08-24 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-24 11:51:00+00	\N
851c4073-41b7-4726-9407-e49bb8f0a5a1	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-24 02:00:00+00	2026-08-24 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-24 01:45:00+00	\N
85729cb6-2445-4614-8b13-6365a6ed1f76	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-12 12:06:00+00	2026-08-12 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-12 11:51:00+00	\N
863246ae-ecce-48c6-8eec-a4af2ed18329	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-10 09:48:00+00	2026-08-10 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-10 09:33:00+00	\N
8ab01c53-a07b-4189-91b6-142c06520057	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-12 04:18:00+00	2026-08-12 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-12 04:03:00+00	\N
8ab97352-17a1-4775-9c7f-a546c2a96f86	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-14 04:18:00+00	2026-08-14 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-14 04:03:00+00	\N
8c68c39e-f7e3-4f38-a531-e04d1d199852	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-22 09:21:00+00	2026-08-22 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-22 09:06:00+00	\N
8d6aea2f-342f-45cb-8b32-c77a87d0b27f	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-25 07:03:00+00	2026-08-25 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-25 06:48:00+00	\N
8da3ff6f-1d93-4ce6-a736-4020e5a2f224	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-11 09:21:00+00	2026-08-11 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-11 09:06:00+00	\N
8dc5c690-35c6-43ed-a281-939cd5f62739	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-14 07:03:00+00	2026-08-14 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-14 06:48:00+00	\N
8df196bb-bc21-4ff0-a26a-24444ae551b3	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-20 12:06:00+00	2026-08-20 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-20 11:51:00+00	\N
90ff38e8-8c9a-4a1e-bf35-25bf19724a67	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-18 02:00:00+00	2026-08-18 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-18 01:45:00+00	\N
91993d3a-f3e9-4ae1-9728-8e45a9de4e20	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-22 02:00:00+00	2026-08-22 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-22 01:45:00+00	\N
93af460a-c483-48db-8110-a4bd92e29ebf	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-12 09:21:00+00	2026-08-12 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-12 09:06:00+00	\N
94136662-0e08-46c1-828e-30a3c20b607c	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-18 07:03:00+00	2026-08-18 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-18 06:48:00+00	\N
958bfc75-f147-4578-aa12-ca376807becb	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-22 07:03:00+00	2026-08-22 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-22 06:48:00+00	\N
968f1151-b6ac-41ec-adc4-ac98571f77d0	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-21 04:18:00+00	2026-08-21 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-21 04:03:00+00	\N
996666a0-2009-4878-ab4b-d35274b29bbe	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-27 02:00:00+00	2026-08-27 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-27 01:45:00+00	\N
9aa60518-f56a-4278-86f1-c7243b120fe1	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-16 04:45:00+00	2026-08-16 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-16 04:30:00+00	\N
9abbd2b0-ef92-46ad-bc18-db993da47c94	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-28 04:18:00+00	2026-08-28 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-28 04:03:00+00	\N
9bf2b2a7-8f83-4d6f-a806-e7300da8a64d	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-19 12:06:00+00	2026-08-19 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-19 11:51:00+00	\N
9c0c48f1-1510-41b5-96df-dc74d3d72ddb	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-11 07:03:00+00	2026-08-11 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-11 06:48:00+00	\N
9c50bf97-8c72-4ea0-ac83-7c183ecdaf45	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-19 02:00:00+00	2026-08-19 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-19 01:45:00+00	\N
9d78da56-927b-40ec-927b-9f138f7cb7f0	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-22 02:00:00+00	2026-08-22 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-22 01:45:00+00	\N
9fdd205b-cb60-4a78-924c-0700bcf6e7a0	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-11 07:03:00+00	2026-08-11 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-11 06:48:00+00	\N
a0d80c98-8cbb-4441-a894-75f6bd2520ca	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-15 02:00:00+00	2026-08-15 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-15 01:45:00+00	\N
a1768e26-0fed-45d0-a764-e7252690c684	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-08 07:03:00+00	2026-08-08 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-08 06:48:00+00	\N
a18dad72-748c-46c2-ad79-649ee5239fa3	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-10 12:06:00+00	2026-08-10 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-10 11:51:00+00	\N
a50f5abe-3159-4db4-ad02-3feb359a3bdc	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-09 04:18:00+00	2026-08-09 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-09 04:03:00+00	\N
a5f223bb-5ace-4336-851d-0e7cd0d75a62	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-28 07:03:00+00	2026-08-28 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-28 06:48:00+00	\N
a621bc83-24db-4361-87c8-6a3601fbb54e	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-25 09:48:00+00	2026-08-25 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-25 09:33:00+00	\N
a634db77-4af0-48a5-8868-286bfb40add4	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-17 09:48:00+00	2026-08-17 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-17 09:33:00+00	\N
a8763bf3-e776-4045-ae5e-092bea6856ce	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-13 12:06:00+00	2026-08-13 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-13 11:51:00+00	\N
ab7b6a39-0f22-4f9d-b92b-4031519f481c	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-23 12:06:00+00	2026-08-23 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-23 11:51:00+00	\N
b0573018-be51-4922-8139-4981ff7a018d	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-21 07:03:00+00	2026-08-21 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-21 06:48:00+00	\N
b209de10-a36a-4c81-bd85-d60144419063	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-28 04:45:00+00	2026-08-28 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-28 04:30:00+00	\N
b220a5a9-2cc2-441f-ab04-9cdd6d342331	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-23 09:48:00+00	2026-08-23 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-23 09:33:00+00	\N
b26eae04-1db7-4f0f-9206-77181f26ecac	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-18 09:48:00+00	2026-08-18 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-18 09:33:00+00	\N
b3893a9c-5049-46a7-ac40-bb1693a2b1e0	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-12 04:45:00+00	2026-08-12 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-12 04:30:00+00	\N
b4630cb2-c82b-45e2-a371-76c58ba787ac	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-08 09:21:00+00	2026-08-08 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-08 09:06:00+00	\N
b507307f-efbd-4fac-823b-38765ca5258c	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-16 09:48:00+00	2026-08-16 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-16 09:33:00+00	\N
b5d83b39-4064-47af-93cc-32bc2971a397	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-11 12:06:00+00	2026-08-11 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-11 11:51:00+00	\N
b646133f-3116-4a35-a449-f9b9f9329bb8	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-15 07:03:00+00	2026-08-15 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-15 06:48:00+00	\N
b695404a-27a8-446f-9c6b-9c471dbe5d1a	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-21 04:45:00+00	2026-08-21 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-21 04:30:00+00	\N
b6dd3006-d37f-4160-a663-4e48dafd4496	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-26 04:45:00+00	2026-08-26 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-26 04:30:00+00	\N
b7fd6104-6161-4ec0-ac1d-1c8749b8ddb2	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-09 09:48:00+00	2026-08-09 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-09 09:33:00+00	\N
b8f294f7-100f-4901-a0af-80a3c0b72b85	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-13 09:48:00+00	2026-08-13 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-13 09:33:00+00	\N
b942ba20-9e07-45e1-b0a5-dc0cbbb8bd81	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-12 12:06:00+00	2026-08-12 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-12 11:51:00+00	\N
b95ba1e5-a3eb-483e-a60e-eb8dbc92ded0	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-24 04:45:00+00	2026-08-24 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-24 04:30:00+00	\N
b98dabf1-161d-4dde-9cc1-4b25c819bc91	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-09 04:45:00+00	2026-08-09 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-09 04:30:00+00	\N
ba263fe2-b679-4d7a-b09c-8d27e83411d1	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-16 12:06:00+00	2026-08-16 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-16 11:51:00+00	\N
bc1f00cb-2a08-4bf6-8a9e-9548ada0888f	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-08 02:00:00+00	2026-08-08 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-08 01:45:00+00	\N
bd6fd5b6-b904-4e7e-861d-ceff69cdc67c	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-27 02:00:00+00	2026-08-27 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-27 01:45:00+00	\N
be428de8-f46c-4048-b420-c95e66035e2e	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-17 02:00:00+00	2026-08-17 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-17 01:45:00+00	\N
c05081f4-b830-474d-9d7f-1f185da7a548	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-09 02:00:00+00	2026-08-09 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-09 01:45:00+00	\N
c1c8a045-3b46-486b-9e0e-8e0115e9afbf	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-18 04:18:00+00	2026-08-18 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-18 04:03:00+00	\N
c21fe9d4-8823-49f6-a172-e3ca92b5d0dc	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-10 12:06:00+00	2026-08-10 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-10 11:51:00+00	\N
c28ebc30-54a9-4862-87fe-13cec527c934	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-26 12:06:00+00	2026-08-26 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-26 11:51:00+00	\N
c76fd972-bee3-478d-a3d6-45ead15870b5	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-08 02:00:00+00	2026-08-08 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-08 01:45:00+00	\N
c78c274d-1081-418c-8fe1-aa92cd01a0eb	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-16 02:00:00+00	2026-08-16 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-16 01:45:00+00	\N
ca6afc76-5f63-419d-a5a0-951bf5e907a3	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-15 07:03:00+00	2026-08-15 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-15 06:48:00+00	\N
ca746880-10f7-4a00-abee-f8ed6262177e	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-19 09:21:00+00	2026-08-19 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-19 09:06:00+00	\N
caa284f7-b6c1-4fed-890d-e4a149a51450	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-13 07:03:00+00	2026-08-13 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-13 06:48:00+00	\N
cc46e1df-497e-4b02-a2f0-aeaca018ff48	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-16 07:03:00+00	2026-08-16 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-16 06:48:00+00	\N
cd2eea5a-ba16-4abf-abc9-1d64627dbdf5	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-22 09:48:00+00	2026-08-22 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-22 09:33:00+00	\N
ce9231e3-b57c-4701-af15-5aaa070e5d9a	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-26 04:18:00+00	2026-08-26 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-26 04:03:00+00	\N
cea2b1dc-285f-4a0c-b227-6e9d55dff1cb	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-24 04:18:00+00	2026-08-24 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-24 04:03:00+00	\N
d13714af-70af-4bc3-8a87-adfea041a73e	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-27 09:21:00+00	2026-08-27 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-27 09:06:00+00	\N
d184dd49-e7e0-485e-8bed-6e519caee166	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-11 02:00:00+00	2026-08-11 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-11 01:45:00+00	\N
d3f1e1e3-91e3-4c17-9366-e281d7b62e81	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-16 04:18:00+00	2026-08-16 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-16 04:03:00+00	\N
d44bc289-89f3-4815-bf1f-672698cf699a	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-26 07:03:00+00	2026-08-26 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-26 06:48:00+00	\N
d4a16f04-fadf-416c-a85e-8388e13ff551	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-21 09:48:00+00	2026-08-21 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-21 09:33:00+00	\N
d4e14fcb-6dd1-47e6-8be1-f8a4b55dd6a5	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-09 12:06:00+00	2026-08-09 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-09 11:51:00+00	\N
d540714d-bd40-44d3-a293-f4c78142ea2d	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-22 07:03:00+00	2026-08-22 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-22 06:48:00+00	\N
d91a3136-1124-42a1-8808-f86317363573	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-26 09:48:00+00	2026-08-26 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-26 09:33:00+00	\N
dd48eb13-abc4-4dd8-84c9-e983da63af5a	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-24 09:21:00+00	2026-08-24 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-24 09:06:00+00	\N
de12403a-184b-4411-9a72-7c4aae8e1902	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-25 09:21:00+00	2026-08-25 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-25 09:06:00+00	\N
de337acd-111e-416f-9466-cf0374410092	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-11 02:00:00+00	2026-08-11 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-11 01:45:00+00	\N
e28b2980-a7d5-4ac6-9ac9-b30cf8124f58	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-08 09:48:00+00	2026-08-08 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-08 09:33:00+00	\N
e60ee494-70c1-4618-b208-ca0de776250d	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-14 09:48:00+00	2026-08-14 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-14 09:33:00+00	\N
e7bc3ab3-d700-4846-b2c6-b8424412242a	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-20 07:03:00+00	2026-08-20 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-20 06:48:00+00	\N
e7fcbd57-3954-4681-a57a-6cd170bda666	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-12 02:00:00+00	2026-08-12 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-12 01:45:00+00	\N
e8d91451-d05d-45fe-b78c-a8c6c27ab977	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-21 02:00:00+00	2026-08-21 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-21 01:45:00+00	\N
e9aab5bc-913c-424b-857f-bbe52a6183ab	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-24 09:48:00+00	2026-08-24 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-24 09:33:00+00	\N
ea4ba3af-4c0f-4f26-b382-dd2443736175	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-14 12:06:00+00	2026-08-14 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-14 11:51:00+00	\N
eabc36bf-afb5-44ee-aced-59b03e40ac31	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-15 09:21:00+00	2026-08-15 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-15 09:06:00+00	\N
ecbc94eb-1a62-4885-9ea6-36b82b32c065	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-17 04:45:00+00	2026-08-17 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-17 04:30:00+00	\N
ecbcbb1b-2374-412b-8eac-2e0b8b0b3e2f	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-25 02:00:00+00	2026-08-25 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-25 01:45:00+00	\N
ed5c10c9-306d-4cfa-b2da-6c66cef02702	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-25 12:06:00+00	2026-08-25 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-25 11:51:00+00	\N
ee5eae50-615c-48db-b6b4-2af08a2f33c2	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-28 02:00:00+00	2026-08-28 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-28 01:45:00+00	\N
ee60deaa-3270-4b7c-8f49-5a72eed3594a	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-27 07:03:00+00	2026-08-27 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-27 06:48:00+00	\N
ef2e35be-48c2-417b-b33a-63596b69125c	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-23 09:21:00+00	2026-08-23 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-23 09:06:00+00	\N
f00a37f5-becd-4c86-a139-93dd0fd9329d	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-23 02:00:00+00	2026-08-23 04:03:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-23 01:45:00+00	\N
f0686207-135b-40a4-a484-4048ae40eed4	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-16 12:06:00+00	2026-08-16 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-16 11:51:00+00	\N
f1176f0e-8b59-4fb4-ad8f-76db2b598f84	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-25 04:45:00+00	2026-08-25 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-25 04:30:00+00	\N
f11dfcbc-2a36-4ced-a16a-3855f5e22d5f	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-10 07:03:00+00	2026-08-10 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-10 06:48:00+00	\N
f1338333-2619-429c-9365-c4f6603ea9fd	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-28 09:21:00+00	2026-08-28 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-28 09:06:00+00	\N
f19f9337-798f-4bbc-aa15-302f339591e2	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-10 04:45:00+00	2026-08-10 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-10 04:30:00+00	\N
f20017ae-2d0b-439a-b468-784e7ff9fb8b	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-18 12:06:00+00	2026-08-18 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-18 11:51:00+00	\N
f2de1fc1-61c4-48a1-9db4-1a2301a0f048	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-17 04:18:00+00	2026-08-17 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-17 04:03:00+00	\N
f731e27c-1c66-48ba-8e12-d39d9cccdee2	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-13 02:00:00+00	2026-08-13 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-13 01:45:00+00	\N
f761fa6d-2792-46d6-9caf-51adb6b9e103	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-13 07:03:00+00	2026-08-13 09:33:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-13 06:48:00+00	\N
f7db444a-8877-470d-a83e-599aee10ebf7	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-11 09:48:00+00	2026-08-11 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-11 09:33:00+00	\N
f96162ed-b7d5-433f-a0ce-2ef69366f372	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-28 12:06:00+00	2026-08-28 14:09:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-28 11:51:00+00	\N
f98fe809-3b43-412f-b664-b6ae1b8e7730	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-09 02:00:00+00	2026-08-09 04:30:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-09 01:45:00+00	\N
fb7f7acb-553c-4c95-a258-22c915407927	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-09 07:03:00+00	2026-08-09 09:06:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-09 06:48:00+00	\N
fc9ef61b-69a9-4ce5-ae71-48a69741bee3	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-27 12:06:00+00	2026-08-27 14:36:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-27 11:51:00+00	\N
fca58c7f-ab89-4cd3-a7d8-06031072c2f2	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-14 09:21:00+00	2026-08-14 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-14 09:06:00+00	\N
fda644cf-a37a-46e8-9eb7-e998164c32a5	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-23 04:45:00+00	2026-08-23 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-23 04:30:00+00	\N
fddce7ea-2575-4425-99b9-e00eff124c22	e82bd69e-79a2-4c79-a020-5eafd337c553	715df074-412b-441b-b93e-0dfa4f6ee8f9	2026-08-19 09:48:00+00	2026-08-19 11:51:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-19 09:33:00+00	\N
ffe37063-6ea8-4062-b461-a38317e4f182	e82bd69e-79a2-4c79-a020-5eafd337c553	69fcd15b-77e6-4ba9-a65a-e5e12019eba0	2026-08-20 04:45:00+00	2026-08-20 06:48:00+00	OPEN	90000.00	dac35bb9-78bf-47c6-bda1-6c991585e958	2026-08-07 07:34:19.893159+00	2026-08-20 04:30:00+00	\N
d3da1059-d608-448e-a1ae-353705b3a94b	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-16 10:29:00+00	2026-08-16 12:59:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-16 10:14:00+00	\N
d40de814-36af-47a2-b7ee-5980fa93c007	f3c19e6d-c4b7-4411-89c4-75331b6c2a43	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-24 07:21:00+00	2026-08-24 10:14:00+00	OPEN	76000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-24 07:06:00+00	\N
d85f240d-89cc-4437-b6a9-fc28972dc6e4	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-22 02:00:00+00	2026-08-22 04:30:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-22 01:45:00+00	\N
d9664308-23af-48ab-8849-5809f30ead68	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-17 13:37:00+00	2026-08-17 15:58:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-17 13:22:00+00	\N
e04e5c31-b8fb-4fe9-adc2-14ce2bba63e4	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-18 10:29:00+00	2026-08-18 12:50:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-18 10:14:00+00	\N
e187082f-2d61-441c-a8cd-ba325976eb0e	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-23 07:44:00+00	2026-08-23 10:14:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-23 07:29:00+00	\N
e62fdfe0-4ff1-4c9a-9579-c09311e2f233	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-23 13:37:00+00	2026-08-23 15:58:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-23 13:22:00+00	\N
ecda2a51-9e79-4f25-9d0e-1622bcbe3ec8	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-15 04:36:00+00	2026-08-15 07:06:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-15 04:21:00+00	\N
f001b124-d853-40bf-acf3-77a471aac701	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-16 02:00:00+00	2026-08-16 04:30:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-16 01:45:00+00	\N
f0ee1241-770f-444d-9eaa-3ccc0e2c38e5	8a807d6a-5673-46fc-8549-1111263594a7	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-20 05:08:00+00	2026-08-20 07:29:00+00	OPEN	120000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-20 04:53:00+00	\N
f71c608f-ee90-4e7b-856f-92719839c612	c4f6fccc-aec1-4512-9bc4-942c2cb576f4	7daf46fc-c530-4e57-bba8-d786f1c6a2e4	2026-08-08 07:44:00+00	2026-08-08 10:14:00+00	OPEN	90000.00	2810314c-85d7-46e5-8449-e69ec5ad3285	2026-08-07 07:45:11.396397+00	2026-08-08 07:29:00+00	\N
\.


--
-- Data for Name: tickets; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.tickets (id, booking_id, booking_seat_id, seat_id, ticket_code, qr_nonce, seat_row, seat_number, status, issued_at, checked_in_at, checked_in_by, unit_price, pricing_details, scan_code) FROM stdin;
ce71e6d5-d739-427b-a72c-d96264fa9251	0c6f3ae9-dfaa-4713-91e9-6715e8f3b78d	fc09d9aa-d0b2-44d5-8115-82e83ffcffb2	bb7adacc-7a56-450d-8421-ac0d76c60a86	C7260730001-01	cfd55cf5258d46b8bd15af2656b9e620	C	10	ISSUED	2026-07-28 12:03:33.011302+00	\N	\N	0.00	{}	Q236157734A1
795636ef-4b39-4212-aea3-cfb77d7e66ae	1860f4e8-918e-4597-a86d-2577be728613	d2a29c4f-18e1-4880-a101-2c1a57760d38	32ca5abb-3280-46e7-b5c1-053f8169675f	C7260730002-01	7e97f3080b3f4fdab8d1c6e343c4a9cf	D	8	ISSUED	2026-07-29 06:45:07.339846+00	\N	\N	0.00	{}	Q4F3FD51FE0B
69c90350-087f-462d-81b6-97984f547b2b	ff8333f4-1be5-4a74-9b3d-e3ee400772d9	5273ef67-f2b6-4047-9890-b5fb2b534d34	078e8247-f639-442f-9ed8-c10452b93473	C7260730003-01	a4a4f918a6df4ce19aa48d54688119a1	E	7	ISSUED	2026-07-29 07:21:40.053029+00	\N	\N	0.00	{}	Q012FBFCA59A
0da25da9-2716-4167-acd3-1fafa1eb137f	ff8333f4-1be5-4a74-9b3d-e3ee400772d9	d876cb60-941e-4880-9af5-c19d7591769f	5de88e3a-c599-4d7d-b4fb-35c594942a43	C7260730003-02	c052d83ef66c45458011b1ac10a3f5b0	E	8	ISSUED	2026-07-29 07:21:40.053029+00	\N	\N	0.00	{}	QE873C89B619
7168df21-ae2d-46a6-968d-b43757255099	751d1181-addc-4100-a0d6-da785f9468b4	beb2aeff-1947-4af5-b46c-b63400619f95	03efca4b-c0a2-45b8-8212-fbc109c90f90	C7260730004-01	53239c8b6d7d42a8a6362cb4c27a7703	A	6	ISSUED	2026-07-29 13:15:19.439433+00	\N	\N	0.00	{}	Q3B3B02FDB5F
281fe960-4869-453e-bedd-bb8bb497375a	4b3483f4-1f1a-454c-9871-63b55cdf0c73	1ef23726-31b3-49f7-8828-6b173ca3dff9	25eae2e2-84b0-4afc-b3c9-63c500ea3879	C7260730005-01	678f6b96f67b4044af97566a1b527271	A	5	ISSUED	2026-07-29 13:38:47.445028+00	\N	\N	0.00	{}	Q95298D0067E
40d75731-ceb9-4f19-9d4f-eff337c59981	3e42ae6b-29d8-45ea-b80c-e7b5ddf1053d	678d012f-0373-496c-a1fb-09070dae79ff	9ba6db82-6e32-4413-8a23-de398df9ffb1	C7260730006-01	ec4e501067884769b3e7e84af3828883	A	8	ISSUED	2026-07-29 13:58:50.696343+00	\N	\N	0.00	{}	Q38009460388
84f60fa0-6a0c-42b9-90f7-eacbaf70270c	2a99efd7-7196-4f63-ac4b-f3670caed351	fd7bf76e-ad46-402e-8fd0-da8475677937	68768715-f9e6-4f9c-a7c0-efbc83edfc75	C7260801011-01	da6fae20eaaf493ab0be5d89ed1e124a	A	12	ISSUED	2026-07-30 15:11:33.114885+00	\N	\N	0.00	{}	QE829F0DE607
cfacf2f0-2c9f-4226-9d1b-23c26e5a90e7	9c735dd5-26fc-4ca8-979c-5c529a8681b6	c95d3b27-18d3-4277-85af-412b96b2bd34	f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a	C7260731005-01	95a622bd4b964c92ab00482e6d059da8	A	11	ISSUED	2026-07-30 15:16:55.81962+00	\N	\N	0.00	{}	QDDA5C948151
9e5a8039-efa3-4546-a3f7-de5bb05f553f	9c735dd5-26fc-4ca8-979c-5c529a8681b6	01c0531c-9be8-4e75-80f6-1b952a530abf	68768715-f9e6-4f9c-a7c0-efbc83edfc75	C7260731005-02	f08c6a10a8a64aada0160a33602b20ca	A	12	ISSUED	2026-07-30 15:16:55.81962+00	\N	\N	0.00	{}	Q5018C4F67AA
7be39ad5-e5eb-4685-ae1a-956f2e67e894	bcbddc3f-79b6-4d4b-af86-33a1f1e93904	4233c406-1798-4234-90e8-5ba522f72b5d	aa2f6757-f430-4564-abf7-5ff595888024	C7260731006-01	432c7eb597a04523a1703916d6e9c9e9	A	9	ISSUED	2026-07-30 15:22:43.78686+00	\N	\N	0.00	{}	QB4C9B00AC18
3c1e9158-fc60-41a5-86e4-63c8bfe844e1	ffb77e65-d41f-48b7-a23a-fd0221a6c53c	38b07830-d184-4376-b567-284552f0e615	68768715-f9e6-4f9c-a7c0-efbc83edfc75	C7260731007-01	fa0773e5d2da451b8c1c4082829acb28	A	12	ISSUED	2026-07-30 15:34:25.251012+00	\N	\N	0.00	{}	Q35B03290E43
3ccc4d92-e73a-46f9-bc78-2d880c95a370	fa5e723c-4c12-4fd5-8708-e23052f2cee8	35afc7d4-81ed-4e1b-9652-df2e67b53752	68768715-f9e6-4f9c-a7c0-efbc83edfc75	C7260802001-01	ccc4353362d74400a23fcefe779c5697	A	12	ISSUED	2026-07-30 15:44:52.380195+00	\N	\N	0.00	{}	Q4526E15C0FF
5e78c323-d594-4845-bfc8-813643a8e6fe	d210f403-2fdd-4583-8e18-8cb7034c1a7d	c45ad659-7b0d-4f71-8d1e-e374b3ebd603	1129090f-3c21-49d4-b882-b3c62f54be1a	C7260731008-01	b37d821829b44c7fa674bb286599420b	B	11	ISSUED	2026-07-30 15:49:20.942537+00	\N	\N	0.00	{}	Q855FD594042
21042024-b534-4b59-a9cb-4dbf9011de88	8eb7e27f-5167-4c41-81a0-cde73361f10f	8a8620dd-a9f7-4a4b-ad5e-915c57332708	68768715-f9e6-4f9c-a7c0-efbc83edfc75	C7260731009-01	ee1ab763544243dc979c794b649fe23c	A	12	ISSUED	2026-07-30 16:14:39.110867+00	\N	\N	0.00	{}	Q0292FBCB2D7
19538c6d-d1fc-4312-914f-287ea82deb8c	3f3d7716-141f-4302-8093-5a9f1fc46235	c02b30ad-8dcc-4e14-aaf5-c00124ead6c2	1129090f-3c21-49d4-b882-b3c62f54be1a	C7260801012-01	788a4eeb48f14fd3aec1de429f2d4587	B	11	ISSUED	2026-07-30 16:24:54.915754+00	\N	\N	0.00	{}	Q2EA27B4FB67
6ad4fb51-1e12-4deb-bc30-d5302cab3eec	a4349175-2741-4061-be9a-d488c5fd959d	fd350b19-ce60-4c65-b5db-f3c49a6e63ad	2ed79287-99c4-4923-8aa9-a9e39223ad74	C7260802002-01	5c57ebc12b034a7e8ee74e4b444ec263	A	10	ISSUED	2026-07-30 18:27:32.166246+00	\N	\N	0.00	{}	QD43F0F0F9BB
83a3887e-5194-4c66-ba5e-762bc4213af1	a4349175-2741-4061-be9a-d488c5fd959d	74b9c13a-17f2-47a7-b40a-69420dadb411	f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a	C7260802002-02	990dedbaec3143ed815bba9f6f8287bf	A	11	ISSUED	2026-07-30 18:27:32.166246+00	\N	\N	0.00	{}	QF25435B26E0
ec6a34f3-10a5-4f1e-997a-7e64b5ecabcb	6bbd507d-85d0-4298-ab5f-73845dc0a90a	85aa6f1c-7f02-48e6-8ee7-13ca0489635c	f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a	C7260731011-01	6a1d68fa2c754a629539e2bdd0bc72e1	A	11	ISSUED	2026-07-30 18:55:04.577309+00	\N	\N	0.00	{}	QA032D033A82
ee08fe06-4050-4782-83cb-bbb98c797617	1fcbccd3-6e37-46b3-b44d-4d0f5fed1550	8533ee26-1b29-497e-84a9-29aa227268d7	f053bfb5-fdef-4e94-90c0-2dbc1ab0dc5a	C7260731012-01	6004a0f603144303b5b581c14f24dc35	A	11	ISSUED	2026-07-30 19:05:28.817411+00	\N	\N	0.00	{}	Q8196023D84A
ab4aa497-5a3c-462e-a60a-aae5d0dba7bc	4ab4de29-b4a0-474b-ac6b-fb4c2ee06d75	38d6ce79-923c-4e86-afdb-d15f0793014b	03efca4b-c0a2-45b8-8212-fbc109c90f90	C7260731013-01	ee6b94e5b1b94058b43941b02bd77bfb	A	6	ISSUED	2026-07-30 19:15:33.916256+00	\N	\N	0.00	{}	Q5133BEDCA61
d1fccd97-c073-46a5-b175-c2669e48387b	85a22a13-c8ac-48f5-b50c-a8b9a22b2f10	c98be923-4081-4696-b4fc-a7e76ff6dc30	e57ad5e9-f5ab-480f-9153-7dfa510e2a70	C7260801014-01	c704d2bfa8da41648f657ead828171df	B	10	ISSUED	2026-07-30 19:39:25.528573+00	\N	\N	0.00	{}	Q337F29EB32C
86576948-5bfe-4725-87f5-59056dcd886d	85a22a13-c8ac-48f5-b50c-a8b9a22b2f10	b9c64734-2cdf-4f43-981d-9a58c894c219	1129090f-3c21-49d4-b882-b3c62f54be1a	C7260801014-02	ce27686e487b410ea8342463e7a51d51	B	11	ISSUED	2026-07-30 19:39:25.528573+00	\N	\N	0.00	{}	Q9DBD96BFFDF
828a7286-9d0c-4277-a1aa-d8ebfd508bb2	651d5cb6-a9bd-48ad-9404-09ab5e0ee935	7a5be13f-e937-493a-b716-fd83929df431	2ed79287-99c4-4923-8aa9-a9e39223ad74	C7260731014-01	bdb08131a2af42aa808fe6f722e65be5	A	10	ISSUED	2026-07-30 19:42:47.515884+00	\N	\N	0.00	{}	QE80B54F2035
f264ea85-6d96-4862-9f9a-35d0c44eb5eb	9ce23bfc-f82f-4df3-bcb0-d520925f6c98	5a5e5ff1-06f7-4459-ab3d-20a0462b227c	dc6f6ebd-0e3f-4a29-aa3b-52f5535b8029	C7260803001-01	ef33e13805a54aef9e3051394a88740f	C	7	ISSUED	2026-08-02 12:20:10.50569+00	\N	\N	0.00	{}	Q69B00E0B080
ff1dc471-18b3-40ad-8330-3703ffcf730b	9ce23bfc-f82f-4df3-bcb0-d520925f6c98	4b91f56f-0e7f-4a46-bc95-2aa778892ad2	ee3f6974-b9a2-4808-9dd5-7ec4d7cfb5fb	C7260803001-02	d7b27e80fc9944e087b79e0ffb3e216d	C	8	ISSUED	2026-08-02 12:20:10.50569+00	\N	\N	0.00	{}	Q340D150F9F0
09611a32-e7aa-460b-be1c-d9fb7251d9fb	2a5ef731-b92b-4fec-98e0-7ee13ca2bdf2	1c8b9577-f22b-4d90-a97a-8cf00344c542	51fe1dd3-cf0f-4858-9f2b-0b548ce8d52e	C7260807001-01	5121c3a01c96460f8f2f2b9cc68e71f4	D	7	USED	2026-08-04 14:53:28.779915+00	2026-08-05 16:12:06.206065+00	2810314c-85d7-46e5-8449-e69ec5ad3285	0.00	{}	Q2F83AB69ADE
2bf8a8a0-b246-4f6a-a00d-7bac0664c795	2a5ef731-b92b-4fec-98e0-7ee13ca2bdf2	aba62010-f054-48ff-9a93-6aeed2feacbf	32ca5abb-3280-46e7-b5c1-053f8169675f	C7260807001-02	08b7d8d14c2b4c59aa41c02da8d0a521	D	8	USED	2026-08-04 14:53:28.779915+00	2026-08-05 16:12:06.206065+00	2810314c-85d7-46e5-8449-e69ec5ad3285	0.00	{}	Q80EAF878066
2e4c49f8-e6f4-4331-95b2-10fb88427cee	533600da-cf60-4155-b812-c255add2ef45	55bf09ae-4525-44b1-bf51-cbc90682cd50	32ca5abb-3280-46e7-b5c1-053f8169675f	C7260807002-01	f4825024f079455f9ae5bbedef06a2bb	D	8	ISSUED	2026-08-06 12:12:36.938116+00	\N	\N	0.00	{}	QBEAE0687ECA
75e6d425-42c2-49b7-bf9d-fcad40a2cb75	533600da-cf60-4155-b812-c255add2ef45	44a2a193-fd2f-4aae-b667-6ab7d964fc42	77e0c246-d4ce-46f5-bc39-c58fa01b46d3	C7260807002-02	ebdc50b7069f42dc96852ad92f00b5ec	D	9	ISSUED	2026-08-06 12:12:36.938116+00	\N	\N	0.00	{}	Q73AFA424DCE
4780f9ba-11aa-4fc6-8f5f-da8c563e01d8	b23ea768-02e2-4241-90a7-fcc4c22d1dd2	1123d3ff-0e13-4d52-bd19-e60313ba5635	7191355f-e232-4000-8daa-22c407f8aae5	C7260808001-01	969697b66c464a0fbafa557211849f01	D	6	USED	2026-08-07 09:02:40.443031+00	2026-08-07 09:07:21.172817+00	2810314c-85d7-46e5-8449-e69ec5ad3285	0.00	{}	Q4D4D814D21C
597a133d-a459-4f13-82ac-addda1405810	a72593a3-4040-4aa9-a352-3f050a6faf31	f839faf8-79b6-4fa9-a3b4-53d763b8b5bd	32ca5abb-3280-46e7-b5c1-053f8169675f	C7260810001-01	e0b1210a6fd3eded5a5b83b5caa4955e	D	8	ISSUED	2026-08-10 06:00:45.727464+00	\N	\N	150000.00	{"surcharge": "0", "base_price": "120000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.25"}	QXKQCW9SCQEQ
c054c36b-2504-4dae-a52b-87f85c82e81a	2e1cbde3-f2c7-4a4c-ba5c-9345fb0466a7	fea69643-4b6a-4ea1-be4e-6b380ba56845	d9cc21ac-906f-467c-8b48-d1cc107c03d6	C8260810001-01	f22a7f747e35cc61636900a6a70e4f75	A	12	ISSUED	2026-08-10 06:37:09.001952+00	\N	\N	90000.00	{"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}	QZN5NXDMFA6M
9cefc1a9-3836-4251-a0b8-aeecea36b495	9257dcad-0488-420e-a6eb-be52650d2702	7790d26b-abb7-4eb4-8d7b-654ee850e193	5042eca3-dfaa-4f3c-a99b-390eb2bd346f	C8260810002-01	9bd679fedd41268b5ceb9bae5ad53b9e	A	11	ISSUED	2026-08-10 06:44:28.853279+00	\N	\N	90000.00	{"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}	Q9IZJSRT9P4C
0210a849-5a67-4bf8-84df-83533dddcff7	dfae2120-2fcd-4778-8f30-76b37f599e56	0b86af4b-6fbf-41c3-bd0f-8eb8c5561d69	aa2f6757-f430-4564-abf7-5ff595888024	C7260810002-01	28b37e8b2f8d67eeafdc453f6309beeb	A	9	ISSUED	2026-08-10 06:46:19.622465+00	\N	\N	90000.00	{"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}	QBMFF0E9RHCK
e8218081-f95a-46ab-ba50-71afa5e04086	dfae2120-2fcd-4778-8f30-76b37f599e56	29d05e98-841a-4785-b35c-530f88e8d16f	9ba6db82-6e32-4413-8a23-de398df9ffb1	C7260810002-02	af49027bff1c19cb4245fbe7abd53e65	A	8	ISSUED	2026-08-10 06:46:19.622465+00	\N	\N	90000.00	{"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}	QLZZLERNU9BZ
bfa45ecd-5bc0-41b6-a435-841eadd174c4	dfae2120-2fcd-4778-8f30-76b37f599e56	c52c8929-a997-4a0c-8071-ca5dd545dad7	efc80c2a-90f1-40d3-bda8-4664d2e29853	C7260810002-03	1ba47f9c388508f30cbedee977928a70	A	7	ISSUED	2026-08-10 06:46:19.622465+00	\N	\N	90000.00	{"surcharge": "0", "base_price": "90000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}	QK1BDTKO0ES6
0e408774-95b4-468a-b438-1fecf2ec59ab	3c845d97-791d-45d8-9c7e-86213bd6ee02	34243790-93e6-40ed-90a8-8f53e9859489	dc6f6ebd-0e3f-4a29-aa3b-52f5535b8029	C7260811001-01	8ef1f53aea9686dd201852c2a4fe1ff7	C	7	ISSUED	2026-08-10 08:15:28.126576+00	\N	\N	120000.00	{"surcharge": "0", "base_price": "120000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}	QNV3STQWH58H
a65b90fe-f826-4eb8-bf7f-fd6f0f06fe63	3c845d97-791d-45d8-9c7e-86213bd6ee02	9b5d7da7-334f-4d35-9245-7a996473f7ff	c9583494-ebc9-43df-a5ed-fc88cf553f0e	C7260811001-02	4e5d9b41d57467fc12878e7abc177fc6	C	6	ISSUED	2026-08-10 08:15:28.126576+00	\N	\N	120000.00	{"surcharge": "0", "base_price": "120000.00", "pricing_rule": null, "pricing_rule_id": null, "rule_multiplier": "1", "seat_multiplier": "1.00"}	Q9C10SOZCZAW
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.user_roles (user_id, role_id, created_at) FROM stdin;
774593d4-5da2-440d-8de6-3ea646880bd1	1	2026-07-28 11:24:35.513918+00
e7288ffc-c117-4eb5-a137-6011c94c0b5c	2	2026-07-28 11:24:35.513918+00
2810314c-85d7-46e5-8449-e69ec5ad3285	3	2026-07-28 11:29:12.62894+00
dac35bb9-78bf-47c6-bda1-6c991585e958	3	2026-07-29 15:58:33.683767+00
5db543a6-cbad-48cb-9a53-0417e1ff70e1	1	2026-08-03 16:28:41.33147+00
82818a84-86a8-45e9-83af-0af1d0ed77b3	1	2026-08-03 16:32:46.086038+00
5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	1	2026-08-03 16:36:12.998547+00
26409e9e-bac0-4ff6-83c1-9f399889cc67	3	2026-08-05 16:23:29.657003+00
5e0114d6-2880-46c2-9c7c-b6cbd2a6aea3	3	2026-08-07 07:19:46.153068+00
6cb9ebe0-9d8a-49c6-bcce-6669fd5ca41b	1	2026-08-07 07:37:09.819753+00
a91cb727-754e-42ba-a15c-8a1466e8ef0a	1	2026-08-10 08:08:12.904869+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.users (id, email, phone, password_hash, full_name, date_of_birth, gender, is_active, created_at, updated_at, address, receive_marketing_emails, is_verified, verification_code, verification_code_expires_at) FROM stdin;
5db543a6-cbad-48cb-9a53-0417e1ff70e1	test_register_user@gmail.com	0912345678	$2b$12$A7caNZGlndP5ma88B9H29OyZCgINy11te4sTsmlaXkaZlI4RWLX7C	Nguyen Van Test	2000-01-01	male	t	2026-08-03 16:28:41.33147+00	2026-08-03 16:28:42.268633+00	Ha Noi	f	f	169850	2026-08-03 16:38:42.300485+00
82818a84-86a8-45e9-83af-0af1d0ed77b3	test_register_user_otp@gmail.com	0912345679	$2b$12$PC32w05E58rl8XacLnVNKeXOyEOh/TSaIN49tXmLiDD4wnupF9ice	Nguyen Van TestNguyen Van Test	2000-01-01	female	t	2026-08-03 16:32:46.086038+00	2026-08-03 16:32:46.729575+00	Ha NoiHa Noi	t	f	297959	2026-08-03 16:42:46.777727+00
a91cb727-754e-42ba-a15c-8a1466e8ef0a	2200002381@nttu.edu.vn	0388562277	$2b$12$bwOomVOc14eMEPH73OW5FuuqutVLIbPDEJS3.gIr/ZzrX8NvxmB0q	Nguyễn Thanh Phong	2004-10-12	male	t	2026-08-10 08:08:12.904869+00	2026-08-10 08:09:01.046423+00	Quận 7, Thành phố Hồ Chí Minh	t	t	\N	\N
774593d4-5da2-440d-8de6-3ea646880bd1	customer@gmail.com	0900000004	$2b$12$86rq3KQFtE2ylZn/.hfuw.b4mXx0lKC/bEH0o3/L0ndz3wT2MrjIy	Nguyễn Văn Khách	\N	\N	t	2026-07-28 11:24:35.513918+00	2026-08-12 15:59:23.340226+00	\N	t	t	\N	\N
6cb9ebe0-9d8a-49c6-bcce-6669fd5ca41b	votoanphu3769@gmail.com	0953867421	$2b$12$c2ITT5cCkO5x3YoGFWfhq.umsY2.QaiBsm0kaT9DuQ.ZDtK2uyiSW	Võ Toàn Phú	2004-09-09	other	t	2026-08-07 07:37:09.819753+00	2026-08-10 06:48:04.297726+00	Quận 7	t	t	\N	\N
e7288ffc-c117-4eb5-a137-6011c94c0b5c	admin@cineai.vn	0900000002	$2b$12$84HaniPNP0FJAHt2i7s4mOWhAOob1vNH2ig8otAu9fveX7kaD1w12	Quản Trị Viên CineAI	\N	\N	t	2026-07-28 11:24:35.513918+00	2026-08-12 15:59:23.340226+00	\N	t	t	\N	\N
dac35bb9-78bf-47c6-bda1-6c991585e958	admin2@cineai.vn	0987865437	$2b$12$4s3ENRZzX1.dOJhtLdMPNe0z3WVdNRaN3ugyyZ93cn3Kpi7lwr.xe	Chi nhánh Cine quận 8	\N	\N	t	2026-07-29 15:58:33.456221+00	2026-07-29 15:58:33.456221+00	\N	t	t	\N	\N
2810314c-85d7-46e5-8449-e69ec5ad3285	admin1@cineai.vn	0900000003	$2b$12$sutck202AboEcAmZZblLzeC2.Wx3RhCWpaki8a1.To/3mIVjqXT1m	Quản trị viên chi nhánh CineAI	\N	\N	t	2026-07-28 11:29:12.155666+00	2026-08-12 15:59:23.340226+00	\N	t	t	\N	\N
5d21d28a-6d2b-4194-a5ba-3413ddfe9bc9	nguyendangthanhphong.lop8a7.23@gmail.com	0388562250	$2b$12$FFWwOUqOGyAAk08mFWz0P.fKKpA02CJ8UBiJE1DDLmsz3XtU9wwvC	Nguyễn Đặng Thanh Phong	2004-10-12	male	t	2026-08-03 16:36:12.998547+00	2026-08-03 16:59:55.901215+00	Quận 7	t	t	\N	\N
5e0114d6-2880-46c2-9c7c-b6cbd2a6aea3	admin_q6@cineai.vn	\N	$2b$12$rK7KhCBS/rBbtuqH79cXzuVoSRkoXd5EHxTolmzsFkVm1dt4mUvEe	Branch Admin Q6	\N	\N	t	2026-08-07 07:19:45.916726+00	2026-08-07 07:19:45.916726+00	\N	t	f	\N	\N
26409e9e-bac0-4ff6-83c1-9f399889cc67	branchadmin.hcm@cinema.vn	\N	$2b$12$KysSW3LpFHCa3hfYGV47Muv6LCukrqIcigknc/Qm0WA6zfoH3/smi	Branch Admin HCM	\N	\N	t	2026-08-05 16:23:29.657003+00	2026-08-10 05:40:44.961766+00	\N	t	t	\N	\N
\.


--
-- Data for Name: vendors; Type: TABLE DATA; Schema: public; Owner: ppq_user
--

COPY public.vendors (id, code, name, description, is_active, created_at) FROM stdin;
016b902c-c6c2-4a94-ac24-25d06996a375	DEFAULT_VENDOR	Default Vendor	Auto-created default vendor	t	2026-07-28 11:28:17.131233+00
\.


--
-- Name: movie_genres_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ppq_user
--

SELECT pg_catalog.setval('public.movie_genres_id_seq', 1, false);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ppq_user
--

SELECT pg_catalog.setval('public.roles_id_seq', 3, true);


--
-- Name: seat_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ppq_user
--

SELECT pg_catalog.setval('public.seat_types_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_events audit_events_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.audit_events
    ADD CONSTRAINT audit_events_pkey PRIMARY KEY (id);


--
-- Name: auditoriums auditoriums_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.auditoriums
    ADD CONSTRAINT auditoriums_pkey PRIMARY KEY (id);


--
-- Name: booking_combos booking_combos_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.booking_combos
    ADD CONSTRAINT booking_combos_pkey PRIMARY KEY (id);


--
-- Name: booking_seats booking_seats_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.booking_seats
    ADD CONSTRAINT booking_seats_pkey PRIMARY KEY (id);


--
-- Name: bookings bookings_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_pkey PRIMARY KEY (id);


--
-- Name: branch_staff branch_staff_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.branch_staff
    ADD CONSTRAINT branch_staff_pkey PRIMARY KEY (branch_id, user_id);


--
-- Name: branches branches_code_key; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT branches_code_key UNIQUE (code);


--
-- Name: branches branches_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT branches_pkey PRIMARY KEY (id);


--
-- Name: combos combos_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.combos
    ADD CONSTRAINT combos_pkey PRIMARY KEY (id);


--
-- Name: movie_change_requests movie_change_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_change_requests
    ADD CONSTRAINT movie_change_requests_pkey PRIMARY KEY (id);


--
-- Name: movie_genre_map movie_genre_map_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_genre_map
    ADD CONSTRAINT movie_genre_map_pkey PRIMARY KEY (movie_id, genre_id);


--
-- Name: movie_genres movie_genres_code_key; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_genres
    ADD CONSTRAINT movie_genres_code_key UNIQUE (code);


--
-- Name: movie_genres movie_genres_name_key; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_genres
    ADD CONSTRAINT movie_genres_name_key UNIQUE (name);


--
-- Name: movie_genres movie_genres_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_genres
    ADD CONSTRAINT movie_genres_pkey PRIMARY KEY (id);


--
-- Name: movie_reviews movie_reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_reviews
    ADD CONSTRAINT movie_reviews_pkey PRIMARY KEY (id);


--
-- Name: movies movies_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movies
    ADD CONSTRAINT movies_pkey PRIMARY KEY (id);


--
-- Name: notification_outbox notification_outbox_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.notification_outbox
    ADD CONSTRAINT notification_outbox_pkey PRIMARY KEY (id);


--
-- Name: payment_status_history payment_status_history_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.payment_status_history
    ADD CONSTRAINT payment_status_history_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: payments payments_transaction_id_key; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_transaction_id_key UNIQUE (transaction_id);


--
-- Name: pricing_rules pricing_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.pricing_rules
    ADD CONSTRAINT pricing_rules_pkey PRIMARY KEY (id);


--
-- Name: promotion_redemptions promotion_redemptions_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.promotion_redemptions
    ADD CONSTRAINT promotion_redemptions_pkey PRIMARY KEY (id);


--
-- Name: promotions promotions_code_key; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.promotions
    ADD CONSTRAINT promotions_code_key UNIQUE (code);


--
-- Name: promotions promotions_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.promotions
    ADD CONSTRAINT promotions_pkey PRIMARY KEY (id);


--
-- Name: roles roles_code_key; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_code_key UNIQUE (code);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: seat_holds seat_holds_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.seat_holds
    ADD CONSTRAINT seat_holds_pkey PRIMARY KEY (id);


--
-- Name: seat_types seat_types_code_key; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.seat_types
    ADD CONSTRAINT seat_types_code_key UNIQUE (code);


--
-- Name: seat_types seat_types_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.seat_types
    ADD CONSTRAINT seat_types_pkey PRIMARY KEY (id);


--
-- Name: seats seats_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.seats
    ADD CONSTRAINT seats_pkey PRIMARY KEY (id);


--
-- Name: showtimes showtimes_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.showtimes
    ADD CONSTRAINT showtimes_pkey PRIMARY KEY (id);


--
-- Name: tickets tickets_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_pkey PRIMARY KEY (id);


--
-- Name: auditoriums uq_auditoriums_branch_code; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.auditoriums
    ADD CONSTRAINT uq_auditoriums_branch_code UNIQUE (branch_id, code);


--
-- Name: booking_combos uq_booking_combos_booking_combo; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.booking_combos
    ADD CONSTRAINT uq_booking_combos_booking_combo UNIQUE (booking_id, combo_id);


--
-- Name: booking_seats uq_booking_seats_showtime_seat; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.booking_seats
    ADD CONSTRAINT uq_booking_seats_showtime_seat UNIQUE (showtime_id, seat_id);


--
-- Name: bookings uq_bookings_ticket_code; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT uq_bookings_ticket_code UNIQUE (ticket_code);


--
-- Name: bookings uq_bookings_user_idempotency; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT uq_bookings_user_idempotency UNIQUE (user_id, idempotency_key);


--
-- Name: movie_reviews uq_movie_reviews_movie_user; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_reviews
    ADD CONSTRAINT uq_movie_reviews_movie_user UNIQUE (movie_id, user_id);


--
-- Name: payments uq_payments_provider_ref; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT uq_payments_provider_ref UNIQUE (provider_ref);


--
-- Name: payments uq_payments_refund_request_id; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT uq_payments_refund_request_id UNIQUE (refund_request_id);


--
-- Name: payments uq_payments_user_idempotency; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT uq_payments_user_idempotency UNIQUE (user_id, idempotency_key);


--
-- Name: promotion_redemptions uq_promotion_redemptions_payment; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.promotion_redemptions
    ADD CONSTRAINT uq_promotion_redemptions_payment UNIQUE (payment_id);


--
-- Name: seat_holds uq_seat_holds_showtime_seat; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.seat_holds
    ADD CONSTRAINT uq_seat_holds_showtime_seat UNIQUE (showtime_id, seat_id);


--
-- Name: seats uq_seats_auditorium_row_number; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.seats
    ADD CONSTRAINT uq_seats_auditorium_row_number UNIQUE (auditorium_id, seat_row, seat_number);


--
-- Name: tickets uq_tickets_booking_seat; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT uq_tickets_booking_seat UNIQUE (booking_seat_id);


--
-- Name: tickets uq_tickets_ticket_code; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT uq_tickets_ticket_code UNIQUE (ticket_code);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (user_id, role_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_phone_key; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_phone_key UNIQUE (phone);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: vendors vendors_code_key; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT vendors_code_key UNIQUE (code);


--
-- Name: vendors vendors_pkey; Type: CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT vendors_pkey PRIMARY KEY (id);


--
-- Name: ix_audit_events_created_at; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_audit_events_created_at ON public.audit_events USING btree (created_at);


--
-- Name: ix_audit_events_entity; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_audit_events_entity ON public.audit_events USING btree (entity_type, entity_id);


--
-- Name: ix_audit_events_entity_id; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_audit_events_entity_id ON public.audit_events USING btree (entity_id);


--
-- Name: ix_audit_events_entity_type; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_audit_events_entity_type ON public.audit_events USING btree (entity_type);


--
-- Name: ix_bookings_ticket_code; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_bookings_ticket_code ON public.bookings USING btree (ticket_code);


--
-- Name: ix_combos_branch_id; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_combos_branch_id ON public.combos USING btree (branch_id);


--
-- Name: ix_movie_reviews_movie_id; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_movie_reviews_movie_id ON public.movie_reviews USING btree (movie_id);


--
-- Name: ix_movie_reviews_user_id; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_movie_reviews_user_id ON public.movie_reviews USING btree (user_id);


--
-- Name: ix_movies_tmdb_id; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE UNIQUE INDEX ix_movies_tmdb_id ON public.movies USING btree (tmdb_id);


--
-- Name: ix_notification_outbox_status; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_notification_outbox_status ON public.notification_outbox USING btree (status);


--
-- Name: ix_notification_outbox_user_id; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_notification_outbox_user_id ON public.notification_outbox USING btree (user_id);


--
-- Name: ix_payment_status_history_payment_id; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_payment_status_history_payment_id ON public.payment_status_history USING btree (payment_id);


--
-- Name: ix_payments_provider_transaction_no; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_payments_provider_transaction_no ON public.payments USING btree (provider_transaction_no);


--
-- Name: ix_pricing_rules_branch_id; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_pricing_rules_branch_id ON public.pricing_rules USING btree (branch_id);


--
-- Name: ix_promotion_redemptions_promotion_id; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_promotion_redemptions_promotion_id ON public.promotion_redemptions USING btree (promotion_id);


--
-- Name: ix_promotion_redemptions_user_id; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_promotion_redemptions_user_id ON public.promotion_redemptions USING btree (user_id);


--
-- Name: ix_seat_holds_expires_at; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_seat_holds_expires_at ON public.seat_holds USING btree (expires_at);


--
-- Name: ix_seat_holds_user_showtime; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_seat_holds_user_showtime ON public.seat_holds USING btree (user_id, showtime_id);


--
-- Name: ix_tickets_booking_id; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_tickets_booking_id ON public.tickets USING btree (booking_id);


--
-- Name: ix_tickets_scan_code; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE UNIQUE INDEX ix_tickets_scan_code ON public.tickets USING btree (scan_code);


--
-- Name: ix_tickets_ticket_code; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE INDEX ix_tickets_ticket_code ON public.tickets USING btree (ticket_code);


--
-- Name: uq_branch_staff_one_active_user; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE UNIQUE INDEX uq_branch_staff_one_active_user ON public.branch_staff USING btree (user_id) WHERE (is_active = true);


--
-- Name: uq_payments_active_booking; Type: INDEX; Schema: public; Owner: ppq_user
--

CREATE UNIQUE INDEX uq_payments_active_booking ON public.payments USING btree (booking_id) WHERE ((status)::text = ANY ((ARRAY['PENDING'::character varying, 'SUCCESS'::character varying, 'RECONCILIATION_REQUIRED'::character varying])::text[]));


--
-- Name: booking_combos trg_audit_booking_combos; Type: TRIGGER; Schema: public; Owner: ppq_user
--

CREATE TRIGGER trg_audit_booking_combos AFTER INSERT OR DELETE OR UPDATE ON public.booking_combos FOR EACH ROW EXECUTE FUNCTION public.cineai_audit_row();


--
-- Name: booking_seats trg_audit_booking_seats; Type: TRIGGER; Schema: public; Owner: ppq_user
--

CREATE TRIGGER trg_audit_booking_seats AFTER INSERT OR DELETE OR UPDATE ON public.booking_seats FOR EACH ROW EXECUTE FUNCTION public.cineai_audit_row();


--
-- Name: bookings trg_audit_bookings; Type: TRIGGER; Schema: public; Owner: ppq_user
--

CREATE TRIGGER trg_audit_bookings AFTER INSERT OR DELETE OR UPDATE ON public.bookings FOR EACH ROW EXECUTE FUNCTION public.cineai_audit_row();


--
-- Name: audit_events trg_audit_events_immutable; Type: TRIGGER; Schema: public; Owner: ppq_user
--

CREATE TRIGGER trg_audit_events_immutable BEFORE DELETE OR UPDATE ON public.audit_events FOR EACH ROW EXECUTE FUNCTION public.prevent_audit_mutation();


--
-- Name: payments trg_audit_payments; Type: TRIGGER; Schema: public; Owner: ppq_user
--

CREATE TRIGGER trg_audit_payments AFTER INSERT OR DELETE OR UPDATE ON public.payments FOR EACH ROW EXECUTE FUNCTION public.cineai_audit_row();


--
-- Name: promotions trg_audit_promotions; Type: TRIGGER; Schema: public; Owner: ppq_user
--

CREATE TRIGGER trg_audit_promotions AFTER INSERT OR DELETE OR UPDATE ON public.promotions FOR EACH ROW EXECUTE FUNCTION public.cineai_audit_row();


--
-- Name: tickets trg_audit_tickets; Type: TRIGGER; Schema: public; Owner: ppq_user
--

CREATE TRIGGER trg_audit_tickets AFTER INSERT OR DELETE OR UPDATE ON public.tickets FOR EACH ROW EXECUTE FUNCTION public.cineai_audit_row();


--
-- Name: auditoriums auditoriums_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.auditoriums
    ADD CONSTRAINT auditoriums_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE CASCADE;


--
-- Name: booking_combos booking_combos_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.booking_combos
    ADD CONSTRAINT booking_combos_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE CASCADE;


--
-- Name: booking_combos booking_combos_combo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.booking_combos
    ADD CONSTRAINT booking_combos_combo_id_fkey FOREIGN KEY (combo_id) REFERENCES public.combos(id) ON DELETE RESTRICT;


--
-- Name: booking_seats booking_seats_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.booking_seats
    ADD CONSTRAINT booking_seats_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE CASCADE;


--
-- Name: booking_seats booking_seats_seat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.booking_seats
    ADD CONSTRAINT booking_seats_seat_id_fkey FOREIGN KEY (seat_id) REFERENCES public.seats(id) ON DELETE RESTRICT;


--
-- Name: booking_seats booking_seats_showtime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.booking_seats
    ADD CONSTRAINT booking_seats_showtime_id_fkey FOREIGN KEY (showtime_id) REFERENCES public.showtimes(id) ON DELETE RESTRICT;


--
-- Name: bookings bookings_showtime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_showtime_id_fkey FOREIGN KEY (showtime_id) REFERENCES public.showtimes(id) ON DELETE RESTRICT;


--
-- Name: bookings bookings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: branch_staff branch_staff_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.branch_staff
    ADD CONSTRAINT branch_staff_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE CASCADE;


--
-- Name: branch_staff branch_staff_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.branch_staff
    ADD CONSTRAINT branch_staff_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: branches branches_vendor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT branches_vendor_id_fkey FOREIGN KEY (vendor_id) REFERENCES public.vendors(id) ON DELETE RESTRICT;


--
-- Name: combos combos_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.combos
    ADD CONSTRAINT combos_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE CASCADE;


--
-- Name: combos combos_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.combos
    ADD CONSTRAINT combos_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: bookings fk_bookings_cancellation_reviewed_by; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT fk_bookings_cancellation_reviewed_by FOREIGN KEY (cancellation_reviewed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: bookings fk_bookings_cancelled_by; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT fk_bookings_cancelled_by FOREIGN KEY (cancelled_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: bookings fk_bookings_checked_in_by; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT fk_bookings_checked_in_by FOREIGN KEY (checked_in_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: bookings fk_bookings_promotion; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT fk_bookings_promotion FOREIGN KEY (promotion_id) REFERENCES public.promotions(id) ON DELETE SET NULL;


--
-- Name: movie_change_requests movie_change_requests_requested_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_change_requests
    ADD CONSTRAINT movie_change_requests_requested_by_id_fkey FOREIGN KEY (requested_by_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: movie_change_requests movie_change_requests_reviewed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_change_requests
    ADD CONSTRAINT movie_change_requests_reviewed_by_id_fkey FOREIGN KEY (reviewed_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: movie_change_requests movie_change_requests_target_movie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_change_requests
    ADD CONSTRAINT movie_change_requests_target_movie_id_fkey FOREIGN KEY (target_movie_id) REFERENCES public.movies(id) ON DELETE SET NULL;


--
-- Name: movie_genre_map movie_genre_map_genre_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_genre_map
    ADD CONSTRAINT movie_genre_map_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES public.movie_genres(id) ON DELETE RESTRICT;


--
-- Name: movie_genre_map movie_genre_map_movie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_genre_map
    ADD CONSTRAINT movie_genre_map_movie_id_fkey FOREIGN KEY (movie_id) REFERENCES public.movies(id) ON DELETE CASCADE;


--
-- Name: movie_reviews movie_reviews_movie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_reviews
    ADD CONSTRAINT movie_reviews_movie_id_fkey FOREIGN KEY (movie_id) REFERENCES public.movies(id) ON DELETE CASCADE;


--
-- Name: movie_reviews movie_reviews_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.movie_reviews
    ADD CONSTRAINT movie_reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: notification_outbox notification_outbox_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.notification_outbox
    ADD CONSTRAINT notification_outbox_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: payment_status_history payment_status_history_payment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.payment_status_history
    ADD CONSTRAINT payment_status_history_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES public.payments(id) ON DELETE CASCADE;


--
-- Name: payments payments_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE RESTRICT;


--
-- Name: payments payments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: pricing_rules pricing_rules_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.pricing_rules
    ADD CONSTRAINT pricing_rules_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE CASCADE;


--
-- Name: promotion_redemptions promotion_redemptions_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.promotion_redemptions
    ADD CONSTRAINT promotion_redemptions_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE CASCADE;


--
-- Name: promotion_redemptions promotion_redemptions_payment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.promotion_redemptions
    ADD CONSTRAINT promotion_redemptions_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES public.payments(id) ON DELETE CASCADE;


--
-- Name: promotion_redemptions promotion_redemptions_promotion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.promotion_redemptions
    ADD CONSTRAINT promotion_redemptions_promotion_id_fkey FOREIGN KEY (promotion_id) REFERENCES public.promotions(id) ON DELETE RESTRICT;


--
-- Name: promotion_redemptions promotion_redemptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.promotion_redemptions
    ADD CONSTRAINT promotion_redemptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: promotions promotions_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.promotions
    ADD CONSTRAINT promotions_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: seat_holds seat_holds_seat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.seat_holds
    ADD CONSTRAINT seat_holds_seat_id_fkey FOREIGN KEY (seat_id) REFERENCES public.seats(id) ON DELETE CASCADE;


--
-- Name: seat_holds seat_holds_showtime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.seat_holds
    ADD CONSTRAINT seat_holds_showtime_id_fkey FOREIGN KEY (showtime_id) REFERENCES public.showtimes(id) ON DELETE CASCADE;


--
-- Name: seat_holds seat_holds_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.seat_holds
    ADD CONSTRAINT seat_holds_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: seats seats_auditorium_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.seats
    ADD CONSTRAINT seats_auditorium_id_fkey FOREIGN KEY (auditorium_id) REFERENCES public.auditoriums(id) ON DELETE CASCADE;


--
-- Name: seats seats_seat_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.seats
    ADD CONSTRAINT seats_seat_type_id_fkey FOREIGN KEY (seat_type_id) REFERENCES public.seat_types(id) ON DELETE RESTRICT;


--
-- Name: showtimes showtimes_auditorium_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.showtimes
    ADD CONSTRAINT showtimes_auditorium_id_fkey FOREIGN KEY (auditorium_id) REFERENCES public.auditoriums(id) ON DELETE RESTRICT;


--
-- Name: showtimes showtimes_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.showtimes
    ADD CONSTRAINT showtimes_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: showtimes showtimes_movie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.showtimes
    ADD CONSTRAINT showtimes_movie_id_fkey FOREIGN KEY (movie_id) REFERENCES public.movies(id) ON DELETE RESTRICT;


--
-- Name: tickets tickets_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE CASCADE;


--
-- Name: tickets tickets_booking_seat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_booking_seat_id_fkey FOREIGN KEY (booking_seat_id) REFERENCES public.booking_seats(id) ON DELETE SET NULL;


--
-- Name: tickets tickets_checked_in_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_checked_in_by_fkey FOREIGN KEY (checked_in_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: tickets tickets_seat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_seat_id_fkey FOREIGN KEY (seat_id) REFERENCES public.seats(id) ON DELETE RESTRICT;


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE RESTRICT;


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ppq_user
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict Vzj0U7fKDvFKgNiQMLJmeqepMmu1eVanITV9kVYyFyS9erJHrpcYx1GUcw30qb9

