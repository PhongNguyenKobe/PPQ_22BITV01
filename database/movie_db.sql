--
-- PostgreSQL database dump
--

\restrict uVlAHh3OP5cH6b0dTc8bcBPE21k5BPHwaXpPYIOEjmNh49cYvmyydXwOYgztsQP

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-07-22 22:53:43

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
-- TOC entry 2 (class 3079 OID 18964)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 5323 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 245 (class 1259 OID 19470)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 19141)
-- Name: auditoriums; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auditoriums (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    branch_id uuid NOT NULL,
    code character varying(30) NOT NULL,
    name character varying(100) NOT NULL,
    total_seats integer NOT NULL,
    screen_type character varying(30),
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT auditoriums_total_seats_check CHECK ((total_seats > 0))
);


ALTER TABLE public.auditoriums OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 19285)
-- Name: booking_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.booking_items (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    booking_id uuid NOT NULL,
    seat_id uuid NOT NULL,
    unit_price numeric(12,2) NOT NULL,
    CONSTRAINT booking_items_unit_price_check CHECK ((unit_price >= (0)::numeric))
);


ALTER TABLE public.booking_items OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 19377)
-- Name: booking_promotions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.booking_promotions (
    booking_id uuid NOT NULL,
    promotion_id uuid NOT NULL,
    applied_amount numeric(12,2) NOT NULL,
    CONSTRAINT booking_promotions_applied_amount_check CHECK ((applied_amount >= (0)::numeric))
);


ALTER TABLE public.booking_promotions OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 19252)
-- Name: bookings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bookings (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    booking_code character varying(30) NOT NULL,
    user_id uuid NOT NULL,
    showtime_id uuid NOT NULL,
    status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    subtotal_amount numeric(12,2) NOT NULL,
    discount_amount numeric(12,2) DEFAULT 0 NOT NULL,
    total_amount numeric(12,2) NOT NULL,
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT bookings_discount_amount_check CHECK ((discount_amount >= (0)::numeric)),
    CONSTRAINT bookings_subtotal_amount_check CHECK ((subtotal_amount >= (0)::numeric)),
    CONSTRAINT bookings_total_amount_check CHECK ((total_amount >= (0)::numeric))
);


ALTER TABLE public.bookings OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 19070)
-- Name: branch_staff; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.branch_staff (
    branch_id uuid NOT NULL,
    user_id uuid NOT NULL,
    staff_role character varying(30) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    assigned_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.branch_staff OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 19045)
-- Name: branches; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.branches OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 19476)
-- Name: movie_change_requests; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.movie_change_requests OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 19124)
-- Name: movie_genre_map; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.movie_genre_map (
    movie_id uuid NOT NULL,
    genre_id smallint NOT NULL
);


ALTER TABLE public.movie_genre_map OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 19093)
-- Name: movie_genres; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.movie_genres (
    id smallint NOT NULL,
    code character varying(40) NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.movie_genres OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 19092)
-- Name: movie_genres_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.movie_genres_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.movie_genres_id_seq OWNER TO postgres;

--
-- TOC entry 5334 (class 0 OID 0)
-- Dependencies: 227
-- Name: movie_genres_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.movie_genres_id_seq OWNED BY public.movie_genres.id;


--
-- TOC entry 229 (class 1259 OID 19106)
-- Name: movies; Type: TABLE; Schema: public; Owner: postgres
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
    CONSTRAINT movies_duration_min_check CHECK ((duration_min > 0))
);


ALTER TABLE public.movies OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 19397)
-- Name: payment_methods; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payment_methods (
    id smallint NOT NULL,
    code character varying(30) NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.payment_methods OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 19396)
-- Name: payment_methods_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payment_methods_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payment_methods_id_seq OWNER TO postgres;

--
-- TOC entry 5338 (class 0 OID 0)
-- Dependencies: 242
-- Name: payment_methods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payment_methods_id_seq OWNED BY public.payment_methods.id;


