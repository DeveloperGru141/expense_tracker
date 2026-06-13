-- Run this in Supabase SQL Editor after creating the "receipts" bucket
-- via Dashboard > Storage > Create bucket (name: "receipts", public: false)

-- 1. Enable RLS on storage.objects (already enabled by default)
-- 2. Create policies for the receipts bucket

-- Allow authenticated users to upload receipt files into their own folder
create policy "Users can upload their own receipts"
on storage.objects
for insert
to authenticated
with check (
  bucket_id = 'receipts'
  and (storage.foldername(name))[1] = (select auth.uid()::text)
);

-- Allow authenticated users to select (read) their own receipt files
create policy "Users can view their own receipts"
on storage.objects
for select
to authenticated
using (
  bucket_id = 'receipts'
  and (storage.foldername(name))[1] = (select auth.uid()::text)
);

-- Allow authenticated users to update their own receipt files (for upsert)
create policy "Users can update their own receipts"
on storage.objects
for update
to authenticated
with check (
  bucket_id = 'receipts'
  and (storage.foldername(name))[1] = (select auth.uid()::text)
);

-- Allow authenticated users to delete their own receipt files
create policy "Users can delete their own receipts"
on storage.objects
for delete
to authenticated
using (
  bucket_id = 'receipts'
  and (storage.foldername(name))[1] = (select auth.uid()::text)
);
