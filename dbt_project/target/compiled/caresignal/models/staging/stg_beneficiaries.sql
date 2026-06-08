with source as (
    select * from `caresignal-ai.caresignal_dev.raw_beneficiaries`
),

renamed as (
    select
        beneficiary_id,
        first_name,
        last_name,
        date(date_of_birth) as date_of_birth,
        gender,
        state,
        zip_code,
        primary_condition,
        cast(has_diabetes as bool) as has_diabetes,
        cast(has_hypertension as bool) as has_hypertension,
        cast(has_heart_disease as bool) as has_heart_disease,
        date_diff(current_date(), date(date_of_birth), year) as age
    from source
)

select * from renamed