--
-- TOC entry 244 (class 1259 OID 19408)
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    booking_id uuid NOT NULL,
    method_id smallint NOT NULL,
    provider_txn_id character varying(100),
    amount numeric(12,2) NOT NULL,
    status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    paid_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT payments_amount_check CHECK ((amount >= (0)::numeric))
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 19346)
-- Name: promotions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.promotions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    discount_type character varying(20) NOT NULL,
    discount_value numeric(12,2) NOT NULL,
    max_discount numeric(12,2),
    min_order_amount numeric(12,2),
    starts_at timestamp with time zone NOT NULL,
    ends_at timestamp with time zone NOT NULL,
    vendor_id uuid,
    branch_id uuid,
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT promotions_check CHECK ((ends_at > starts_at)),
    CONSTRAINT promotions_discount_value_check CHECK ((discount_value >= (0)::numeric))
);


ALTER TABLE public.promotions OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 18976)
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id smallint NOT NULL,
    code character varying(30) NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 18975)
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- TOC entry 5343 (class 0 OID 0)
-- Dependencies: 220
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- TOC entry 233 (class 1259 OID 19163)
-- Name: seat_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.seat_types (
    id smallint NOT NULL,
    code character varying(30) NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.seat_types OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 19162)
-- Name: seat_types_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.seat_types_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.seat_types_id_seq OWNER TO postgres;

--
-- TOC entry 5346 (class 0 OID 0)
-- Dependencies: 232
-- Name: seat_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.seat_types_id_seq OWNED BY public.seat_types.id;


--
-- TOC entry 234 (class 1259 OID 19174)
-- Name: seats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.seats (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    auditorium_id uuid NOT NULL,
    seat_row character varying(5) NOT NULL,
    seat_number smallint NOT NULL,
    seat_type_id smallint NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT seats_seat_number_check CHECK ((seat_number > 0))
);


ALTER TABLE public.seats OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 19233)
-- Name: showtime_seat_prices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.showtime_seat_prices (
    showtime_id uuid NOT NULL,
    seat_type_id smallint NOT NULL,
    price numeric(12,2) NOT NULL,
    CONSTRAINT showtime_seat_prices_price_check CHECK ((price >= (0)::numeric))
);


ALTER TABLE public.showtime_seat_prices OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 19200)
-- Name: showtimes; Type: TABLE; Schema: public; Owner: postgres
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
    CONSTRAINT showtimes_base_price_check CHECK ((base_price >= (0)::numeric)),
    CONSTRAINT showtimes_check CHECK ((ends_at > starts_at))
);


ALTER TABLE public.showtimes OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 19308)
-- Name: tickets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tickets (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    booking_item_id uuid NOT NULL,
    showtime_id uuid NOT NULL,
    seat_id uuid NOT NULL,
    ticket_code character varying(50) NOT NULL,
    qr_code_data text,
    status character varying(20) DEFAULT 'ISSUED'::character varying NOT NULL,
    issued_at timestamp with time zone DEFAULT now() NOT NULL,
    used_at timestamp with time zone
);


