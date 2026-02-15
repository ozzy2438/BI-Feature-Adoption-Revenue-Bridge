SELECT *
FROM {{ ref('mart_feature_adoption') }}
WHERE adoption_rate < 0
   OR adoption_rate > 1
