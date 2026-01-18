with source as (
    select * from {{ source('telegram', 'yolo_detections') }}
),

renamed as (
    select
        message_id,
        channel_name,
        image_path,
        detected_objects,
        -- Round confidence to 4 decimal places
        round(cast(best_confidence as numeric), 4) as confidence_score,
        image_category
    from source
)

select * from renamed