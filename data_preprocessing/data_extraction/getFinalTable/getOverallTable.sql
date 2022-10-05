--Initial code for the lab portion was retrieved from https://github.com/arnepeine/ventai/blob/main/overalltable_Lab_withventparams.sql
--Initial code for the rest was retrieved from https://github.com/arnepeine/ventai/blob/main/overalltable_withoutLab_withventparams.sql
--Modifications were made when needed for performance improvement, readability or simplification.

DROP table IF EXISTS `OverallTable`;
CREATE table `OverallTable` AS

SELECT merged.subject_id, hadm_id, icustay_id, charttime 
     --vital signs
	 , avg(gcs) as gcs, avg(HeartRate) as HeartRate , avg(SysBP) as SysBP
     , avg(DiasBP) as DiasBP , avg(MeanBP) as MeanBP , avg(SysBP)/avg(HeartRate) as shockindex, avg(RespRate) as RespRate
     , avg(TempC) as TempC , avg(SpO2) as SpO2 
	 --lab values
	 , avg(POTASSIUM) as POTASSIUM , avg(SODIUM) as SODIUM , avg(CHLORIDE) as CHLORIDE , avg(GLUCOSE) as GLUCOSE
	 , avg(BUN) as BUN , avg(CREATININE) as CREATININE , avg(MAGNESIUM) as MAGNESIUM , avg(CALCIUM) as CALCIUM , avg(ionizedcalcium) ionizedcalcium
	 , avg(CARBONDIOXIDE) as CARBONDIOXIDE , avg(SGOT) as SGOT , avg(SGPT) as SGPT , avg(BILIRUBIN) as BILIRUBIN , avg(ALBUMIN) as ALBUMIN 
	 , avg(HEMOGLOBIN) as HEMOGLOBIN , avg(WBC) as WBC , avg(PLATELET) as PLATELET , avg(PTT) as PTT
     , avg(PT) as PT , avg(INR) as INR , avg(PH) as PH , avg(PaO2) as PaO2 , avg(PaCO2) as PaCO2
     , avg(BASE_EXCESS) as BASE_EXCESS , avg(BICARBONATE) as BICARBONATE , avg(LACTATE) as LACTATE 
	 -- multiply by 100 because FiO2 is in a % but should be a fraction. This idea is retrieved from https://github.com/MIT-LCP/mimic-code/blob/master/concepts/firstday/blood-gas-first-day-arterial.sql
	 , avg(PaO2)/avg(Fio2)*100 as PaO2FiO2ratio 
	 , avg(BANDS) as BANDS 
	 --fluids
	 , avg(urineoutput) as urineoutput, avg(iv_total) as iv_total, avg(cum_fluid_balance) as cum_fluid_balance
	 , avg(rate_norepinephrine) as rate_norepinephrine , avg(rate_epinephrine) as rate_epinephrine 
	 , avg(rate_phenylephrine) as rate_phenylephrine , avg(rate_vasopressin) as rate_vasopressin 
	 , avg(rate_dopamine) as rate_dopamine , avg(vaso_total) as vaso_total
	 --ventilation parameters
	 , CAST((avg(mechvent)>0) AS integer) as MechVent, avg(FiO2) as FiO2
         , max(PEEP) as PEEP, max(tidal_volume) as tidal_volume, max(plateau_pressure) as plateau_pressure

