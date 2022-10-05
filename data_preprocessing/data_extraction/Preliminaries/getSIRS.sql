--Initial code was retrieved https://github.com/arnepeine/ventai/blob/main/getSIRS_withventparams.sql.
--Modifications were made when needed for performance improvement, readability or simplification.

DROP table IF EXISTS `SIRS`;
CREATE table `SIRS` AS

with scorecomp as(

SELECT icustay_id, subject_id , hadm_id,  start_time, tempC , heartrate , resprate , paco2 , wbc , bands
FROM `OverallTable2`),

scorecalc as
( SELECT icustay_id, subject_id , hadm_id, start_time, tempC , heartrate , resprate , paco2 , wbc , bands
 , case
      when Tempc < 36.0 then 1
      when Tempc > 38.0 then 1
      when Tempc is null then null
      else 0
    end as Temp_score
, case
      when HeartRate > 90.0  then 1
      when HeartRate is null then null
      else 0
    end as HeartRate_score
, case
      when RespRate > 20.0  then 1
      when PaCO2 < 32.0  then 1
      when coalesce(RespRate, PaCO2) is null then null
      else 0
    end as Resp_score
, case
      when WBC <  4.0  then 1
      when WBC > 12.0  then 1
      when Bands > 10 then 1-- > 10% immature neurophils (band forms)
      when coalesce(WBC, Bands) is null then null
      else 0
    end as WBC_score
 
 from scorecomp
)

select
  icustay_id, subject_id , hadm_id, start_time
  -- Combine all the scores to get SIRS
  -- Impute 0 if the score is missing
  , coalesce(Temp_score,0)
  + coalesce(HeartRate_score,0)
  + coalesce(Resp_score,0)
  + coalesce(WBC_score,0)
    as SIRS
  , Temp_score, HeartRate_score, Resp_score, WBC_score
from scorecalc;
