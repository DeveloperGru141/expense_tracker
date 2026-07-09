-- 1. Fix RLS policies: wrap auth.uid() in (select auth.uid()) for initplan optimization
-- Users
drop policy if exists "Users select" on users;
drop policy if exists "Users update" on users;
drop policy if exists "Enable insert for users based on user_id" on users;
create policy "Users select" on users for select to authenticated using ((select auth.uid()) = id);
create policy "Users update" on users for update to authenticated using ((select auth.uid()) = id) with check ((select auth.uid()) = id);
create policy "Enable insert for users based on user_id" on users for insert to authenticated with check ((select auth.uid()) = id);

-- Categories
drop policy if exists "Categories select" on categories;
drop policy if exists "Categories insert" on categories;
drop policy if exists "Categories update" on categories;
drop policy if exists "Categories delete" on categories;
create policy "Categories select" on categories for select to authenticated using ((select auth.uid()) = user_id);
create policy "Categories insert" on categories for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Categories update" on categories for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Categories delete" on categories for delete to authenticated using ((select auth.uid()) = user_id);

-- Expenses
drop policy if exists "Expenses select" on expenses;
drop policy if exists "Expenses insert" on expenses;
drop policy if exists "Expenses update" on expenses;
drop policy if exists "Expenses delete" on expenses;
create policy "Expenses select" on expenses for select to authenticated using ((select auth.uid()) = user_id);
create policy "Expenses insert" on expenses for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Expenses update" on expenses for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Expenses delete" on expenses for delete to authenticated using ((select auth.uid()) = user_id);

-- Recurring Expenses
drop policy if exists "Recurring expenses select" on recurring_expenses;
drop policy if exists "Recurring expenses insert" on recurring_expenses;
drop policy if exists "Recurring expenses update" on recurring_expenses;
drop policy if exists "Recurring expenses delete" on recurring_expenses;
create policy "Recurring expenses select" on recurring_expenses for select to authenticated using ((select auth.uid()) = user_id);
create policy "Recurring expenses insert" on recurring_expenses for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Recurring expenses update" on recurring_expenses for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Recurring expenses delete" on recurring_expenses for delete to authenticated using ((select auth.uid()) = user_id);

-- Income
drop policy if exists "Income select" on income;
drop policy if exists "Income insert" on income;
drop policy if exists "Income update" on income;
drop policy if exists "Income delete" on income;
create policy "Income select" on income for select to authenticated using ((select auth.uid()) = user_id);
create policy "Income insert" on income for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Income update" on income for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Income delete" on income for delete to authenticated using ((select auth.uid()) = user_id);

-- Recurring Income
drop policy if exists "Recurring income select" on recurring_income;
drop policy if exists "Recurring income insert" on recurring_income;
drop policy if exists "Recurring income update" on recurring_income;
drop policy if exists "Recurring income delete" on recurring_income;
create policy "Recurring income select" on recurring_income for select to authenticated using ((select auth.uid()) = user_id);
create policy "Recurring income insert" on recurring_income for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Recurring income update" on recurring_income for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Recurring income delete" on recurring_income for delete to authenticated using ((select auth.uid()) = user_id);

-- Settings
drop policy if exists "Settings select" on settings;
drop policy if exists "Settings insert" on settings;
drop policy if exists "Settings update" on settings;
drop policy if exists "Settings delete" on settings;
create policy "Settings select" on settings for select to authenticated using ((select auth.uid()) = user_id);
create policy "Settings insert" on settings for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Settings update" on settings for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Settings delete" on settings for delete to authenticated using ((select auth.uid()) = user_id);

-- 2. Add indexes on user_id foreign key columns for query performance
create index if not exists idx_expenses_user_id on expenses(user_id);
create index if not exists idx_income_user_id on income(user_id);
create index if not exists idx_recurring_expenses_user_id on recurring_expenses(user_id);
create index if not exists idx_recurring_income_user_id on recurring_income(user_id);
create index if not exists idx_categories_user_id on categories(user_id);
create index if not exists idx_settings_user_id on settings(user_id);

-- 3. Revoke public and authenticated execute on handle_new_user (it's trigger-only, no need for RPC access)
revoke execute on function public.handle_new_user() from anon, authenticated;

-- 4. Remove unused food column from categories (added accidentally)
alter table categories drop column if exists food;

-- 5. Change financial columns from double precision to numeric(12,2)
alter table expenses alter column amount type numeric(12,2) using amount::numeric(12,2);
alter table income alter column amount type numeric(12,2) using amount::numeric(12,2);
alter table recurring_expenses alter column amount type numeric(12,2) using amount::numeric(12,2);
alter table recurring_income alter column amount type numeric(12,2) using amount::numeric(12,2);
alter table categories alter column budget_limit type numeric(12,2) using budget_limit::numeric(12,2);

-- 6. Add updated_at timestamps to track record changes
alter table users add column if not exists updated_at timestamp with time zone default timezone('utc'::text, now());
alter table categories add column if not exists updated_at timestamp with time zone default timezone('utc'::text, now());
alter table expenses add column if not exists updated_at timestamp with time zone default timezone('utc'::text, now());
alter table income add column if not exists updated_at timestamp with time zone default timezone('utc'::text, now());
alter table recurring_expenses add column if not exists updated_at timestamp with time zone default timezone('utc'::text, now());
alter table recurring_income add column if not exists updated_at timestamp with time zone default timezone('utc'::text, now());
