calorie_prompt_template = """<s>[INST] You are an AI assistant that provides nutritional information.  
You will receive a list of detected food items, and your task is to return the average number of calories per 100 grams for each food item.  

Food items: {food_list}  

Provide the output in the following format:  
Food 1: X calories per 100gs
Food 2: Y calories per 100g  
...  
[/INST]"""