FROM
(
SELECT lab.subject_id, lab.hadm_id, lab.icustay_id, lab.charttime
	-- vital signs
	 , CAST(null AS FLOAT64) as gcs, CAST(null AS FLOAT64) as heartrate, CAST(null AS FLOAT64) as sysbp, CAST(null AS FLOAT64) as diasbp, CAST(null AS FLOAT64) as meanbp,  CAST(null AS FLOAT64) as resprate, CAST(null AS FLOAT64) as tempc, CAST(null AS FLOAT64) as spo2 
	--lab values 
	 , POTASSIUM , SODIUM , CHLORIDE , GLUCOSE , BUN , CREATININE , MAGNESIUM , CALCIUM , CARBONDIOXIDE 
	 , BILIRUBIN , ALBUMIN , HEMOGLOBIN , WBC , PLATELET , PTT , PT , INR , PH , PaO2 , PaCO2
     , BASE_EXCESS , BICARBONATE , LACTATE , BANDS, SGOT , SGPT , IONIZEDCALCIUM
	-- fluids
	 , CAST(null AS FLOAT64) as urineoutput, CAST(null AS FLOAT64) as iv_total, CAST(null AS FLOAT64) as cum_fluid_balance
	 , CAST(null AS FLOAT64) as rate_norepinephrine , CAST(null AS FLOAT64) as rate_epinephrine 
	 , CAST(null AS FLOAT64) as rate_phenylephrine , CAST(null AS FLOAT64) as rate_vasopressin 
	 , CAST(null AS FLOAT64) as rate_dopamine , CAST(null AS FLOAT64) as vaso_total
	--ventilation parameters
	 , CAST(null AS INT64) as MechVent , CAST(null AS FLOAT64) as FiO2
	 , CAST(null AS FLOAT64) as PEEP, CAST(null AS FLOAT64) as tidal_volume, CAST(null AS FLOAT64) as plateau_pressure
FROM `getAllLabvalues` lab 
UNION ALL
SELECT subject_id, hadm_id, icustay_id, charttime
	 -- vital signs
	 , gcs, heartrate, sysbp, diasbp, meanbp, resprate, tempc, spo2 
	 --lab values
	 , CAST(null AS FLOAT64) as POTASSIUM , CAST(null AS FLOAT64) as SODIUM , CAST(null AS FLOAT64) as CHLORIDE , CAST(null AS FLOAT64) as GLUCOSE , CAST(null AS FLOAT64) as BUN , CAST(null AS FLOAT64) as CREATININE , CAST(null AS FLOAT64) as MAGNESIUM , CAST(null AS FLOAT64) as IONIZEDCALCIUM , CAST(null AS FLOAT64) as CALCIUM , CAST(null AS FLOAT64) as CARBONDIOXIDE 
	 , CAST(null AS FLOAT64) as SGOT , CAST(null AS FLOAT64) as SGPT , CAST(null AS FLOAT64) as BILIRUBIN , CAST(null AS FLOAT64) as ALBUMIN , CAST(null AS FLOAT64) as HEMOGLOBIN , CAST(null AS FLOAT64) as WBC , CAST(null AS FLOAT64) as PLATELET , CAST(null AS FLOAT64) as PTT , CAST(null AS FLOAT64) as PT , CAST(null AS FLOAT64) as INR , CAST(null AS FLOAT64) as PH , CAST(null AS FLOAT64) as PaO2 , CAST(null AS FLOAT64) as PaCO2
     , CAST(null AS FLOAT64) as BASE_EXCESS , CAST(null AS FLOAT64) as BICARBONATE , CAST(null AS FLOAT64) as LACTATE , CAST(null AS FLOAT64) as BANDS
	-- fluids
	 , CAST(null AS FLOAT64) as urineoutput, CAST(null AS FLOAT64) as iv_total, CAST(null AS FLOAT64) as cum_fluid_balance
	 , CAST(null AS FLOAT64) as rate_norepinephrine , CAST(null AS FLOAT64) as rate_epinephrine 
	 , CAST(null AS FLOAT64) as rate_phenylephrine , CAST(null AS FLOAT64) as rate_vasopressin 
	 , CAST(null AS FLOAT64) as rate_dopamine , CAST(null AS FLOAT64) as vaso_total
	--ventilation parameters
	 , CAST(null AS INT64) as MechVent , CAST(null AS FLOAT64) as FiO2
	 , CAST(null AS FLOAT64) as PEEP, CAST(null AS FLOAT64) as tidal_volume, CAST(null AS FLOAT64) as plateau_pressure		
FROM `getAllVitalSigns` vit
UNION ALL
SELECT subject_id, hadm_id, icustay_id, charttime
	-- vital signs
	 , null as gcs, null as heartrate, null as sysbp, null as diasbp, null as meanbp,  null as resprate, null as tempc, null as spo2 
     --lab values
	 , CAST(null AS FLOAT64) as POTASSIUM , CAST(null AS FLOAT64) as SODIUM , CAST(null AS FLOAT64) as CHLORIDE , CAST(null AS FLOAT64) as GLUCOSE , CAST(null AS FLOAT64) as BUN , CAST(null AS FLOAT64) as CREATININE , CAST(null AS FLOAT64) as MAGNESIUM , CAST(null AS FLOAT64) as IONIZEDCALCIUM , CAST(null AS FLOAT64) as CALCIUM , CAST(null AS FLOAT64) as CARBONDIOXIDE 
	 , CAST(null AS FLOAT64) as SGOT , CAST(null AS FLOAT64) as SGPT , CAST(null AS FLOAT64) as BILIRUBIN , CAST(null AS FLOAT64) as ALBUMIN , CAST(null AS FLOAT64) as HEMOGLOBIN , CAST(null AS FLOAT64) as WBC , CAST(null AS FLOAT64) as PLATELET , CAST(null AS FLOAT64) as PTT , CAST(null AS FLOAT64) as PT , CAST(null AS FLOAT64) as INR , CAST(null AS FLOAT64) as PH , CAST(null AS FLOAT64) as PaO2 , CAST(null AS FLOAT64) as PaCO2
     , CAST(null AS FLOAT64) as BASE_EXCESS , CAST(null AS FLOAT64) as BICARBONATE , CAST(null AS FLOAT64) as LACTATE , CAST(null AS FLOAT64) as BANDS
	-- fluids
	 , urineoutput, iv_total, cum_fluid_balance
	 , rate_norepinephrine , rate_epinephrine , rate_phenylephrine 
	 , rate_vasopressin , rate_dopamine , vaso_total
	--ventilation parameters
	 , CAST(null AS INT64) as MechVent , CAST(null AS FLOAT64) as FiO2
	 , CAST(null AS FLOAT64) as PEEP, CAST(null AS FLOAT64) as tidal_volume, CAST(null AS FLOAT64) as plateau_pressure
FROM `getAllFluids` fl	
UNION ALL
SELECT subject_id, hadm_id, icustay_id, charttime
	 -- vital signs
	 , null as gcs, null as heartrate, null as sysbp, null as diasbp, null as meanbp, null as resprate, null as tempc, null as spo2 
	 --lab values
	 , CAST(null AS FLOAT64) as POTASSIUM , CAST(null AS FLOAT64) as SODIUM , CAST(null AS FLOAT64) as CHLORIDE , CAST(null AS FLOAT64) as GLUCOSE , CAST(null AS FLOAT64) as BUN , CAST(null AS FLOAT64) as CREATININE , CAST(null AS FLOAT64) as MAGNESIUM , CAST(null AS FLOAT64) as IONIZEDCALCIUM , CAST(null AS FLOAT64) as CALCIUM , CAST(null AS FLOAT64) as CARBONDIOXIDE 
	 , CAST(null AS FLOAT64) as SGOT , CAST(null AS FLOAT64) as SGPT , CAST(null AS FLOAT64) as BILIRUBIN , CAST(null AS FLOAT64) as ALBUMIN , CAST(null AS FLOAT64) as HEMOGLOBIN , CAST(null AS FLOAT64) as WBC , CAST(null AS FLOAT64) as PLATELET , CAST(null AS FLOAT64) as PTT , CAST(null AS FLOAT64) as PT , CAST(null AS FLOAT64) as INR , CAST(null AS FLOAT64) as PH , CAST(null AS FLOAT64) as PaO2 , CAST(null AS FLOAT64) as PaCO2
     , CAST(null AS FLOAT64) as BASE_EXCESS , CAST(null AS FLOAT64) as BICARBONATE , CAST(null AS FLOAT64) as LACTATE , CAST(null AS FLOAT64) as BANDS
	-- fluids
	 , CAST(null AS FLOAT64) as urineoutput, CAST(null AS FLOAT64) as iv_total, CAST(null AS FLOAT64) as cum_fluid_balance
	 , CAST(null AS FLOAT64) as rate_norepinephrine , CAST(null AS FLOAT64) as rate_epinephrine 
	 , CAST(null AS FLOAT64) as rate_phenylephrine , CAST(null AS FLOAT64) as rate_vasopressin 
	 , CAST(null AS FLOAT64) as rate_dopamine , CAST(null AS FLOAT64) as vaso_total
	--ventilation parameters
	 , MechVent , fio2_chartevents as FiO2
	 , PEEP as PEEP, tidal_volume as tidal_volume, plateau_pressure as plateau_pressure	
FROM `getAllVentilationparams` cumflu

) merged 


group by subject_id, hadm_id, icustay_id, charttime	
order by subject_id, hadm_id, icustay_id, charttime
