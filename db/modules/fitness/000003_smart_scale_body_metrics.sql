-- Extend Fitness Coach body metrics with smart-scale body-composition readings.
-- These columns keep frequently used composition values queryable while the
-- original device payload and screenshot/image provenance remain in metadata.

ALTER TABLE fitness.body_metrics
  ADD COLUMN IF NOT EXISTS bmi numeric,
  ADD COLUMN IF NOT EXISTS body_condition_score numeric,
  ADD COLUMN IF NOT EXISTS skeletal_muscle_pct numeric,
  ADD COLUMN IF NOT EXISTS water_pct numeric,
  ADD COLUMN IF NOT EXISTS protein_pct numeric,
  ADD COLUMN IF NOT EXISTS visceral_fat_index numeric,
  ADD COLUMN IF NOT EXISTS bone_mass_pct numeric,
  ADD COLUMN IF NOT EXISTS bmr_kcal numeric,
  ADD COLUMN IF NOT EXISTS biological_age_years numeric,
  ADD COLUMN IF NOT EXISTS fat_weight_kg numeric,
  ADD COLUMN IF NOT EXISTS body_fat_mass_index numeric,
  ADD COLUMN IF NOT EXISTS fat_free_mass_kg numeric,
  ADD COLUMN IF NOT EXISTS weight_change_kg numeric;

COMMENT ON COLUMN fitness.body_metrics.bmi IS 'BMI value supplied by the measurement source, when available.';
COMMENT ON COLUMN fitness.body_metrics.body_condition_score IS 'Vendor/app body condition score from smart scale or wearable source.';
COMMENT ON COLUMN fitness.body_metrics.skeletal_muscle_pct IS 'Skeletal muscle percentage from body-composition scale/source.';
COMMENT ON COLUMN fitness.body_metrics.water_pct IS 'Body water percentage from body-composition scale/source.';
COMMENT ON COLUMN fitness.body_metrics.protein_pct IS 'Body protein percentage from body-composition scale/source.';
COMMENT ON COLUMN fitness.body_metrics.visceral_fat_index IS 'Vendor visceral fat index from body-composition scale/source.';
COMMENT ON COLUMN fitness.body_metrics.bone_mass_pct IS 'Bone mass percentage from body-composition scale/source when reported as percent.';
COMMENT ON COLUMN fitness.body_metrics.bmr_kcal IS 'Basal metabolic rate reported by the source, in kcal/day.';
COMMENT ON COLUMN fitness.body_metrics.biological_age_years IS 'Vendor/app biological/metabolic age estimate in years.';
COMMENT ON COLUMN fitness.body_metrics.fat_weight_kg IS 'Fat mass weight reported by the source, in kilograms.';
COMMENT ON COLUMN fitness.body_metrics.body_fat_mass_index IS 'Vendor/app body fat mass index value.';
COMMENT ON COLUMN fitness.body_metrics.fat_free_mass_kg IS 'Fat-free mass reported by the source, in kilograms.';
COMMENT ON COLUMN fitness.body_metrics.weight_change_kg IS 'Weight delta since previous source measurement, in kilograms.';
