{{ config(materialized='table') }}

SELECT
*
FROM PUBLIC.users
