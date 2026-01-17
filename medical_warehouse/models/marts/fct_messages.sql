with messages as (
    select * from {{ ref('stg_telegram_messages') }}
),

channels as (
    select * from {{ ref('dim_channels') }}
)

select
    m.message_id,
    c.channel_key,
    -- Create date key integer (YYYYMMDD) to join with dim_dates later
    to_char(m.message_date, 'YYYYMMDD')::int as date_key,
    m.message_date,
    m.message_text,
    m.message_length,
    m.has_media,
    m.views as view_count,
    m.forwards as forward_count
from messages m
left join channels c on m.channel_name = c.channel_name