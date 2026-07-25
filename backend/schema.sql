-- Run this once in Supabase: Project -> SQL Editor -> New query -> Run

create table if not exists companies (
    ticker text primary key,
    name text not null,
    sector text,
    exchange text default 'NSE',
    description text
);

create table if not exists price_history (
    ticker text references companies(ticker),
    date date not null,
    open numeric,
    high numeric,
    low numeric,
    close numeric,
    volume bigint,
    primary key (ticker, date)
);

create table if not exists fundamentals (
    ticker text references companies(ticker),
    as_of_date date not null,
    market_cap numeric,
    pe_ratio numeric,
    eps numeric,
    primary key (ticker, as_of_date)
);

-- Returns the single most recent price row per ticker, in one query
-- instead of the API needing to query once per company.
create or replace function latest_prices()
returns setof price_history as $$
    select distinct on (ticker) *
    from price_history
    order by ticker, date desc;
$$ language sql stable;
