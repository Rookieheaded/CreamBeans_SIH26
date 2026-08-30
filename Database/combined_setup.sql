-- ============================================================================
-- CREAM BEANS — SIH 2026 Campus Lost & Found System
-- Combined Schema + Auth + Storage + Seed Setup for Supabase
-- Person 6: Database & Data-Integration Engineer
-- ============================================================================

-- 1. DROP EXISTING TABLES IF THEY EXIST (Clean Reset)
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS items CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 2. CREATE USERS TABLE (Strict CANONICAL Schema from PROJECT_SPEC.md)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. CREATE ITEMS TABLE (Strict CANONICAL Schema from PROJECT_SPEC.md)
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('lost', 'found')),
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    image_url TEXT,
    location VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    timestamp TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'matched', 'returned')),
    embedding FLOAT8[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_items_status ON items(status);
CREATE INDEX idx_items_type ON items(type);
CREATE INDEX idx_items_reporter ON items(reporter_id);
CREATE INDEX idx_items_type_status ON items(type, status);

-- 4. CREATE MATCHES TABLE (Strict CANONICAL Schema from PROJECT_SPEC.md)
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lost_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    found_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    image_score DOUBLE PRECISION NOT NULL,
    text_score DOUBLE PRECISION NOT NULL,
    location_score DOUBLE PRECISION NOT NULL,
    time_score DOUBLE PRECISION NOT NULL,
    final_score DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_matches_lost_item ON matches(lost_item_id);
CREATE INDEX idx_matches_found_item ON matches(found_item_id);
CREATE INDEX idx_matches_final_score ON matches(final_score DESC);

-- 5. ENABLE ROW LEVEL SECURITY (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read users" ON users FOR SELECT USING (true);
CREATE POLICY "Allow public insert users" ON users FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update users" ON users FOR UPDATE USING (true);

CREATE POLICY "Allow public read items" ON items FOR SELECT USING (true);
CREATE POLICY "Allow public insert items" ON items FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update items" ON items FOR UPDATE USING (true);

CREATE POLICY "Allow public read matches" ON matches FOR SELECT USING (true);
CREATE POLICY "Allow public insert matches" ON matches FOR INSERT WITH CHECK (true);

-- 6. AUTOMATIC RLS EVENT TRIGGER FOR FUTURE TABLES
CREATE OR REPLACE FUNCTION public.auto_enable_rls()
RETURNS event_trigger AS $$
DECLARE
    obj record;
BEGIN
    FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands() WHERE command_tag = 'CREATE TABLE' LOOP
        IF obj.schema_name = 'public' THEN
            EXECUTE format('ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY;', obj.schema_name, obj.object_identity);
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

DROP EVENT TRIGGER IF EXISTS trigger_auto_enable_rls;

CREATE EVENT TRIGGER trigger_auto_enable_rls
ON ddl_command_end
WHEN TAG IN ('CREATE TABLE')
EXECUTE FUNCTION public.auto_enable_rls();

-- 7. SUPABASE AUTH INTEGRATION TRIGGER (auth.users -> public.users sync)
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, name, email, phone, created_at)
    VALUES (
        new.id,
        COALESCE(new.raw_user_meta_data->>'name', new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1)),
        new.email,
        new.raw_user_meta_data->>'phone',
        new.created_at
    )
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        email = EXCLUDED.email,
        phone = EXCLUDED.phone;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'auth' AND tablename = 'users') THEN
        DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
        CREATE TRIGGER on_auth_user_created
            AFTER INSERT ON auth.users
            FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
    END IF;
END $$;

-- 8. SUPABASE STORAGE BUCKET CONFIGURATION ('item-images')
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'storage' AND tablename = 'buckets') THEN
        INSERT INTO storage.buckets (id, name, public)
        VALUES ('item-images', 'item-images', true)
        ON CONFLICT (id) DO NOTHING;
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'storage' AND tablename = 'objects') THEN
        DROP POLICY IF EXISTS "Public Read Access for item-images" ON storage.objects;
        CREATE POLICY "Public Read Access for item-images" ON storage.objects
            FOR SELECT USING (bucket_id = 'item-images');

        DROP POLICY IF EXISTS "Public Upload Access for item-images" ON storage.objects;
        CREATE POLICY "Public Upload Access for item-images" ON storage.objects
            FOR INSERT WITH CHECK (bucket_id = 'item-images');
    END IF;
END $$;

