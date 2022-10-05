DROP table IF EXISTS `OverallTable4`;
CREATE table `OverallTable4` AS

SELECT * FROM `OverallTable3`
WHERE mechvent = 1 AND icustay_id IS NOT NULL AND weight < 1000;

ALTER TABLE `OverallTable4`
DROP COLUMN sgot;
ALTER TABLE `OverallTable4`
DROP COLUMN sgpt;
