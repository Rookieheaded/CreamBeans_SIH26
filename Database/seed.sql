-- ============================================================================
-- CREAM BEANS — SIH 2026 Campus Lost & Found Intelligence System
-- Deterministic Seed Dataset
-- Person 6: Database & Data-Integration Engineer
-- ============================================================================

-- Clean existing data safely (only truncates if tables already exist)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'claims') THEN
        TRUNCATE TABLE claims CASCADE;
    END IF;
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'matches') THEN
        TRUNCATE TABLE matches CASCADE;
    END IF;
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'items') THEN
        TRUNCATE TABLE items CASCADE;
    END IF;
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        TRUNCATE TABLE users CASCADE;
    END IF;
END $$;

-- Fixed UUIDs for deterministic testing
-- USERS (User 5 is designated Admin / Security Office)
INSERT INTO users (id, name, email, phone, is_admin, created_at) VALUES
('11111111-1111-4111-a111-111111111111', 'Rahul Sharma', 'rahul.cs24@nitk.edu.in', '+91-9876543210', false, '2026-08-01T10:00:00Z'),
('22222222-2222-4222-a222-222222222222', 'Ananya Patel', 'ananya.ee23@nitk.edu.in', '+91-9876543211', false, '2026-08-02T11:00:00Z'),
('33333333-3333-4333-a333-333333333333', 'Vikram Rao', 'vikram.mech22@nitk.edu.in', '+91-9876543212', false, '2026-08-03T12:00:00Z'),
('44444444-4444-4444-a444-444444444444', 'Priya Nair', 'priya.ec24@nitk.edu.in', '+91-9876543213', false, '2026-08-04T13:00:00Z'),
('55555555-5555-4555-a555-555555555555', 'NITK Security Office', 'security.office@nitk.edu.in', '+91-8242474000', true, '2026-08-05T09:00:00Z');

-- ============================================================================
-- FOUND ITEMS (20 ITEMS)
-- ============================================================================

-- 1. Black Lenovo backpack (Strongest match for LOST-01)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000001', '55555555-5555-4555-a555-555555555555', 'found', 'Backpacks', 'Black Lenovo backpack with padded laptop compartment and red zipper accent', 'https://storage.supabase.co/item-images/found_lenovo_bag.jpg', 'Central Library 2nd Floor', 13.0102, 74.7943, '2026-08-28T14:30:00Z', 'active', '2026-08-28T14:35:00Z');

-- 2. Dark laptop bag (Near-duplicate candidate 2 for LOST-01)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000002', '22222222-2222-4222-a222-222222222222', 'found', 'Backpacks', 'Dark grey laptop bag found on chair in CS lab', 'https://storage.supabase.co/item-images/found_dark_laptop_bag.jpg', 'Dept of Computer Science Room 201', 13.0108, 74.7951, '2026-08-28T16:00:00Z', 'active', '2026-08-28T16:10:00Z');

-- 3. Blue Nike backpack (Distractor for LOST-01)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000003', '33333333-3333-4333-a333-333333333333', 'found', 'Backpacks', 'Blue Nike sports backpack with water bottle side pocket', 'https://storage.supabase.co/item-images/found_blue_nike.jpg', 'Main Canteen Area', 13.0095, 74.7938, '2026-08-27T12:15:00Z', 'active', '2026-08-27T12:30:00Z');

-- 4. Silver MacBook Air 13-inch (Strongest match for LOST-02)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000004', '55555555-5555-4555-a555-555555555555', 'found', 'Laptops', 'Silver Apple MacBook Air 13-inch M2 with anime sticker on lid', 'https://storage.supabase.co/item-images/found_macbook_air.jpg', 'LHC Lecture Hall 3', 13.0112, 74.7960, '2026-08-29T10:00:00Z', 'active', '2026-08-29T10:05:00Z');

-- 5. Dell Black 15-inch Laptop (Distractor for LOST-02)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000005', '11111111-1111-4111-a111-111111111111', 'found', 'Laptops', 'Black Dell Inspiron 15-inch laptop left near charger point', 'https://storage.supabase.co/item-images/found_dell_laptop.jpg', 'Central Library Ground Floor', 13.0101, 74.7942, '2026-08-28T11:30:00Z', 'active', '2026-08-28T11:45:00Z');

