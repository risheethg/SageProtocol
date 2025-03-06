calorie_prompt_template = """<s>[INST] You are an AI assistant that provides nutritional information.  
You will receive the name of a detected food item, and your task is to return the average number of calories per 100 grams of that food.  

Food item: {food_name}  
Calories per 100g: [/INST]"""