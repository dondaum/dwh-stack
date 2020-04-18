{{ config(materialized='table') }}

SELECT
domain AS VALUE_TYPE,
email,
'domain' AS typename
FROM {{ ref('EXTRACT_EMAIL') }}
UNION ALL
SELECT
USERNAME AS VALUE_TYPE,
email,
'USERNAME' AS typename
FROM {{ ref('EXTRA_USER_EMAIL') }}