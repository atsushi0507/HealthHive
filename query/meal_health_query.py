def update_insert_meal_plans(user_id, date, meal_type, menu, weight, calorie):
    project_id = "health-hive-data"
    dataset_id = "diet_health_management"
    table_id = "suggested_meal_plans"
    query = f"""
    MERGE `{project_id}.{dataset_id}.{table_id}` AS T
    USING (
        SELECT
            '{user_id}' AS user_id,
            DATE('{date}') AS date,
            '{meal_type}' AS meal_type,
            '{menu}' AS menu,
            '{weight}' AS weight,
            '{calorie}' AS calorie

    ) AS S
    ON
        T.user_id = S.user_id
        AND
        T.date = DATE(S.date)
        AND
        T.meal_type = S.meal_type
    WHEN MATCHED THEN
        UPDATE SET
            menu = S.menu,
            weight = S.weight,
            calorie = S.calorie
    WHEN NOT MATCHED THEN
        INSERT (user_id, date, meal_type, menu, weight, calorie)
        VALUES (user_id, date, meal_type, menu, weight, calorie)
    """
    return query


def update_insert_health_log(user_id, date, weight, body_fat):
    project_id = "health-hive-data"
    dataset_id = "diet_health_management"
    table_id = "daily_body_metrics"
    query = f"""
    MERGE `{project_id}.{dataset_id}.{table_id}` AS T
    USING (
        SELECT
            '{user_id}' AS user_id,
            DATE('{date}') AS date,
            {weight} AS weight,
            {body_fat} AS body_fat
    ) AS S
    ON
        T.user_id = S.user_id
        AND
        T.date = S.date
    WHEN MATCHED THEN
        UPDATE SET
            weight = S.weight,
            body_fat = S.body_fat
    WHEN NOT MATCHED THEN
        INSERT (user_id, date, weight, body_fat)
        VALUES (user_id, date, weight, body_fat)
    """
    return query


def update_insert_meal_log(user_id, date, meal_type, menu):
    project_id = "health-hive-data"
    dataset_id = "diet_health_management"
    table_id = "consumed_meals"
    query = f"""
    MERGE `{project_id}.{dataset_id}.{table_id}` AS T
    USING (
        SELECT
            '{user_id}' AS user_id,
            DATE('{date}') AS date,
            '{meal_type}' AS meal_type,
            '{menu}' AS menu
    ) AS S
    ON
        T.user_id = S.user_id
        AND
        T.date = S.date
        AND
        T.meal_type = S.meal_type
    WHEN MATCHED THEN
        UPDATE SET
        menu = S.menu
    WHEN NOT MATCHED THEN
        INSERT (user_id, date, meal_type, menu)
        VALUES (user_id, date, meal_type, menu)
    """
    return query


def read_body_log(user_id):
    project_id = "health-hive-data"
    dataset_id = "diet_health_management"
    table_id = "daily_body_metrics"
    query = f"""
    SELECT
        date,
        weight,
        body_fat
    FROM
        `{project_id}.{dataset_id}.{table_id}`
    WHERE
        user_id = '{user_id}'
    ORDER BY
        date
    """
    return query