-- 6. Brown Leather Wallet (Strongest match for LOST-03)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000006', '44444444-4444-4444-a444-444444444444', 'found', 'Wallets', 'Brown leather bi-fold wallet containing SBI debit card and driving license', 'https://storage.supabase.co/item-images/found_brown_wallet.jpg', 'SAC Sports Complex Quadrangle', 13.0080, 74.7925, '2026-08-29T17:45:00Z', 'active', '2026-08-29T17:50:00Z');

-- 7. Black Slim Leather Card Holder (Distractor for LOST-03)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000007', '22222222-2222-4222-a222-222222222222', 'found', 'Wallets', 'Black slim minimalist card holder with 3 credit cards', 'https://storage.supabase.co/item-images/found_black_cardholder.jpg', 'Main Canteen Cash Counter', 13.0096, 74.7939, '2026-08-27T13:00:00Z', 'active', '2026-08-27T13:10:00Z');

-- 8. iPhone 13 Pro Graphite (Strongest match for LOST-04)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000008', '44444444-4444-4444-a444-444444444444', 'found', 'Phones', 'Graphite Apple iPhone 13 Pro with clear silicone case', 'https://storage.supabase.co/item-images/found_iphone13.jpg', 'Department of Electronics Lab 2', 13.0105, 74.7955, '2026-08-29T15:20:00Z', 'active', '2026-08-29T15:25:00Z');

-- 9. Samsung Galaxy A54 Blue (Distractor for LOST-04)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000009', '33333333-3333-4333-a333-333333333333', 'found', 'Phones', 'Awesome Blue Samsung Galaxy A54 smartphone with black bumper case', 'https://storage.supabase.co/item-images/found_samsung_a54.jpg', 'Mega Tower Hostel Block 7 Common Room', 13.0125, 74.7970, '2026-08-28T20:10:00Z', 'active', '2026-08-28T20:20:00Z');

-- 10. Sony WH-1000XM4 Black Headphones (Strongest match for LOST-05)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000010', '11111111-1111-4111-a111-111111111111', 'found', 'Headphones', 'Black Sony WH-1000XM4 wireless over-ear noise cancelling headphones in black zip case', 'https://storage.supabase.co/item-images/found_sony_headphones.jpg', 'Central Library Reading Room', 13.0103, 74.7944, '2026-08-29T09:15:00Z', 'active', '2026-08-29T09:20:00Z');

-- 11. White Apple AirPods Pro 2 (Distractor for LOST-05)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000011', '22222222-2222-4222-a222-222222222222', 'found', 'Headphones', 'White Apple AirPods Pro 2 in wireless charging case with lanyard loop', 'https://storage.supabase.co/item-images/found_airpods_pro.jpg', 'LHC Hall 1 Desk 4', 13.0110, 74.7958, '2026-08-28T15:00:00Z', 'active', '2026-08-28T15:10:00Z');

-- 12. Milton Stainless Steel Water Bottle 1L (Strongest match for LOST-06)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000012', '33333333-3333-4333-a333-333333333333', 'found', 'Water Bottles', 'Milton 1000ml stainless steel metallic water bottle with minor dent on bottom', 'https://storage.supabase.co/item-images/found_milton_bottle.jpg', 'Pavilion Grounds Benches', 13.0075, 74.7920, '2026-08-27T18:30:00Z', 'active', '2026-08-27T18:40:00Z');

-- 13. Decathlon Blue Gym Water Bottle (Distractor for LOST-06)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000013', '55555555-5555-4555-a555-555555555555', 'found', 'Water Bottles', 'Decathlon 750ml blue plastic gym shaker bottle', 'https://storage.supabase.co/item-images/found_blue_shaker.jpg', 'SAC Badminton Court', 13.0082, 74.7928, '2026-08-29T08:00:00Z', 'active', '2026-08-29T08:15:00Z');

-- 14. Set of 3 Keys on Red Honda Keychain (Strongest match for LOST-07)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000014', '33333333-3333-4333-a333-333333333333', 'found', 'Keys', '3 door keys attached to a red rubber Honda wing logo keychain', 'https://storage.supabase.co/item-images/found_red_honda_keys.jpg', 'Mechanical Dept Workshop Corridor', 13.0090, 74.7948, '2026-08-28T11:00:00Z', 'active', '2026-08-28T11:10:00Z');

