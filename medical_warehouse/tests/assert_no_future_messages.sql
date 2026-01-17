-- We should not have messages from the future
select *
from {{ ref('fct_messages') }}
where message_date > current_timestamp