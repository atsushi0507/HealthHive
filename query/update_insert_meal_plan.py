def update_insert_meal_plans(user_id, date, breakfast, lunch, dinner):
    project_id = "health-hive-data"
    dataset_id = "diet_health_management"
    table_id = "suggested_meal_plans"
    query = f"""
    MERGE `{project_id}.{dataset_id}.{table_id}` AS T
    USING (
        SELECT
            '{user_id}' AS user_id,
            DATE('{date}') AS date,
            '{breakfast}' AS breakfast,
            '{lunch}' AS lunch,
            '{dinner}' AS dinner
    ) AS S
    ON
        T.user_id = S.user_id
        AND
        T.date = DATE(S.date)
    WHEN MATCHED THEN
        UPDATE SET
            breakfast = S.breakfast,
            lunch = S.lunch,
            dinner = S.dinner
    WHEN NOT MATCHED THEN
        INSERT (user_id, date, breakfast, lunch, dinner)
        VALUES (user_id, date, breakfast, lunch, dinner)
    """
    return query
