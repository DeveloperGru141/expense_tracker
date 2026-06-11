-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Users Table
create table if not exists users (
    id uuid primary key default uuid_generate_v4(),
    username text unique not null,
    google_id text unique,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Categories Table
create table if not exists categories (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    name text not null,
    color text default '#0f766e',
    budget_limit float default 0,
    unique(user_id, name)
);

-- Expenses Table
create table if not exists expenses (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    title text not null,
    amount float not null,
    category text not null,
    expense_date date not null,
    notes text default '',
    receipt_image text default ''
);

-- Recurring Expenses Table
create table if not exists recurring_expenses (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    title text not null,
    amount float not null,
    category text not null,
    frequency text not null,
    start_date date not null,
    next_occurrence date not null,
    notes text default ''
);

-- Income Table
create table if not exists income (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    title text not null,
    amount float not null,
    category text not null,
    income_date date not null,
    notes text default ''
);

-- Recurring Income Table
create table if not exists recurring_income (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    title text not null,
    amount float not null,
    category text not null,
    frequency text not null,
    start_date date not null,
    next_occurrence date not null,
    notes text default ''
);

-- Settings Table
create table if not exists settings (
    user_id uuid not null references users(id) on delete cascade,
    key text not null,
    value text not null,
    primary key (user_id, key)
);
