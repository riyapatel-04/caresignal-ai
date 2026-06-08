with source as (
    select * from `caresignal-ai.caresignal_dev.raw_pharmacy_claims`
),

renamed as (
    select
        claim_id,
        beneficiary_id,
        drug_name,
        date(fill_date) as fill_date,
        days_supply,
        quantity,
        refill_number,
        cast(missed_refill as bool) as missed_refill,
        prescriber_state,
        total_drug_cost,
        date_add(date(fill_date), interval days_supply day) as next_refill_due_date
    from source
)

select * from renamed