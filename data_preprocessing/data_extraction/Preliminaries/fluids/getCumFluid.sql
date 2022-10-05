--Initial code was retrieved from https://github.com/arnepeine/ventai/blob/main/getCumFluid.sql
--Modifications were made when needed for performance improvement, readability or simplification.

DROP table IF EXISTS `getCumFluid`;
CREATE table `getCumFluid` as 

--Input events for CareVue patients.

SELECT subject_id, hadm_id, icustay_id, charttime, in_amount, in_cum_amt, out_amount, out_cum_amt,
       sum(out_amount) OVER (PARTITION BY in_out.icustay_id ORDER BY charttime)
	   -sum(in_amount) OVER (PARTITION BY in_out.icustay_id ORDER BY charttime) as cum_fluid_balance
FROM(

SELECT subject_id, hadm_id,merged.icustay_id,charttime, in_amount,
       sum(in_amount) OVER (PARTITION BY merged.icustay_id ORDER BY charttime) AS in_cum_amt,--,valueuom
	   CAST(null AS FLOAT64) AS out_amount, CAST(null AS FLOAT64) AS out_cum_amt
FROM (
	SELECT icustay_id, charttime, 
	--Unit conversion is not necessary for CareVue patients since they are either in cc or mL which are equivalent units.
	sum(amount) as in_amount
	FROM `physionet-data.mimiciii_clinical.inputevents_cv` inevcv
	WHERE amountuom in ('cc','ml')
	GROUP BY icustay_id,charttime) as merged
INNER JOIN `physionet-data.mimiciii_clinical.icustays` ic
ON ic.icustay_id=merged.icustay_id


UNION ALL

--Input events for MetaVision patients.

SELECT subject_id, hadm_id,merged.icustay_id,charttime, in_amount,
       sum(in_amount) OVER (PARTITION BY merged.icustay_id ORDER BY charttime) AS cum_amt,
	   CAST(null AS FLOAT64) AS out_amount, CAST(null AS FLOAT64) AS out_cum_amt--,valueuom
FROM (
	SELECT icustay_id, starttime as charttime, 
	--Some unit conversions that will end up in 'mL'.
	(CASE WHEN amountuom='ml' THEN sum(amount) 
	      WHEN amountuom='L'  THEN sum(amount)*0.001 
	      WHEN amountuom='uL' THEN sum(amount)*1000  END) as in_amount
	FROM `physionet-data.mimiciii_clinical.inputevents_mv` inevmv
	WHERE amountuom in ('L','ml','uL')
	GROUP BY icustay_id,charttime,amountuom) as merged
INNER JOIN `physionet-data.mimiciii_clinical.icustays` ic
ON ic.icustay_id=merged.icustay_id

UNION ALL

--Output events.

SELECT subject_id, hadm_id,merged.icustay_id, charttime, 
       CAST(null AS FLOAT64) AS in_amount, CAST(null AS FLOAT64) AS in_cum_amt, out_amount,
       sum(out_amount) OVER (PARTITION BY merged.icustay_id ORDER BY charttime) AS out_cum_amt--,valueuom
FROM (
	SELECT icustay_id, charttime, sum(value) as out_amount
	FROM `physionet-data.mimiciii_clinical.outputevents` outev
	WHERE valueuom in ('mL','ml')
	GROUP BY icustay_id,charttime) as merged
INNER JOIN `physionet-data.mimiciii_clinical.icustays` ic
ON ic.icustay_id=merged.icustay_id
	) AS in_out

ORDER BY icustay_id,charttime
