create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path to 'public'
as $$
declare
  base_username text;
  final_username text;
begin
  base_username := split_part(new.email, '@', 1);
  final_username := base_username;

  if exists (select 1 from public.users where username = final_username) then
    final_username := base_username || '_' || substr(md5(new.id::text), 1, 6);
  end if;

  insert into public.users (id, username)
  values (new.id, final_username);
  return new;
end;
$$;

delete from public.users where id not in (select id from auth.users);
