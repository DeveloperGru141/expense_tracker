create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path to 'public'
as $$
begin
  insert into public.users (id, username)
  values (new.id, split_part(new.email, '@', 1));
  return new;
end;
$$;
