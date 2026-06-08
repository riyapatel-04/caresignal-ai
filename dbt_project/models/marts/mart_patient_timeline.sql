with beneficiaries as (
    select * from {{ ref('stg_beneficiaries') }}
),

pharmacy as (
    select
        beneficiary_id,
        count(*) as total_prescriptions,
        countif(missed_refill = true) as total_missed_refills,
        round(safe_divide(
            countif(missed_refill = false),
            count(*)
        ), 2) as pdc_score,
        max(fill_date) as last_fill_date,
        min(fill_date) as first_fill_date,
        string_agg(distinct drug_name, ', ') as drugs_prescribed
    from {{ ref('stg_pharmacy_claims') }}
    group by beneficiary_id
),

medical as (
    select
        beneficiary_id,
        count(*) as total_medical_claims,
        countif(is_er_visit = true) as total_er_visits,
        countif(is_inpatient = true) as total_inpatient_visits,
        max(visit_date) as last_visit_date,
        round(sum(total_charge_amount), 2) as total_charge_amount
    from {{ ref('stg_medical_claims') }}
    group by beneficiary_id
),

final as (
    select
        b.beneficiary_id,
        b.first_name,
        b.last_name,
        b.date_of_birth,
        b.age,
        b.gender,
        b.state,
        b.primary_condition,
        b.has_diabetes,
        b.has_hypertension,
        b.has_heart_disease,
        coalesce(p.total_prescriptions, 0) as total_prescriptions,
        coalesce(p.total_missed_refills, 0) as total_missed_refills,
        coalesce(p.pdc_score, 0) as pdc_score,
        p.last_fill_date,
        p.first_fill_date,
        p.drugs_prescribed,
        coalesce(m.total_medical_claims, 0) as total_medical_claims,
        coalesce(m.total_er_visits, 0) as total_er_visits,
        coalesce(m.total_inpatient_visits, 0) as total_inpatient_visits,
        m.last_visit_date,
        coalesce(m.total_charge_amount, 0) as total_charge_amount,
        case
            when coalesce(p.pdc_score, 0) < 0.8 then 'HIGH'
            when coalesce(p.pdc_score, 0) < 0.9 then 'MEDIUM'
            else 'LOW'
        end as adherence_risk_level
    from beneficiaries b
    left join pharmacy p on b.beneficiary_id = p.beneficiary_id
    left join medical m on b.beneficiary_id = m.beneficiary_id
)

select * from final