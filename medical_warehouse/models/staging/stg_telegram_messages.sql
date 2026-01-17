with source as (
    select * from {{ source('telegram', 'telegram_messages') }}
),

cleaned as (
    select
        id as simple_id,
        message_id,
        channel_name,
        message_date,
        -- Extract just the text, handle nulls
        coalesce(message_text, '') as message_text,
        -- Calculate text length
        length(coalesce(message_text, '')) as message_length,
        has_media,
        image_path,
        -- Handle null views/forwards
        coalesce(views, 0) as views,
        coalesce(forwards, 0) as forwards,
        scraped_at
    from source
    where message_date is not null -- Filter garbage
)

select * from cleaned