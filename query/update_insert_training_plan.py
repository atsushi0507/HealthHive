def update_insert_training_plan(user_id, date, training_plan):
    project_id = "health-hive-data"
    dataset_id = "excercise_management"
    table_id = "suggested_train_plans"
    query=f"""
    MERGE `{project_id}.{dataset_id}.{table_id}` AS T
    USING(
        SELECT
            '{user_id}' AS user_id,
            DATE('{date}') AS date,
            `{training_plan}` AS training_plan
    ) AS S
    ON
        T.user_id = S.user_id
        AND
        T.date = S.date
    WHEN MATCHED THEN
        UPDATE SET
            training_plan = S.training_plan
    WHEN NOT MATCHED THEN
        INSERT (user_id, date, training_plan)
        VALUES (user_id, date, training_plan)
    """
    return query
