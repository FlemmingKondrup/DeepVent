DROP table IF EXISTS `getAllFluids`;
CREATE table `getAllFluids` AS

SELECT subject_id, hadm_id, icustay_id, charttime,
	 --urine output
       avg(urineoutput) as urineoutput
	 -- vasopressors
	 , avg(rate_norepinephrine) as rate_norepinephrine , avg(rate_epinephrine) as rate_epinephrine 
	 , avg(rate_phenylephrine) as rate_phenylephrine , avg(rate_vasopressin) as rate_vasopressin 
	 , avg(rate_dopamine) as rate_dopamine , avg(vaso_total) as vaso_total
	 -- intravenous fluids
	 , avg(iv_total) as iv_total
	 -- cumulated fluid balance
	 , avg(cum_fluid_balance) as cum_fluid_balance
FROM 
(
( SELECT subject_id, hadm_id, icustay_id, charttime
         , urineoutput
         , CAST(null AS FLOAT64) as rate_norepinephrine , CAST(null AS FLOAT64) as rate_epinephrine 
	 , CAST(null AS FLOAT64) as rate_phenylephrine , CAST(null AS FLOAT64) as rate_vasopressin 
	 , CAST(null AS FLOAT64) as rate_dopamine , CAST(null AS FLOAT64) as vaso_total
	 , CAST(null AS FLOAT64) as iv_total
	 , CAST(null AS FLOAT64) as cum_fluid_balance
FROM `getUrineOutput`)
UNION ALL
( SELECT ic.subject_id, ic.hadm_id, ic.icustay_id, starttime as charttime
         , CAST(null AS FLOAT64) as urineoutput
         , rate_norepinephrine , rate_epinephrine 
	 , rate_phenylephrine , rate_vasopressin 
	 , rate_dopamine , vaso_total
	 , CAST(null AS FLOAT64) as iv_total
	 , CAST(null AS FLOAT64) as cum_fluid_balance
FROM `getVasopressors` vp INNER JOIN `physionet-data.mimiciii_clinical.icustays` ic
ON vp.icustay_id=ic.icustay_id
)
UNION ALL
( SELECT subject_id, hadm_id, icustay_id, charttime
         , CAST(null AS FLOAT64) as urineoutput
         , CAST(null AS FLOAT64) as rate_norepinephrine , CAST(null AS FLOAT64) as rate_epinephrine 
	 , CAST(null AS FLOAT64) as rate_phenylephrine , CAST(null AS FLOAT64) as rate_vasopressin 
	 , CAST(null AS FLOAT64) as rate_dopamine , CAST(null AS FLOAT64) as vaso_total
	 , amount as iv_total
	 , CAST(null AS FLOAT64) as cum_fluid_balance
FROM `getIntravenous`)
UNION ALL
( SELECT subject_id, hadm_id, icustay_id, charttime
         , CAST(null AS FLOAT64) as urineoutput
         , CAST(null AS FLOAT64) as rate_norepinephrine , CAST(null AS FLOAT64) as rate_epinephrine 
	 , CAST(null AS FLOAT64) as rate_phenylephrine , CAST(null AS FLOAT64) as rate_vasopressin 
	 , CAST(null AS FLOAT64) as rate_dopamine , CAST(null AS FLOAT64) as vaso_total
	 , CAST(null AS FLOAT64) as iv_total
	 , cum_fluid_balance
FROM `getCumFluid`)
)

group by subject_id, hadm_id, icustay_id, charttime	
order by subject_id, hadm_id, icustay_id, charttime
