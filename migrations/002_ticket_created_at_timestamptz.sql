-- Migration 002: Standardize ticket creation timestamps
-- Date: 2026-11-21
-- Description: Add a timezone-aware created_at timestamp to tickets.
-- Safety: This migration does not delete or overwrite existing ticket data.

-- Add created_at only if it does not already exist.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'tickets'
          AND column_name = 'created_at'
    ) THEN
        ALTER TABLE public.tickets
            ADD COLUMN created_at timestamptz;
    END IF;
END $$;

-- Backfill only rows that do not yet have created_at.
-- IMPORTANT: Review before production deployment. If the existing 'date'
-- column contains only a calendar date, this backfill uses the migration
-- execution time and must not be treated as the original lodging time.
UPDATE public.tickets
SET created_at = now()
WHERE created_at IS NULL;

-- Make created_at mandatory and database-generated for new tickets.
ALTER TABLE public.tickets
    ALTER COLUMN created_at SET NOT NULL;

ALTER TABLE public.tickets
    ALTER COLUMN created_at SET DEFAULT now();

-- Support recent-ticket queries and reporting.
CREATE INDEX IF NOT EXISTS idx_tickets_created_at
    ON public.tickets (created_at DESC);

-- Verification
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'tickets'
  AND column_name = 'created_at';
