What column exist: 
create table public.sellout_entries2 (
  id uuid not null default gen_random_uuid (),
  product_ean text null,
  month integer null,
  year integer null,
  quantity integer null,
  sales_lc text null,
  sales_eur numeric null,
  currency text null,
  created_at timestamp without time zone null default now(),
  reseller text null,
  functional_name text null,
  upload_id uuid null,
  constraint sellout_entries2_pkey primary key (id),
  constraint sellout_entries2_product_ean_fkey foreign KEY (product_ean) references products (ean),
  constraint sellout_entries2_upload_id_fkey foreign KEY (upload_id) references uploads (id) on delete set null,
  constraint sellout_entries_month_check check (
    (
      (month >= 1)
      and (month <= 12)
    )
  ),
  constraint sellout_entries_year_check check ((year >= 2000))
) TABLESPACE pg_default;

create index IF not exists idx_sellout_entries2_product_ean on public.sellout_entries2 using btree (product_ean) TABLESPACE pg_default;

create index IF not exists idx_sellout_entries2_reseller on public.sellout_entries2 using btree (reseller) TABLESPACE pg_default;

create trigger trg_fill_sales_eur_aromateque BEFORE INSERT
or
update on sellout_entries2 for EACH row
execute FUNCTION fill_sales_eur_aromateque ();








column: functional_name should store for a short while.




switch values:
