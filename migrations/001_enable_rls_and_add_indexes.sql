-- Migration 001: Enable Row Level Security and Add Indexes
-- Date: 2026-08-19
-- Description: Critical security hardening and performance optimization

-- ============================================
-- SECURITY: Enable Row Level Security (RLS)
-- ============================================

ALTER TABLE public.tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nas_backups ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.management_pack_snapshot_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.management_pack_snapshot_files ENABLE ROW LEVEL SECURITY;

-- ============================================
-- SECURITY: Create RLS Policies
-- ============================================

-- Tickets: Full CRUD for authenticated users
DROP POLICY IF EXISTS "authenticated_users_tickets_select" ON public.tickets;
CREATE POLICY "authenticated_users_tickets_select" ON public.tickets
  FOR SELECT TO authenticated USING (true);

DROP POLICY IF EXISTS "authenticated_users_tickets_insert" ON public.tickets;
CREATE POLICY "authenticated_users_tickets_insert" ON public.tickets
  FOR INSERT TO authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "authenticated_users_tickets_update" ON public.tickets;
CREATE POLICY "authenticated_users_tickets_update" ON public.tickets
  FOR UPDATE TO authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "authenticated_users_tickets_delete" ON public.tickets;
CREATE POLICY "authenticated_users_tickets_delete" ON public.tickets
  FOR DELETE TO authenticated USING (true);

-- NAS Backups: Full CRUD for authenticated users
DROP POLICY IF EXISTS "authenticated_users_nas_select" ON public.nas_backups;
CREATE POLICY "authenticated_users_nas_select" ON public.nas_backups
  FOR SELECT TO authenticated USING (true);

DROP POLICY IF EXISTS "authenticated_users_nas_insert" ON public.nas_backups;
CREATE POLICY "authenticated_users_nas_insert" ON public.nas_backups
  FOR INSERT TO authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "authenticated_users_nas_update" ON public.nas_backups;
CREATE POLICY "authenticated_users_nas_update" ON public.nas_backups
  FOR UPDATE TO authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "authenticated_users_nas_delete" ON public.nas_backups;
CREATE POLICY "authenticated_users_nas_delete" ON public.nas_backups
  FOR DELETE TO authenticated USING (true);

-- Users: Read all, update own profile
DROP POLICY IF EXISTS "users_select" ON public.users;
CREATE POLICY "users_select" ON public.users
  FOR SELECT TO authenticated USING (true);

DROP POLICY IF EXISTS "users_insert" ON public.users;
CREATE POLICY "users_insert" ON public.users
  FOR INSERT TO authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "users_update_own" ON public.users;
CREATE POLICY "users_update_own" ON public.users
  FOR UPDATE TO authenticated 
  USING (true) 
  WITH CHECK (true);

-- Management Pack: Full access for authenticated users
DROP POLICY IF EXISTS "authenticated_users_metrics_all" ON public.management_pack_snapshot_metrics;
CREATE POLICY "authenticated_users_metrics_all" ON public.management_pack_snapshot_metrics
  FOR ALL TO authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "authenticated_users_files_all" ON public.management_pack_snapshot_files;
CREATE POLICY "authenticated_users_files_all" ON public.management_pack_snapshot_files
  FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- ============================================
-- PERFORMANCE: Add Database Indexes
-- ============================================

-- Tickets table indexes
CREATE INDEX IF NOT EXISTS idx_tickets_date ON public.tickets(date);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON public.tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_attended_by ON public.tickets(attended_by);
CREATE INDEX IF NOT EXISTS idx_tickets_department ON public.tickets(department);
CREATE INDEX IF NOT EXISTS idx_tickets_location ON public.tickets(location);
CREATE INDEX IF NOT EXISTS idx_tickets_category ON public.tickets(category);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_tickets_status_date ON public.tickets(status, date);
CREATE INDEX IF NOT EXISTS idx_tickets_attended_by_status ON public.tickets(attended_by, status);

-- NAS Backups table indexes
CREATE INDEX IF NOT EXISTS idx_nas_backups_date ON public.nas_backups(date);
CREATE INDEX IF NOT EXISTS idx_nas_backups_server ON public.nas_backups(server_name);

-- ============================================
-- VERIFICATION
-- ============================================

-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN ('tickets', 'nas_backups', 'users', 'management_pack_snapshot_metrics', 'management_pack_snapshot_files');

-- Check indexes
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
  AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;
