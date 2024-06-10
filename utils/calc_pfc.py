def calc_pfc(personal_info):
    if personal_info["gender"] == "男性":
        bmr = 88.362 + (13.397 * personal_info["weight"]) + (4.799 * personal_info["height"]) - (5.677 * personal_info["age"])
    else:
        bmr = 447.593 + (9.247 * personal_info["weight"]) + (3.098 * personal_info["height"]) - (4.330 * personal_info["age"])

    activity_factors = {
        "ほとんど運動しない": 1.2,
        "軽い運動をする": 1.375,
        "中程度の運動をする": 1.55,
        "活発に運動をする": 1.725,
        "非常に激しい運動をする": 1.9
    }

    tdee = bmr * activity_factors[personal_info["activity_level"]]

    if personal_info["goal"] == "減量":
        target_calories = tdee - 500
        p_ratio, f_ratio, c_ratio = 0.30, 0.25, 0.45
    elif personal_info["goal"] == "現状維持":
        target_calories = tdee
        p_ratio, f_ratio, c_ratio = 0.25, 0.25, 0.50
    else: # 増量
        target_calories = tdee + 500
        p_ratio, f_ratio, c_ratio = 0.20, 0.25, 0.55

    p_grams = (target_calories * p_ratio) / 4
    f_grams = (target_calories * f_ratio) / 9
    c_grams = (target_calories * c_ratio) / 4

    return {
        "target_calories": target_calories,
        "p_grams": p_grams,
        "f_grams": f_grams,
        "c_grams": c_grams
        }