-- 9. INSERT DEMO USERS (5 USERS)
INSERT INTO users (id, name, email, phone, created_at) VALUES
('11111111-1111-4111-a111-111111111111', 'Rahul Sharma', 'rahul.cs24@nitk.edu.in', '+91-9876543210', '2026-08-01T10:00:00Z'),
('22222222-2222-4222-a222-222222222222', 'Ananya Patel', 'ananya.ee23@nitk.edu.in', '+91-9876543211', '2026-08-02T11:00:00Z'),
('33333333-3333-4333-a333-333333333333', 'Vikram Rao', 'vikram.mech22@nitk.edu.in', '+91-9876543212', '2026-08-03T12:00:00Z'),
('44444444-4444-4444-a444-444444444444', 'Priya Nair', 'priya.ec24@nitk.edu.in', '+91-9876543213', '2026-08-04T13:00:00Z'),
('55555555-5555-4555-a555-555555555555', 'NITK Security Office', 'security.office@nitk.edu.in', '+91-8242474000', '2026-08-05T09:00:00Z');

-- 10. INSERT DEMO FOUND ITEMS (20 ITEMS)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('f0000000-0000-4000-a000-000000000001', '55555555-5555-4555-a555-555555555555', 'found', 'Backpacks', 'Black Lenovo backpack with padded laptop compartment and red zipper accent', 'https://storage.supabase.co/item-images/found_lenovo_bag.jpg', 'Central Library 2nd Floor', 13.0102, 74.7943, '2026-08-28T14:30:00Z', 'active', '2026-08-28T14:35:00Z'),
('f0000000-0000-4000-a000-000000000002', '22222222-2222-4222-a222-222222222222', 'found', 'Backpacks', 'Dark grey laptop bag found on chair in CS lab', 'https://storage.supabase.co/item-images/found_dark_laptop_bag.jpg', 'Dept of Computer Science Room 201', 13.0108, 74.7951, '2026-08-28T16:00:00Z', 'active', '2026-08-28T16:10:00Z'),
('f0000000-0000-4000-a000-000000000003', '33333333-3333-4333-a333-333333333333', 'found', 'Backpacks', 'Blue Nike sports backpack with water bottle side pocket', 'https://storage.supabase.co/item-images/found_blue_nike.jpg', 'Main Canteen Area', 13.0095, 74.7938, '2026-08-27T12:15:00Z', 'active', '2026-08-27T12:30:00Z'),
('f0000000-0000-4000-a000-000000000004', '55555555-5555-4555-a555-555555555555', 'found', 'Laptops', 'Silver Apple MacBook Air 13-inch M2 with anime sticker on lid', 'https://storage.supabase.co/item-images/found_macbook_air.jpg', 'LHC Lecture Hall 3', 13.0112, 74.7960, '2026-08-29T10:00:00Z', 'active', '2026-08-29T10:05:00Z'),
('f0000000-0000-4000-a000-000000000005', '11111111-1111-4111-a111-111111111111', 'found', 'Laptops', 'Black Dell Inspiron 15-inch laptop left near charger point', 'https://storage.supabase.co/item-images/found_dell_laptop.jpg', 'Central Library Ground Floor', 13.0101, 74.7942, '2026-08-28T11:30:00Z', 'active', '2026-08-28T11:45:00Z'),
('f0000000-0000-4000-a000-000000000006', '44444444-4444-4444-a444-444444444444', 'found', 'Wallets', 'Brown leather bi-fold wallet containing SBI debit card and driving license', 'https://storage.supabase.co/item-images/found_brown_wallet.jpg', 'SAC Sports Complex Quadrangle', 13.0080, 74.7925, '2026-08-29T17:45:00Z', 'active', '2026-08-29T17:50:00Z'),
('f0000000-0000-4000-a000-000000000007', '22222222-2222-4222-a222-222222222222', 'found', 'Wallets', 'Black slim minimalist card holder with 3 credit cards', 'https://storage.supabase.co/item-images/found_black_cardholder.jpg', 'Main Canteen Cash Counter', 13.0096, 74.7939, '2026-08-27T13:00:00Z', 'active', '2026-08-27T13:10:00Z'),
('f0000000-0000-4000-a000-000000000008', '44444444-4444-4444-a444-444444444444', 'found', 'Phones', 'Graphite Apple iPhone 13 Pro with clear silicone case', 'https://storage.supabase.co/item-images/found_iphone13.jpg', 'Department of Electronics Lab 2', 13.0105, 74.7955, '2026-08-29T15:20:00Z', 'active', '2026-08-29T15:25:00Z'),
('f0000000-0000-4000-a000-000000000009', '33333333-3333-4333-a333-333333333333', 'found', 'Phones', 'Awesome Blue Samsung Galaxy A54 smartphone with black bumper case', 'https://storage.supabase.co/item-images/found_samsung_a54.jpg', 'Mega Tower Hostel Block 7 Common Room', 13.0125, 74.7970, '2026-08-28T20:10:00Z', 'active', '2026-08-28T20:20:00Z'),
('f0000000-0000-4000-a000-000000000010', '11111111-1111-4111-a111-111111111111', 'found', 'Headphones', 'Black Sony WH-1000XM4 wireless over-ear noise cancelling headphones in black zip case', 'https://storage.supabase.co/item-images/found_sony_headphones.jpg', 'Central Library Reading Room', 13.0103, 74.7944, '2026-08-29T09:15:00Z', 'active', '2026-08-29T09:20:00Z'),
('f0000000-0000-4000-a000-000000000011', '22222222-2222-4222-a222-222222222222', 'found', 'Headphones', 'White Apple AirPods Pro 2 in wireless charging case with lanyard loop', 'https://storage.supabase.co/item-images/found_airpods_pro.jpg', 'LHC Hall 1 Desk 4', 13.0110, 74.7958, '2026-08-28T15:00:00Z', 'active', '2026-08-28T15:10:00Z'),
('f0000000-0000-4000-a000-000000000012', '33333333-3333-4333-a333-333333333333', 'found', 'Water Bottles', 'Milton 1000ml stainless steel metallic water bottle with minor dent on bottom', 'https://storage.supabase.co/item-images/found_milton_bottle.jpg', 'Pavilion Grounds Benches', 13.0075, 74.7920, '2026-08-27T18:30:00Z', 'active', '2026-08-27T18:40:00Z'),
('f0000000-0000-4000-a000-000000000013', '55555555-5555-4555-a555-555555555555', 'found', 'Water Bottles', 'Decathlon 750ml blue plastic gym shaker bottle', 'https://storage.supabase.co/item-images/found_blue_shaker.jpg', 'SAC Badminton Court', 13.0082, 74.7928, '2026-08-29T08:00:00Z', 'active', '2026-08-29T08:15:00Z'),
('f0000000-0000-4000-a000-000000000014', '33333333-3333-4333-a333-333333333333', 'found', 'Keys', '3 door keys attached to a red rubber Honda wing logo keychain', 'https://storage.supabase.co/item-images/found_red_honda_keys.jpg', 'Mechanical Dept Workshop Corridor', 13.0090, 74.7948, '2026-08-28T11:00:00Z', 'active', '2026-08-28T11:10:00Z'),
('f0000000-0000-4000-a000-000000000015', '55555555-5555-4555-a555-555555555555', 'found', 'Keys', 'Single silver scooter ignition key on brass ring', 'https://storage.supabase.co/item-images/found_single_key.jpg', 'Gate 2 Parking Lot', 13.0060, 74.7910, '2026-08-29T12:40:00Z', 'active', '2026-08-29T12:45:00Z'),
('f0000000-0000-4000-a000-000000000016', '55555555-5555-4555-a555-555555555555', 'found', 'ID Cards', 'NITK Surathkal Student ID Card belonging to Mechanical Engineering student', 'https://storage.supabase.co/item-images/found_student_id.jpg', 'Admin Block Counter 3', 13.0098, 74.7940, '2026-08-29T14:00:00Z', 'active', '2026-08-29T14:05:00Z'),
('f0000000-0000-4000-a000-000000000017', '11111111-1111-4111-a111-111111111111', 'found', 'ID Cards', 'White smart card with NITK Library barcode', 'https://storage.supabase.co/item-images/found_library_card.jpg', 'Central Library Issue Desk', 13.0101, 74.7941, '2026-08-28T17:30:00Z', 'active', '2026-08-28T17:35:00Z'),
('f0000000-0000-4000-a000-000000000018', '22222222-2222-4222-a222-222222222222', 'found', 'Umbrellas', 'Black 3-fold automatic open umbrella with wrist strap', 'https://storage.supabase.co/item-images/found_black_umbrella.jpg', 'Mining Dept Entrance Porch', 13.0115, 74.7965, '2026-08-27T16:45:00Z', 'active', '2026-08-27T16:50:00Z'),
('f0000000-0000-4000-a000-000000000019', '55555555-5555-4555-a555-555555555555', 'found', 'Umbrellas', 'Large non-foldable blue and white golf umbrella with curved wooden handle', 'https://storage.supabase.co/item-images/found_blue_golf_umbrella.jpg', 'Main Gate Security Post', 13.0055, 74.7905, '2026-08-28T08:30:00Z', 'active', '2026-08-28T08:40:00Z'),
('f0000000-0000-4000-a000-000000000020', '44444444-4444-4444-a444-444444444444', 'found', 'Electronics', 'Casio FX-991EX ClassWiz non-programmable scientific calculator with black hard cover', 'https://storage.supabase.co/item-images/found_casio_991ex.jpg', 'LHC Lecture Room 5', 13.0113, 74.7962, '2026-08-29T11:15:00Z', 'active', '2026-08-29T11:20:00Z');