-- 15. Single Bike Key with Brass Ring (Distractor for LOST-07)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000015', '55555555-5555-4555-a555-555555555555', 'found', 'Keys', 'Single silver scooter ignition key on brass ring', 'https://storage.supabase.co/item-images/found_single_key.jpg', 'Gate 2 Parking Lot', 13.0060, 74.7910, '2026-08-29T12:40:00Z', 'active', '2026-08-29T12:45:00Z');

-- 16. NITK Student ID Card - Mechanical (Strongest match for LOST-08)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000016', '55555555-5555-4555-a555-555555555555', 'found', 'ID Cards', 'NITK Surathkal Student ID Card belonging to Mechanical Engineering student', 'https://storage.supabase.co/item-images/found_student_id.jpg', 'Admin Block Counter 3', 13.0098, 74.7940, '2026-08-29T14:00:00Z', 'active', '2026-08-29T14:05:00Z');

-- 17. NITK Faculty Library Access Card (Distractor for LOST-08)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000017', '11111111-1111-4111-a111-111111111111', 'found', 'ID Cards', 'White smart card with NITK Library barcode', 'https://storage.supabase.co/item-images/found_library_card.jpg', 'Central Library Issue Desk', 13.0101, 74.7941, '2026-08-28T17:30:00Z', 'active', '2026-08-28T17:35:00Z');

-- 18. Foldable Black Automatic Umbrella (Strongest match for LOST-09)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000018', '22222222-2222-4222-a222-222222222222', 'found', 'Umbrellas', 'Black 3-fold automatic open umbrella with wrist strap', 'https://storage.supabase.co/item-images/found_black_umbrella.jpg', 'Mining Dept Entrance Porch', 13.0115, 74.7965, '2026-08-27T16:45:00Z', 'active', '2026-08-27T16:50:00Z');

-- 19. Large Blue Golf Umbrella (Distractor for LOST-09)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000019', '55555555-5555-4555-a555-555555555555', 'found', 'Umbrellas', 'Large non-foldable blue and white golf umbrella with curved wooden handle', 'https://storage.supabase.co/item-images/found_blue_golf_umbrella.jpg', 'Main Gate Security Post', 13.0055, 74.7905, '2026-08-28T08:30:00Z', 'active', '2026-08-28T08:40:00Z');

-- 20. Casio Scientific Calculator FX-991EX Black (Strongest match for LOST-10)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000020', '44444444-4444-4444-a444-444444444444', 'found', 'Electronics', 'Casio FX-991EX ClassWiz non-programmable scientific calculator with black hard cover', 'https://storage.supabase.co/item-images/found_casio_991ex.jpg', 'LHC Lecture Room 5', 13.0113, 74.7962, '2026-08-29T11:15:00Z', 'active', '2026-08-29T11:20:00Z');


-- ============================================================================
-- LOST ITEMS (10 ITEMS)
-- ============================================================================

-- 1. Black backpack with laptop compartment (Matches FOUND-01)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('e0000000-0000-4000-a000-000000000001', '11111111-1111-4111-a111-111111111111', 'lost', 'Backpacks', 'Black Lenovo laptop backpack left on 2nd floor library study desk', 'https://storage.supabase.co/item-images/lost_black_backpack.jpg', 'Central Library 2nd Floor', 13.0102, 74.7943, '2026-08-28T14:00:00Z', 'active', '2026-08-28T14:15:00Z');

-- 2. Silver Apple Laptop 13 inch (Matches FOUND-04)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('e0000000-0000-4000-a000-000000000002', '22222222-2222-4222-a222-222222222222', 'lost', 'Laptops', 'Silver Apple MacBook Air 13-inch with stickers on top lid', 'https://storage.supabase.co/item-images/lost_macbook.jpg', 'LHC Lecture Hall 3', 13.0112, 74.7960, '2026-08-29T09:30:00Z', 'active', '2026-08-29T09:45:00Z');

-- 3. Brown Leather Wallet with Cards (Matches FOUND-06)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('e0000000-0000-4000-a000-000000000003', '33333333-3333-4333-a333-333333333333', 'lost', 'Wallets', 'Brown leather wallet containing SBI card and ID card', 'https://storage.supabase.co/item-images/lost_brown_wallet.jpg', 'SAC Sports Complex', 13.0080, 74.7925, '2026-08-29T17:00:00Z', 'active', '2026-08-29T17:15:00Z');

