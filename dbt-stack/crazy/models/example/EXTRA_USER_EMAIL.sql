{{ config(materialized='table') }}

SELECT
left(email, strpos(email, '@') - 1) as USERNAME,
email
FROM {{ ref('BASE_EMAIL') }}