-- 11. INSERT DEMO LOST ITEMS (10 ITEMS)
INSERT INTO items (id, reporter_id, type, category, description, image_url, location, latitude, longitude, timestamp, status, created_at) VALUES
('e0000000-0000-4000-a000-000000000001', '11111111-1111-4111-a111-111111111111', 'lost', 'Backpacks', 'Black Lenovo laptop backpack left on 2nd floor library study desk', 'https://storage.supabase.co/item-images/lost_black_backpack.jpg', 'Central Library 2nd Floor', 13.0102, 74.7943, '2026-08-28T14:00:00Z', 'active', '2026-08-28T14:15:00Z'),
('e0000000-0000-4000-a000-000000000002', '22222222-2222-4222-a222-222222222222', 'lost', 'Laptops', 'Silver Apple MacBook Air 13-inch with stickers on top lid', 'https://storage.supabase.co/item-images/lost_macbook.jpg', 'LHC Lecture Hall 3', 13.0112, 74.7960, '2026-08-29T09:30:00Z', 'active', '2026-08-29T09:45:00Z'),
('e0000000-0000-4000-a000-000000000003', '33333333-3333-4333-a333-333333333333', 'lost', 'Wallets', 'Brown leather wallet containing SBI card and ID card', 'https://storage.supabase.co/item-images/lost_brown_wallet.jpg', 'SAC Sports Complex', 13.0080, 74.7925, '2026-08-29T17:00:00Z', 'active', '2026-08-29T17:15:00Z'),
('e0000000-0000-4000-a000-000000000004', '44444444-4444-4444-a444-444444444444', 'lost', 'Phones', 'Apple iPhone 13 Pro dark color in clear transparent back cover', 'https://storage.supabase.co/item-images/lost_iphone13.jpg', 'Department of Electronics Labs', 13.0105, 74.7955, '2026-08-29T15:00:00Z', 'active', '2026-08-29T15:10:00Z'),
('e0000000-0000-4000-a000-000000000005', '11111111-1111-4111-a111-111111111111', 'lost', 'Headphones', 'Black Sony over-ear noise cancelling headphones', 'https://storage.supabase.co/item-images/lost_sony_headphones.jpg', 'Central Library Quiet Zone', 13.0103, 74.7944, '2026-08-29T09:00:00Z', 'active', '2026-08-29T09:05:00Z'),
('e0000000-0000-4000-a000-000000000006', '33333333-3333-4333-a333-333333333333', 'lost', 'Water Bottles', 'Silver steel water bottle 1 litre capacity Milton make', 'https://storage.supabase.co/item-images/lost_steel_bottle.jpg', 'Pavilion Grounds', 13.0075, 74.7920, '2026-08-27T18:00:00Z', 'active', '2026-08-27T18:15:00Z'),
('e0000000-0000-4000-a000-000000000007', '33333333-3333-4333-a333-333333333333', 'lost', 'Keys', 'Set of house keys on red Honda keychain', 'https://storage.supabase.co/item-images/lost_honda_keys.jpg', 'Mechanical Dept', 13.0090, 74.7948, '2026-08-28T10:30:00Z', 'active', '2026-08-28T10:45:00Z'),
('e0000000-0000-4000-a000-000000000008', '33333333-3333-4333-a333-333333333333', 'lost', 'ID Cards', 'NITK student identification card Vikram Rao Mechanical', 'https://storage.supabase.co/item-images/lost_id_card.jpg', 'Admin Building', 13.0098, 74.7940, '2026-08-29T13:30:00Z', 'active', '2026-08-29T13:40:00Z'),
('e0000000-0000-4000-a000-000000000009', '22222222-2222-4222-a222-222222222222', 'lost', 'Umbrellas', 'Black foldable automatic button umbrella', 'https://storage.supabase.co/item-images/lost_black_umbrella.jpg', 'Mining Department', 13.0115, 74.7965, '2026-08-27T16:30:00Z', 'active', '2026-08-27T16:40:00Z'),
('e0000000-0000-4000-a000-000000000010', '44444444-4444-4444-a444-444444444444', 'lost', 'Electronics', 'Casio scientific calculator model 991 black cover', 'https://storage.supabase.co/item-images/lost_casio_991.jpg', 'LHC Complex', 13.0113, 74.7962, '2026-08-29T11:00:00Z', 'active', '2026-08-29T11:10:00Z');
