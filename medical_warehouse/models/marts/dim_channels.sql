with stg_messages as (
    select * from {{ ref('stg_telegram_messages') }}
),

channel_stats as (
    select
        channel_name,
        min(message_date) as first_post_date,
        max(message_date) as last_post_date,
        count(*) as total_posts,
        avg(views) as avg_views
    from stg_messages
    group by channel_name
)

select
    -- Generate a surrogate key (hash of channel name)
    {{ dbt_utils.generate_surrogate_key(['channel_name']) }} as channel_key,
    channel_name,
    case 
        when channel_name ilike '%cosmetics%' then 'Cosmetics'
        when channel_name ilike '%pharma%' then 'Pharmaceutical'
        else 'Medical/Other'
    end as channel_type,
    first_post_date,
    last_post_date,
    total_posts,
    round(avg_views::numeric, 2) as avg_views
from channel_stats