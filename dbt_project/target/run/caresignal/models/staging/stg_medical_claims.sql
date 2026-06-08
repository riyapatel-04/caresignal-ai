

  create or replace view `caresignal-ai`.`caresignal_dev_staging`.`stg_medical_claims`
  OPTIONS()
  as with source as (
    select * from `caresignal-ai.caresignal_dev.raw_medical_claims`
),

renamed as (
    select
        claim_id,
        beneficiary_id,
        claim_type,
        date(visit_date) as visit_date,
        diagnosis_code,
        diagnosis_description,
        total_charge_amount,
        medicare_payment_amount,
        provider_state,
        case
            when claim_type = 'ER' then true
            else false
        end as is_er_visit,
        case
            when claim_type = 'Inpatient' then true
            else false
        end as is_inpatient
    from source
)

select * from renamed;