ALTER TABLE public.tickets OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 19009)
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles (
    user_id uuid NOT NULL,
    role_id smallint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 18987)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
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
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 19028)
-- Name: vendors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vendors (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.vendors OWNER TO postgres;

--
-- TOC entry 4974 (class 2604 OID 19096)
-- Name: movie_genres id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie_genres ALTER COLUMN id SET DEFAULT nextval('public.movie_genres_id_seq'::regclass);


--
-- TOC entry 4997 (class 2604 OID 19400)
-- Name: payment_methods id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_methods ALTER COLUMN id SET DEFAULT nextval('public.payment_methods_id_seq'::regclass);


--
-- TOC entry 4960 (class 2604 OID 18979)
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- TOC entry 4981 (class 2604 OID 19166)
-- Name: seat_types id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seat_types ALTER COLUMN id SET DEFAULT nextval('public.seat_types_id_seq'::regclass);


--
-- TOC entry 5109 (class 2606 OID 19475)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 5053 (class 2606 OID 19156)
-- Name: auditoriums auditoriums_branch_id_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoriums
    ADD CONSTRAINT auditoriums_branch_id_code_key UNIQUE (branch_id, code);


--
-- TOC entry 5055 (class 2606 OID 19154)
-- Name: auditoriums auditoriums_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoriums
    ADD CONSTRAINT auditoriums_pkey PRIMARY KEY (id);


--
-- TOC entry 5079 (class 2606 OID 19297)
-- Name: booking_items booking_items_booking_id_seat_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.booking_items
    ADD CONSTRAINT booking_items_booking_id_seat_id_key UNIQUE (booking_id, seat_id);


--
-- TOC entry 5081 (class 2606 OID 19295)
-- Name: booking_items booking_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.booking_items
    ADD CONSTRAINT booking_items_pkey PRIMARY KEY (id);


--
-- TOC entry 5098 (class 2606 OID 19385)
-- Name: booking_promotions booking_promotions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.booking_promotions
    ADD CONSTRAINT booking_promotions_pkey PRIMARY KEY (booking_id, promotion_id);


--
-- TOC entry 5073 (class 2606 OID 19274)
-- Name: bookings bookings_booking_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_booking_code_key UNIQUE (booking_code);


--
-- TOC entry 5075 (class 2606 OID 19272)
-- Name: bookings bookings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_pkey PRIMARY KEY (id);


--
-- TOC entry 5041 (class 2606 OID 19081)
-- Name: branch_staff branch_staff_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branch_staff
    ADD CONSTRAINT branch_staff_pkey PRIMARY KEY (branch_id, user_id);


--
-- TOC entry 5036 (class 2606 OID 19064)
-- Name: branches branches_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT branches_code_key UNIQUE (code);


--
-- TOC entry 5038 (class 2606 OID 19062)
-- Name: branches branches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT branches_pkey PRIMARY KEY (id);


--
-- TOC entry 5111 (class 2606 OID 19491)
-- Name: movie_change_requests movie_change_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie_change_requests
    ADD CONSTRAINT movie_change_requests_pkey PRIMARY KEY (id);


--
-- TOC entry 5051 (class 2606 OID 19130)
-- Name: movie_genre_map movie_genre_map_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie_genre_map
    ADD CONSTRAINT movie_genre_map_pkey PRIMARY KEY (movie_id, genre_id);


--
-- TOC entry 5043 (class 2606 OID 19103)
-- Name: movie_genres movie_genres_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie_genres
    ADD CONSTRAINT movie_genres_code_key UNIQUE (code);


--
-- TOC entry 5045 (class 2606 OID 19105)
-- Name: movie_genres movie_genres_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie_genres
    ADD CONSTRAINT movie_genres_name_key UNIQUE (name);


--
-- TOC entry 5047 (class 2606 OID 19101)
-- Name: movie_genres movie_genres_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie_genres
    ADD CONSTRAINT movie_genres_pkey PRIMARY KEY (id);


--
-- TOC entry 5049 (class 2606 OID 19123)
-- Name: movies movies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movies
    ADD CONSTRAINT movies_pkey PRIMARY KEY (id);


--
-- TOC entry 5100 (class 2606 OID 19407)
-- Name: payment_methods payment_methods_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_methods
    ADD CONSTRAINT payment_methods_code_key UNIQUE (code);


--
-- TOC entry 5102 (class 2606 OID 19405)
-- Name: payment_methods payment_methods_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_methods
    ADD CONSTRAINT payment_methods_pkey PRIMARY KEY (id);


--
-- TOC entry 5105 (class 2606 OID 19422)
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- TOC entry 5107 (class 2606 OID 19424)
-- Name: payments payments_provider_txn_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_provider_txn_id_key UNIQUE (provider_txn_id);


--
-- TOC entry 5094 (class 2606 OID 19366)
-- Name: promotions promotions_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.promotions
    ADD CONSTRAINT promotions_code_key UNIQUE (code);


--
-- TOC entry 5096 (class 2606 OID 19364)
-- Name: promotions promotions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.promotions
    ADD CONSTRAINT promotions_pkey PRIMARY KEY (id);


--
-- TOC entry 5019 (class 2606 OID 18986)
-- Name: roles roles_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_code_key UNIQUE (code);


--
-- TOC entry 5021 (class 2606 OID 18984)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- TOC entry 5058 (class 2606 OID 19173)
-- Name: seat_types seat_types_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seat_types
    ADD CONSTRAINT seat_types_code_key UNIQUE (code);


--
-- TOC entry 5060 (class 2606 OID 19171)
-- Name: seat_types seat_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seat_types
    ADD CONSTRAINT seat_types_pkey PRIMARY KEY (id);


--
-- TOC entry 5063 (class 2606 OID 19189)
-- Name: seats seats_auditorium_id_seat_row_seat_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seats
    ADD CONSTRAINT seats_auditorium_id_seat_row_seat_number_key UNIQUE (auditorium_id, seat_row, seat_number);


--
-- TOC entry 5065 (class 2606 OID 19187)
-- Name: seats seats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seats
    ADD CONSTRAINT seats_pkey PRIMARY KEY (id);


--
-- TOC entry 5071 (class 2606 OID 19241)
-- Name: showtime_seat_prices showtime_seat_prices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.showtime_seat_prices
    ADD CONSTRAINT showtime_seat_prices_pkey PRIMARY KEY (showtime_id, seat_type_id);


--
-- TOC entry 5069 (class 2606 OID 19217)
-- Name: showtimes showtimes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.showtimes
    ADD CONSTRAINT showtimes_pkey PRIMARY KEY (id);


--
-- TOC entry 5085 (class 2606 OID 19326)
-- Name: tickets tickets_booking_item_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_booking_item_id_key UNIQUE (booking_item_id);


--
-- TOC entry 5087 (class 2606 OID 19324)
-- Name: tickets tickets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_pkey PRIMARY KEY (id);


--
-- TOC entry 5089 (class 2606 OID 19330)
-- Name: tickets tickets_showtime_id_seat_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_showtime_id_seat_id_key UNIQUE (showtime_id, seat_id);


--
-- TOC entry 5091 (class 2606 OID 19328)
-- Name: tickets tickets_ticket_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_ticket_code_key UNIQUE (ticket_code);


--
-- TOC entry 5030 (class 2606 OID 19017)
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (user_id, role_id);


--
-- TOC entry 5024 (class 2606 OID 19006)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 5026 (class 2606 OID 19008)
-- Name: users users_phone_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_phone_key UNIQUE (phone);


--
-- TOC entry 5028 (class 2606 OID 19004)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 5032 (class 2606 OID 19044)
-- Name: vendors vendors_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT vendors_code_key UNIQUE (code);


--
-- TOC entry 5034 (class 2606 OID 19042)
-- Name: vendors vendors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT vendors_pkey PRIMARY KEY (id);


--
-- TOC entry 5056 (class 1259 OID 19437)
-- Name: idx_auditoriums_branch; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoriums_branch ON public.auditoriums USING btree (branch_id);


--
-- TOC entry 5082 (class 1259 OID 19443)
-- Name: idx_booking_items_booking; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_booking_items_booking ON public.booking_items USING btree (booking_id);


--
-- TOC entry 5076 (class 1259 OID 19442)
-- Name: idx_bookings_showtime; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bookings_showtime ON public.bookings USING btree (showtime_id);


--
-- TOC entry 5077 (class 1259 OID 19441)
-- Name: idx_bookings_user_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bookings_user_created ON public.bookings USING btree (user_id, created_at DESC);


--
-- TOC entry 5039 (class 1259 OID 19436)
-- Name: idx_branches_vendor; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_branches_vendor ON public.branches USING btree (vendor_id);


--
-- TOC entry 5103 (class 1259 OID 19445)
-- Name: idx_payments_booking_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_payments_booking_status ON public.payments USING btree (booking_id, status);


--
-- TOC entry 5092 (class 1259 OID 19446)
-- Name: idx_promotions_active_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_promotions_active_time ON public.promotions USING btree (is_active, starts_at, ends_at);


--
-- TOC entry 5061 (class 1259 OID 19438)
-- Name: idx_seats_auditorium; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_seats_auditorium ON public.seats USING btree (auditorium_id);


--
-- TOC entry 5066 (class 1259 OID 19440)
-- Name: idx_showtimes_auditorium_start; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_showtimes_auditorium_start ON public.showtimes USING btree (auditorium_id, starts_at);


--
-- TOC entry 5067 (class 1259 OID 19439)
-- Name: idx_showtimes_movie_start; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_showtimes_movie_start ON public.showtimes USING btree (movie_id, starts_at);


--
-- TOC entry 5083 (class 1259 OID 19444)
-- Name: idx_tickets_showtime_seat; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tickets_showtime_seat ON public.tickets USING btree (showtime_id, seat_id);


--
-- TOC entry 5022 (class 1259 OID 19435)
-- Name: idx_users_email_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_email_active ON public.users USING btree (email, is_active);


--
-- TOC entry 5119 (class 2606 OID 19157)
-- Name: auditoriums auditoriums_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoriums
    ADD CONSTRAINT auditoriums_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE CASCADE;


--
-- TOC entry 5129 (class 2606 OID 19298)
-- Name: booking_items booking_items_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.booking_items
    ADD CONSTRAINT booking_items_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE CASCADE;


--
-- TOC entry 5130 (class 2606 OID 19303)
-- Name: booking_items booking_items_seat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.booking_items
    ADD CONSTRAINT booking_items_seat_id_fkey FOREIGN KEY (seat_id) REFERENCES public.seats(id) ON DELETE RESTRICT;


--
-- TOC entry 5136 (class 2606 OID 19386)
-- Name: booking_promotions booking_promotions_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.booking_promotions
    ADD CONSTRAINT booking_promotions_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE CASCADE;


--
-- TOC entry 5137 (class 2606 OID 19391)
-- Name: booking_promotions booking_promotions_promotion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.booking_promotions
    ADD CONSTRAINT booking_promotions_promotion_id_fkey FOREIGN KEY (promotion_id) REFERENCES public.promotions(id) ON DELETE RESTRICT;


--
-- TOC entry 5127 (class 2606 OID 19280)
-- Name: bookings bookings_showtime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_showtime_id_fkey FOREIGN KEY (showtime_id) REFERENCES public.showtimes(id) ON DELETE RESTRICT;


--
-- TOC entry 5128 (class 2606 OID 19275)
-- Name: bookings bookings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- TOC entry 5115 (class 2606 OID 19082)
-- Name: branch_staff branch_staff_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branch_staff
    ADD CONSTRAINT branch_staff_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE CASCADE;


--
-- TOC entry 5116 (class 2606 OID 19087)
-- Name: branch_staff branch_staff_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branch_staff
    ADD CONSTRAINT branch_staff_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 5114 (class 2606 OID 19065)
-- Name: branches branches_vendor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT branches_vendor_id_fkey FOREIGN KEY (vendor_id) REFERENCES public.vendors(id) ON DELETE RESTRICT;


--
-- TOC entry 5140 (class 2606 OID 19492)
-- Name: movie_change_requests movie_change_requests_requested_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie_change_requests
    ADD CONSTRAINT movie_change_requests_requested_by_id_fkey FOREIGN KEY (requested_by_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 5141 (class 2606 OID 19502)
-- Name: movie_change_requests movie_change_requests_reviewed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie_change_requests
    ADD CONSTRAINT movie_change_requests_reviewed_by_id_fkey FOREIGN KEY (reviewed_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 5142 (class 2606 OID 19497)
-- Name: movie_change_requests movie_change_requests_target_movie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie_change_requests
    ADD CONSTRAINT movie_change_requests_target_movie_id_fkey FOREIGN KEY (target_movie_id) REFERENCES public.movies(id) ON DELETE SET NULL;


--
-- TOC entry 5117 (class 2606 OID 19136)
-- Name: movie_genre_map movie_genre_map_genre_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie_genre_map
    ADD CONSTRAINT movie_genre_map_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES public.movie_genres(id) ON DELETE RESTRICT;


--
-- TOC entry 5118 (class 2606 OID 19131)
-- Name: movie_genre_map movie_genre_map_movie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie_genre_map
    ADD CONSTRAINT movie_genre_map_movie_id_fkey FOREIGN KEY (movie_id) REFERENCES public.movies(id) ON DELETE CASCADE;


--
-- TOC entry 5138 (class 2606 OID 19425)
-- Name: payments payments_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE RESTRICT;


--
-- TOC entry 5139 (class 2606 OID 19430)
-- Name: payments payments_method_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_method_id_fkey FOREIGN KEY (method_id) REFERENCES public.payment_methods(id) ON DELETE RESTRICT;


--
-- TOC entry 5134 (class 2606 OID 19372)
-- Name: promotions promotions_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.promotions
    ADD CONSTRAINT promotions_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE SET NULL;


--
-- TOC entry 5135 (class 2606 OID 19367)
-- Name: promotions promotions_vendor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.promotions
    ADD CONSTRAINT promotions_vendor_id_fkey FOREIGN KEY (vendor_id) REFERENCES public.vendors(id) ON DELETE SET NULL;


--
-- TOC entry 5120 (class 2606 OID 19190)
-- Name: seats seats_auditorium_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seats
    ADD CONSTRAINT seats_auditorium_id_fkey FOREIGN KEY (auditorium_id) REFERENCES public.auditoriums(id) ON DELETE CASCADE;


--
-- TOC entry 5121 (class 2606 OID 19195)
-- Name: seats seats_seat_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seats
    ADD CONSTRAINT seats_seat_type_id_fkey FOREIGN KEY (seat_type_id) REFERENCES public.seat_types(id) ON DELETE RESTRICT;


--
-- TOC entry 5125 (class 2606 OID 19247)
-- Name: showtime_seat_prices showtime_seat_prices_seat_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.showtime_seat_prices
    ADD CONSTRAINT showtime_seat_prices_seat_type_id_fkey FOREIGN KEY (seat_type_id) REFERENCES public.seat_types(id) ON DELETE RESTRICT;


--
-- TOC entry 5126 (class 2606 OID 19242)
-- Name: showtime_seat_prices showtime_seat_prices_showtime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.showtime_seat_prices
    ADD CONSTRAINT showtime_seat_prices_showtime_id_fkey FOREIGN KEY (showtime_id) REFERENCES public.showtimes(id) ON DELETE CASCADE;


--
-- TOC entry 5122 (class 2606 OID 19223)
-- Name: showtimes showtimes_auditorium_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.showtimes
    ADD CONSTRAINT showtimes_auditorium_id_fkey FOREIGN KEY (auditorium_id) REFERENCES public.auditoriums(id) ON DELETE RESTRICT;


--
-- TOC entry 5123 (class 2606 OID 19228)
-- Name: showtimes showtimes_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.showtimes
    ADD CONSTRAINT showtimes_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 5124 (class 2606 OID 19218)
-- Name: showtimes showtimes_movie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.showtimes
    ADD CONSTRAINT showtimes_movie_id_fkey FOREIGN KEY (movie_id) REFERENCES public.movies(id) ON DELETE RESTRICT;


--
-- TOC entry 5131 (class 2606 OID 19331)
-- Name: tickets tickets_booking_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_booking_item_id_fkey FOREIGN KEY (booking_item_id) REFERENCES public.booking_items(id) ON DELETE CASCADE;


--
-- TOC entry 5132 (class 2606 OID 19341)
-- Name: tickets tickets_seat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_seat_id_fkey FOREIGN KEY (seat_id) REFERENCES public.seats(id) ON DELETE RESTRICT;


--
-- TOC entry 5133 (class 2606 OID 19336)
-- Name: tickets tickets_showtime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_showtime_id_fkey FOREIGN KEY (showtime_id) REFERENCES public.showtimes(id) ON DELETE RESTRICT;


--
-- TOC entry 5112 (class 2606 OID 19023)
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE RESTRICT;


--
-- TOC entry 5113 (class 2606 OID 19018)
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 5322 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO app_rw;
GRANT USAGE ON SCHEMA public TO app_ro;
GRANT USAGE ON SCHEMA public TO dba_admin;


--
-- TOC entry 5324 (class 0 OID 0)
-- Dependencies: 245
-- Name: TABLE alembic_version; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.alembic_version TO app_rw;
GRANT SELECT ON TABLE public.alembic_version TO app_ro;
GRANT ALL ON TABLE public.alembic_version TO dba_admin;


--
-- TOC entry 5325 (class 0 OID 0)
-- Dependencies: 231
-- Name: TABLE auditoriums; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.auditoriums TO app_rw;
GRANT SELECT ON TABLE public.auditoriums TO app_ro;
GRANT ALL ON TABLE public.auditoriums TO dba_admin;


--
-- TOC entry 5326 (class 0 OID 0)
-- Dependencies: 238
-- Name: TABLE booking_items; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.booking_items TO app_rw;
GRANT SELECT ON TABLE public.booking_items TO app_ro;
GRANT ALL ON TABLE public.booking_items TO dba_admin;


--
-- TOC entry 5327 (class 0 OID 0)
-- Dependencies: 241
-- Name: TABLE booking_promotions; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.booking_promotions TO app_rw;
GRANT SELECT ON TABLE public.booking_promotions TO app_ro;
GRANT ALL ON TABLE public.booking_promotions TO dba_admin;


--
-- TOC entry 5328 (class 0 OID 0)
-- Dependencies: 237
-- Name: TABLE bookings; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.bookings TO app_rw;
GRANT SELECT ON TABLE public.bookings TO app_ro;
GRANT ALL ON TABLE public.bookings TO dba_admin;


--
-- TOC entry 5329 (class 0 OID 0)
-- Dependencies: 226
-- Name: TABLE branch_staff; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.branch_staff TO app_rw;
GRANT SELECT ON TABLE public.branch_staff TO app_ro;
GRANT ALL ON TABLE public.branch_staff TO dba_admin;


--
-- TOC entry 5330 (class 0 OID 0)
-- Dependencies: 225
-- Name: TABLE branches; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.branches TO app_rw;
GRANT SELECT ON TABLE public.branches TO app_ro;
GRANT ALL ON TABLE public.branches TO dba_admin;


--
-- TOC entry 5331 (class 0 OID 0)
-- Dependencies: 246
-- Name: TABLE movie_change_requests; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.movie_change_requests TO app_rw;
GRANT SELECT ON TABLE public.movie_change_requests TO app_ro;
GRANT ALL ON TABLE public.movie_change_requests TO dba_admin;


--
-- TOC entry 5332 (class 0 OID 0)
-- Dependencies: 230
-- Name: TABLE movie_genre_map; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.movie_genre_map TO app_rw;
GRANT SELECT ON TABLE public.movie_genre_map TO app_ro;
GRANT ALL ON TABLE public.movie_genre_map TO dba_admin;


--
-- TOC entry 5333 (class 0 OID 0)
-- Dependencies: 228
-- Name: TABLE movie_genres; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.movie_genres TO app_rw;
GRANT SELECT ON TABLE public.movie_genres TO app_ro;
GRANT ALL ON TABLE public.movie_genres TO dba_admin;


--
-- TOC entry 5335 (class 0 OID 0)
-- Dependencies: 227
-- Name: SEQUENCE movie_genres_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.movie_genres_id_seq TO dba_admin;


--
-- TOC entry 5336 (class 0 OID 0)
-- Dependencies: 229
-- Name: TABLE movies; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.movies TO app_rw;
GRANT SELECT ON TABLE public.movies TO app_ro;
GRANT ALL ON TABLE public.movies TO dba_admin;


--
-- TOC entry 5337 (class 0 OID 0)
-- Dependencies: 243
-- Name: TABLE payment_methods; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.payment_methods TO app_rw;
GRANT SELECT ON TABLE public.payment_methods TO app_ro;
GRANT ALL ON TABLE public.payment_methods TO dba_admin;


--
-- TOC entry 5339 (class 0 OID 0)
-- Dependencies: 242
-- Name: SEQUENCE payment_methods_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.payment_methods_id_seq TO dba_admin;


--
-- TOC entry 5340 (class 0 OID 0)
-- Dependencies: 244
-- Name: TABLE payments; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.payments TO app_rw;
GRANT SELECT ON TABLE public.payments TO app_ro;
GRANT ALL ON TABLE public.payments TO dba_admin;


--
-- TOC entry 5341 (class 0 OID 0)
-- Dependencies: 240
-- Name: TABLE promotions; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.promotions TO app_rw;
GRANT SELECT ON TABLE public.promotions TO app_ro;
GRANT ALL ON TABLE public.promotions TO dba_admin;


--
-- TOC entry 5342 (class 0 OID 0)
-- Dependencies: 221
-- Name: TABLE roles; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.roles TO app_rw;
GRANT SELECT ON TABLE public.roles TO app_ro;
GRANT ALL ON TABLE public.roles TO dba_admin;


--
-- TOC entry 5344 (class 0 OID 0)
-- Dependencies: 220
-- Name: SEQUENCE roles_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.roles_id_seq TO dba_admin;


--
-- TOC entry 5345 (class 0 OID 0)
-- Dependencies: 233
-- Name: TABLE seat_types; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.seat_types TO app_rw;
GRANT SELECT ON TABLE public.seat_types TO app_ro;
GRANT ALL ON TABLE public.seat_types TO dba_admin;


--
-- TOC entry 5347 (class 0 OID 0)
-- Dependencies: 232
-- Name: SEQUENCE seat_types_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.seat_types_id_seq TO dba_admin;


--
-- TOC entry 5348 (class 0 OID 0)
-- Dependencies: 234
-- Name: TABLE seats; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.seats TO app_rw;
GRANT SELECT ON TABLE public.seats TO app_ro;
GRANT ALL ON TABLE public.seats TO dba_admin;


--
-- TOC entry 5349 (class 0 OID 0)
-- Dependencies: 236
-- Name: TABLE showtime_seat_prices; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.showtime_seat_prices TO app_rw;
GRANT SELECT ON TABLE public.showtime_seat_prices TO app_ro;
GRANT ALL ON TABLE public.showtime_seat_prices TO dba_admin;


--
-- TOC entry 5350 (class 0 OID 0)
-- Dependencies: 235
-- Name: TABLE showtimes; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.showtimes TO app_rw;
GRANT SELECT ON TABLE public.showtimes TO app_ro;
GRANT ALL ON TABLE public.showtimes TO dba_admin;


--
-- TOC entry 5351 (class 0 OID 0)
-- Dependencies: 239
-- Name: TABLE tickets; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.tickets TO app_rw;
GRANT SELECT ON TABLE public.tickets TO app_ro;
GRANT ALL ON TABLE public.tickets TO dba_admin;


--
-- TOC entry 5352 (class 0 OID 0)
-- Dependencies: 223
-- Name: TABLE user_roles; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.user_roles TO app_rw;
GRANT SELECT ON TABLE public.user_roles TO app_ro;
GRANT ALL ON TABLE public.user_roles TO dba_admin;


--
-- TOC entry 5353 (class 0 OID 0)
-- Dependencies: 222
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.users TO app_rw;
GRANT SELECT ON TABLE public.users TO app_ro;
GRANT ALL ON TABLE public.users TO dba_admin;


--
-- TOC entry 5354 (class 0 OID 0)
-- Dependencies: 224
-- Name: TABLE vendors; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.vendors TO app_rw;
GRANT SELECT ON TABLE public.vendors TO app_ro;
GRANT ALL ON TABLE public.vendors TO dba_admin;


--
-- TOC entry 2155 (class 826 OID 19455)
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO dba_admin;


--
-- TOC entry 2154 (class 826 OID 19454)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO app_rw;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO app_ro;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO dba_admin;


-- Completed on 2026-07-22 22:53:44

--
-- PostgreSQL database dump complete
--

\unrestrict uVlAHh3OP5cH6b0dTc8bcBPE21k5BPHwaXpPYIOEjmNh49cYvmyydXwOYgztsQP