-- 4. iPhone 13 Pro Space Grey (Matches FOUND-08)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('e0000000-0000-4000-a000-000000000004', '44444444-4444-4444-a444-444444444444', 'lost', 'Phones', 'Apple iPhone 13 Pro dark color in clear transparent back cover', 'https://storage.supabase.co/item-images/lost_iphone13.jpg', 'Department of Electronics Labs', 13.0105, 74.7955, '2026-08-29T15:00:00Z', 'active', '2026-08-29T15:10:00Z');

-- 5. Sony Noise Cancelling Over-ear Headphones (Matches FOUND-10)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('e0000000-0000-4000-a000-000000000005', '11111111-1111-4111-a111-111111111111', 'lost', 'Headphones', 'Black Sony over-ear noise cancelling headphones', 'https://storage.supabase.co/item-images/lost_sony_headphones.jpg', 'Central Library Quiet Zone', 13.0103, 74.7944, '2026-08-29T09:00:00Z', 'active', '2026-08-29T09:05:00Z');

-- 6. Silver Metallic Water Bottle 1L (Matches FOUND-12)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('e0000000-0000-4000-a000-000000000006', '33333333-3333-4333-a333-333333333333', 'lost', 'Water Bottles', 'Silver steel water bottle 1 litre capacity Milton make', 'https://storage.supabase.co/item-images/lost_steel_bottle.jpg', 'Pavilion Grounds', 13.0075, 74.7920, '2026-08-27T18:00:00Z', 'active', '2026-08-27T18:15:00Z');

-- 7. Keys on Red Keychain (Matches FOUND-14)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('e0000000-0000-4000-a000-000000000007', '33333333-3333-4333-a333-333333333333', 'lost', 'Keys', 'Set of house keys on red Honda keychain', 'https://storage.supabase.co/item-images/lost_honda_keys.jpg', 'Mechanical Dept', 13.0090, 74.7948, '2026-08-28T10:30:00Z', 'active', '2026-08-28T10:45:00Z');

-- 8. NITK College ID Card (Matches FOUND-16)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('e0000000-0000-4000-a000-000000000008', '33333333-3333-4333-a333-333333333333', 'lost', 'ID Cards', 'NITK student identification card Vikram Rao Mechanical', 'https://storage.supabase.co/item-images/lost_id_card.jpg', 'Admin Building', 13.0098, 74.7940, '2026-08-29T13:30:00Z', 'active', '2026-08-29T13:40:00Z');

-- 9. Black Compact Folding Umbrella (Matches FOUND-18)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('e0000000-0000-4000-a000-000000000009', '22222222-2222-4222-a222-222222222222', 'lost', 'Umbrellas', 'Black foldable automatic button umbrella', 'https://storage.supabase.co/item-images/lost_black_umbrella.jpg', 'Mining Department', 13.0115, 74.7965, '2026-08-27T16:30:00Z', 'active', '2026-08-27T16:40:00Z');

-- 10. Casio Scientific Calculator FX991 (Matches FOUND-20)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('e0000000-0000-4000-a000-000000000010', '44444444-4444-4444-a444-444444444444', 'lost', 'Electronics', 'Casio scientific calculator model 991 black cover', 'https://storage.supabase.co/item-images/lost_casio_991.jpg', 'LHC Complex', 13.0113, 74.7962, '2026-08-29T11:00:00Z', 'active', '2026-08-29T11:10:00Z');

-- ============================================================================
-- DEMO MATCH RESULT
-- ============================================================================
INSERT INTO matches (id, lost_item_id, found_item_id, image_score, text_score, location_score, time_score, final_score, created_at) VALUES
('m0000000-0000-4000-a000-000000000001', 'e0000000-0000-4000-a000-000000000001', 'f0000000-0000-4000-a000-000000000001', 0.95, 0.92, 0.98, 0.90, 0.94, '2026-08-28T14:40:00Z');

-- ============================================================================
-- DEMO CLAIM
-- ============================================================================
INSERT INTO claims (id, claimant_id, lost_item_id, found_item_id, match_id, status, created_at) VALUES
('c0000000-0000-4000-a000-000000000001', '11111111-1111-4111-a111-111111111111', 'e0000000-0000-4000-a000-000000000001', 'f0000000-0000-4000-a000-000000000001', 'm0000000-0000-4000-a000-000000000001', 'pending', '2026-08-28T15:00:00Z');
