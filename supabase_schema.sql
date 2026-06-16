-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Users Table
create table if not exists users (
    id uuid primary key default uuid_generate_v4(),
    username text unique not null,
    google_id text unique,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now())
);

alter table users enable row level security;

create policy "Users select" on users for select to authenticated using ((select auth.uid()) = id);
create policy "Users update" on users for update to authenticated using ((select auth.uid()) = id) with check ((select auth.uid()) = id);
create policy "Enable insert for users based on user_id" on users for insert to authenticated with check ((select auth.uid()) = id);

-- Categories Table
create table if not exists categories (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    name text not null,
    color text default '#0f766e',
    budget_limit numeric(12,2) default 0,
    updated_at timestamp with time zone default timezone('utc'::text, now()),
    unique(user_id, name)
);

alter table categories enable row level security;

create policy "Categories select" on categories for select to authenticated using ((select auth.uid()) = user_id);
create policy "Categories insert" on categories for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Categories update" on categories for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Categories delete" on categories for delete to authenticated using ((select auth.uid()) = user_id);

-- Expenses Table
create table if not exists expenses (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    title text not null,
    amount numeric(12,2) not null,
    category text not null,
    expense_date date not null,
    notes text default '',
    receipt_image text default '',
    updated_at timestamp with time zone default timezone('utc'::text, now())
);

alter table expenses enable row level security;

create policy "Expenses select" on expenses for select to authenticated using ((select auth.uid()) = user_id);
create policy "Expenses insert" on expenses for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Expenses update" on expenses for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Expenses delete" on expenses for delete to authenticated using ((select auth.uid()) = user_id);

-- Recurring Expenses Table
create table if not exists recurring_expenses (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    title text not null,
    amount numeric(12,2) not null,
    category text not null,
    frequency text not null,
    start_date date not null,
    next_occurrence date not null,
    notes text default '',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now())
);

alter table recurring_expenses enable row level security;

create policy "Recurring expenses select" on recurring_expenses for select to authenticated using ((select auth.uid()) = user_id);
create policy "Recurring expenses insert" on recurring_expenses for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Recurring expenses update" on recurring_expenses for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Recurring expenses delete" on recurring_expenses for delete to authenticated using ((select auth.uid()) = user_id);

-- Income Table
create table if not exists income (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    title text not null,
    amount numeric(12,2) not null,
    category text not null,
    income_date date not null,
    notes text default '',
    updated_at timestamp with time zone default timezone('utc'::text, now())
);

alter table income enable row level security;

create policy "Income select" on income for select to authenticated using ((select auth.uid()) = user_id);
create policy "Income insert" on income for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Income update" on income for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Income delete" on income for delete to authenticated using ((select auth.uid()) = user_id);

-- Recurring Income Table
create table if not exists recurring_income (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    title text not null,
    amount numeric(12,2) not null,
    category text not null,
    frequency text not null,
    start_date date not null,
    next_occurrence date not null,
    notes text default '',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now())
);

alter table recurring_income enable row level security;

create policy "Recurring income select" on recurring_income for select to authenticated using ((select auth.uid()) = user_id);
create policy "Recurring income insert" on recurring_income for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Recurring income update" on recurring_income for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Recurring income delete" on recurring_income for delete to authenticated using ((select auth.uid()) = user_id);

-- Settings Table
create table if not exists settings (
    user_id uuid not null references users(id) on delete cascade,
    key text not null,
    value text not null,
    primary key (user_id, key)
);

alter table settings enable row level security;

create policy "Settings select" on settings for select to authenticated using ((select auth.uid()) = user_id);
create policy "Settings insert" on settings for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Settings update" on settings for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Settings delete" on settings for delete to authenticated using ((select auth.uid()) = user_id);

-- Indexes for performance
create index if not exists idx_expenses_user_id on expenses(user_id);
create index if not exists idx_income_user_id on income(user_id);
create index if not exists idx_recurring_expenses_user_id on recurring_expenses(user_id);
create index if not exists idx_recurring_income_user_id on recurring_income(user_id);
create index if not exists idx_categories_user_id on categories(user_id);
create index if not exists idx_settings_user_id on settings(user_id);
