with detections as (
    select * from {{ ref('stg_yolo_detections') }}
),

messages as (
    -- We join with fct_messages to get the correct foreign keys (channel_key, date_key)
    select 
        message_id, 
        channel_key, 
        date_key 
    from {{ ref('fct_messages') }}
)

select
    d.message_id,
    m.channel_key,
    m.date_key,
    d.image_category,
    d.confidence_score,
    d.detected_objects
from detections d
-- Inner join because we only care about detections that map to valid messages in our warehouse
inner join messages m on d.message_id = m.message_id