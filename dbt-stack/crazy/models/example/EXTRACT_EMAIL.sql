{{ config(materialized='table') }}

SELECT
substring(email from '@(.*)$') as domain,
email
FROM {{ ref('BASE_EMAIL') }}
