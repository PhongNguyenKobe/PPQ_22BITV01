BEGIN;

-- Roles
INSERT INTO roles (code, name) VALUES
('SUPER_ADMIN', 'Website Super Admin'),
('BRANCH_ADMIN', 'Branch Admin'),
('CUSTOMER', 'Customer'),
('STAFF', 'Branch Staff')
ON CONFLICT (code) DO NOTHING;

-- Users
INSERT INTO users (id, email, phone, password_hash, full_name, date_of_birth, gender, is_active)
VALUES
('11111111-1111-1111-1111-111111111111', 'superadmin@cinema.vn', '0900000001', 'hashed_pw_demo_1', 'Super Admin', '1990-01-01', 'male', TRUE),
('22222222-2222-2222-2222-222222222222', 'branchadmin.hcm@cinema.vn', '0900000002', 'hashed_pw_demo_2', 'Branch Admin HCM', '1992-02-02', 'female', TRUE),
('33333333-3333-3333-3333-333333333333', 'staff.hcm@cinema.vn', '0900000003', 'hashed_pw_demo_3', 'Staff HCM', '1998-03-03', 'male', TRUE),
('44444444-4444-4444-4444-444444444444', 'customer1@gmail.com', '0900000004', 'hashed_pw_demo_4', 'Nguyen Van A', '2000-04-04', 'male', TRUE),
('55555555-5555-5555-5555-555555555555', 'customer2@gmail.com', '0900000005', 'hashed_pw_demo_5', 'Tran Thi B', '2001-05-05', 'female', TRUE)
ON CONFLICT (email) DO NOTHING;

INSERT INTO user_roles (user_id, role_id)
SELECT '11111111-1111-1111-1111-111111111111', id FROM roles WHERE code = 'SUPER_ADMIN'
ON CONFLICT DO NOTHING;
INSERT INTO user_roles (user_id, role_id)
SELECT '22222222-2222-2222-2222-222222222222', id FROM roles WHERE code = 'BRANCH_ADMIN'
ON CONFLICT DO NOTHING;
INSERT INTO user_roles (user_id, role_id)
SELECT '33333333-3333-3333-3333-333333333333', id FROM roles WHERE code = 'STAFF'
ON CONFLICT DO NOTHING;
INSERT INTO user_roles (user_id, role_id)
SELECT '44444444-4444-4444-4444-444444444444', id FROM roles WHERE code = 'CUSTOMER'
ON CONFLICT DO NOTHING;
INSERT INTO user_roles (user_id, role_id)
SELECT '55555555-5555-5555-5555-555555555555', id FROM roles WHERE code = 'CUSTOMER'
ON CONFLICT DO NOTHING;

-- Vendors / Branches
INSERT INTO vendors (id, code, name, description, is_active)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'CGV_GROUP', 'CGV Demo Group', 'Demo cinema vendor', TRUE),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'BETA_GROUP', 'Beta Demo Group', 'Second demo vendor', TRUE)
ON CONFLICT (code) DO NOTHING;

INSERT INTO branches (id, vendor_id, code, name, address_line, city, district, latitude, longitude, phone, is_active)
VALUES
('aaaabbbb-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'CGV_HCM_Q1', 'CGV Quận 1', '123 Lê Lợi', 'HCM', 'Quận 1', 10.7765300, 106.7009800, '0281111111', TRUE),
('aaaacccc-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'CGV_HCM_Q7', 'CGV Quận 7', '456 Nguyễn Hữu Thọ', 'HCM', 'Quận 7', 10.7294700, 106.7219100, '0282222222', TRUE),
('bbbbcccc-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'BETA_HN_CG', 'Beta Cầu Giấy', '789 Trần Duy Hưng', 'Hà Nội', 'Cầu Giấy', 21.0122300, 105.8059300, '0243333333', TRUE)
ON CONFLICT (code) DO NOTHING;

INSERT INTO branch_staff (branch_id, user_id, staff_role, is_active)
VALUES
('aaaabbbb-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '22222222-2222-2222-2222-222222222222', 'BRANCH_ADMIN', TRUE),
('aaaabbbb-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '33333333-3333-3333-3333-333333333333', 'STAFF', TRUE)
ON CONFLICT (branch_id, user_id) DO NOTHING;

-- Genres / Movies
INSERT INTO movie_genres (code, name) VALUES
('ACTION', 'Hành động'),
('ROMANCE', 'Tình cảm'),
('COMEDY', 'Hài'),
('HORROR', 'Kinh dị'),
('SCI_FI', 'Khoa học viễn tưởng'),
('ANIMATION', 'Hoạt hình')
ON CONFLICT (code) DO NOTHING;

INSERT INTO movies (id, title, original_title, description, duration_min, release_date, age_rating, language, trailer_url, poster_url, status)
VALUES
('a1111111-1111-1111-1111-111111111111', 'Avengers: Demo War', 'Avengers: Demo War', 'Biệt đội siêu anh hùng tái hợp.', 140, '2024-12-20', 'T13', 'English', 'https://youtube.com/watch?v=demo1', 'https://picsum.photos/300/450?1', 'NOW_SHOWING'),
('a2222222-2222-2222-2222-222222222222', 'Love In Saigon', 'Love In Saigon', 'Chuyện tình nơi đô thị hiện đại.', 115, '2025-01-15', 'P', 'Vietnamese', 'https://youtube.com/watch?v=demo2', 'https://picsum.photos/300/450?2', 'NOW_SHOWING'),
('a3333333-3333-3333-3333-333333333333', 'Ghost Apartment', 'Ghost Apartment', 'Bí ẩn trong khu chung cư cũ.', 105, '2025-02-01', 'T16', 'Vietnamese', 'https://youtube.com/watch?v=demo3', 'https://picsum.photos/300/450?3', 'UPCOMING')
ON CONFLICT DO NOTHING;

INSERT INTO movie_genre_map (movie_id, genre_id)
SELECT 'a1111111-1111-1111-1111-111111111111', id FROM movie_genres WHERE code IN ('ACTION','SCI_FI')
ON CONFLICT DO NOTHING;
INSERT INTO movie_genre_map (movie_id, genre_id)
SELECT 'a2222222-2222-2222-2222-222222222222', id FROM movie_genres WHERE code IN ('ROMANCE','COMEDY')
ON CONFLICT DO NOTHING;
INSERT INTO movie_genre_map (movie_id, genre_id)
SELECT 'a3333333-3333-3333-3333-333333333333', id FROM movie_genres WHERE code IN ('HORROR')
ON CONFLICT DO NOTHING;

COMMIT;