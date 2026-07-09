-- Add created_at to expenses table for audit trail
alter table if exists expenses
  add column if not exists created_at timestamp with time zone default timezone('utc'::text, now()) not null;

-- Add created_at to income table for audit trail
alter table if exists income
  add column if not exists created_at timestamp with time zone default timezone('utc'::text, now()) not null;

-- Create frequency enum type for recurring transactions
do $$ begin
  create type transaction_frequency as enum ('daily', 'weekly', 'monthly', 'yearly');
exception
  when duplicate_object then null;
end $$;

-- Add check constraint on recurring_expenses frequency
alter table if exists recurring_expenses
  drop constraint if exists recurring_expenses_frequency_check;

alter table if exists recurring_expenses
  add constraint recurring_expenses_frequency_check
  check (frequency in ('daily', 'weekly', 'monthly', 'yearly'));

alter table if exists recurring_income
  drop constraint if exists recurring_income_frequency_check;

alter table if exists recurring_income
  add constraint recurring_income_frequency_check
  check (frequency in ('daily', 'weekly', 'monthly', 'yearly'));

-- Index on expense_date for faster date-range queries
create index if not exists idx_expenses_date on expenses(expense_date);
create index if not exists idx_income_date on income(income_date);
