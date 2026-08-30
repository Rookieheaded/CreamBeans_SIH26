-- ============================================================================
-- CREAM BEANS — SIH 2026 Campus Lost & Found Intelligence System
-- Database Schema (Supabase / PostgreSQL)
-- Person 6: Database & Data-Integration Engineer
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================================
-- 1. USERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 2. ITEMS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS items (
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
    embedding vector(512),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for frequent queries
CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
CREATE INDEX IF NOT EXISTS idx_items_type ON items(type);
CREATE INDEX IF NOT EXISTS idx_items_reporter ON items(reporter_id);
CREATE INDEX IF NOT EXISTS idx_items_type_status ON items(type, status);

-- ============================================================================
-- 3. MATCHES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS matches (
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

-- Indexes for match retrieval
CREATE INDEX IF NOT EXISTS idx_matches_lost_item ON matches(lost_item_id);
CREATE INDEX IF NOT EXISTS idx_matches_found_item ON matches(found_item_id);
CREATE INDEX IF NOT EXISTS idx_matches_final_score ON matches(final_score DESC);

-- ============================================================================
-- 4. CLAIMS TABLE (Minimal SIH Claim System)
-- ============================================================================
CREATE TABLE IF NOT EXISTS claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claimant_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lost_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    found_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    match_id UUID REFERENCES matches(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_claims_claimant ON claims(claimant_id);
CREATE INDEX IF NOT EXISTS idx_claims_lost ON claims(lost_item_id);
CREATE INDEX IF NOT EXISTS idx_claims_found ON claims(found_item_id);
CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status);

-- ============================================================================
-- 5. ROW LEVEL SECURITY (RLS) FOR TABLES
-- ============================================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims ENABLE ROW LEVEL SECURITY;

-- Permissive policies for MVP API access
CREATE POLICY "Allow public read access to users" ON users FOR SELECT USING (true);
CREATE POLICY "Allow public insert access to users" ON users FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update access to users" ON users FOR UPDATE USING (true);

CREATE POLICY "Allow public read access to items" ON items FOR SELECT USING (true);
CREATE POLICY "Allow public insert access to items" ON items FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update access to items" ON items FOR UPDATE USING (true);

CREATE POLICY "Allow public read access to matches" ON matches FOR SELECT USING (true);
CREATE POLICY "Allow public insert access to matches" ON matches FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read access to claims" ON claims FOR SELECT USING (true);
CREATE POLICY "Allow public insert access to claims" ON claims FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update access to claims" ON claims FOR UPDATE USING (true);

-- ============================================================================
-- 6. AUTOMATIC RLS EVENT TRIGGER FOR NEW TABLES IN PUBLIC SCHEMA
-- ============================================================================
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

-- ============================================================================
-- 7. SUPABASE AUTH INTEGRATION TRIGGER
-- Syncs registered auth.users into public.users
-- ============================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, name, email, phone, is_admin, created_at)
    VALUES (
        new.id,
        COALESCE(new.raw_user_meta_data->>'name', new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1)),
        new.email,
        new.raw_user_meta_data->>'phone',
        COALESCE((new.raw_user_meta_data->>'is_admin')::boolean, false),
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

-- ============================================================================
-- 8. SUPABASE STORAGE BUCKET CONFIGURATION ('item-images')
-- ============================================================================
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
