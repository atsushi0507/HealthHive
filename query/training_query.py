def update_insert_training_plan(user_id, date, workout, duration):
    project_id = "health-hive-data"
    dataset_id = "exercise_management"
    table_id = "suggested_training_plans"
    query = f"""
    MERGE `{project_id}.{dataset_id}.{table_id}` AS T
    USING(
        SELECT
            '{user_id}' AS user_id,
            DATE('{date}') AS date,
            '{workout}' AS workout,
            '{duration}' AS duration
    ) AS S
    ON
        T.user_id = S.user_id
        AND
        T.date = S.date
    WHEN MATCHED THEN
        UPDATE SET
            workout = S.workout,
            duration = S.duration
    WHEN NOT MATCHED THEN
        INSERT (user_id, date, workout, duration)
        VALUES (user_id, date, workout, duration)
    """
    return query


def update_insert_training_log(user_id, date, workout, duration):
    project_id = "health-hive-data"
    dataset_id = "exercise_management"
    table_id = "workout_logs"
    query = f"""
    MERGE `{project_id}.{dataset_id}.{table_id}` AS T
    USING (
        SELECT
            '{user_id}' AS user_id,
            DATE('{date}') AS date,
            '{workout}' AS workout,
            {duration} AS duration
    ) AS S
    ON
        T.user_id = S.user_id
        AND
        T.date = S.date
        AND
        T.workout = S.workout
    WHEN MATCHED THEN
        UPDATE SET
            duration = S.duration
    WHEN NOT MATCHED THEN
        INSERT (user_id, date, workout, duration)
        VALUES (user_id, date, workout, duration)
    """
    return query


def read_train_log(user_id):
    project_id = "health-hive-data"
    dataset_id = "exercise_management"
    table_id = "workout_logs"
    query = f"""
    SELECT
        date,
        workout,
        duration
    FROM
        `{project_id}.{dataset_id}.{table_id}`
    WHERE
        user_id = '{user_id}'
    ORDER BY
        date
    """
    return query