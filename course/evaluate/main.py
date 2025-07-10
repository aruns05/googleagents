PROJECT_ID = "energymgmt-461218"  # @param {type:"string"}
LOCATION = "us-central1"  # @param {type:"string"}


if not PROJECT_ID or PROJECT_ID == "[your-project-id]":
    raise ValueError("Please set your PROJECT_ID")

import vertexai

vertexai.init(project=PROJECT_ID, location=LOCATION)

import pandas as pd
from vertexai.evaluation import EvalTask
from vertexai.generative_models import GenerativeModel, HarmBlockThreshold, HarmCategory
from vertexai.preview.evaluation import notebook_utils

system_instruction = "You are a poetic assistant, skilled in explaining complex concepts with creative flair."
question = "How does LLM work?"
requirements = "Explain concepts in great depth using simple terms, and give examples to help people learn. At the end of each explanation, you ask a question to check for understanding"

prompt_template = f"{system_instruction} Answer this question: {question}, and follow the requirements: {requirements}."


model_response = (
    GenerativeModel("gemini-2.0-flash")
    .generate_content(prompt_template)
    .candidates[0]
    .content.parts[0]
    .text
)


print(f"Assembled Prompt:{prompt_template}")
print(f"Model Response: ")
print(model_response)



instruction = "Summarize the following article"

context = [
    "To make a classic spaghetti carbonara, start by bringing a large pot of salted water to a boil. While the water is heating up, cook pancetta or guanciale in a skillet with olive oil over medium heat until it's crispy and golden brown. Once the pancetta is done, remove it from the skillet and set it aside. In the same skillet, whisk together eggs, grated Parmesan cheese, and black pepper to make the sauce. When the pasta is cooked al dente, drain it and immediately toss it in the skillet with the egg mixture, adding a splash of the pasta cooking water to create a creamy sauce.",
    "Preparing a perfect risotto requires patience and attention to detail. Begin by heating butter in a large, heavy-bottomed pot over medium heat. Add finely chopped onions and minced garlic to the pot, and cook until they're soft and translucent, about 5 minutes. Next, add Arborio rice to the pot and cook, stirring constantly, until the grains are coated with the butter and begin to toast slightly. Pour in a splash of white wine and cook until it's absorbed. From there, gradually add hot chicken or vegetable broth to the rice, stirring frequently, until the risotto is creamy and the rice is tender with a slight bite.",
    "For a flavorful grilled steak, start by choosing a well-marbled cut of beef like ribeye or New York strip. Season the steak generously with kosher salt and freshly ground black pepper on both sides, pressing the seasoning into the meat. Preheat a grill to high heat and brush the grates with oil to prevent sticking. Place the seasoned steak on the grill and cook for about 4-5 minutes on each side for medium-rare, or adjust the cooking time to your desired level of doneness. Let the steak rest for a few minutes before slicing against the grain and serving.",
    "Creating a creamy homemade tomato soup is a comforting and simple process. Begin by heating olive oil in a large pot over medium heat. Add diced onions and minced garlic to the pot and cook until they're soft and fragrant. Next, add chopped fresh tomatoes, chicken or vegetable broth, and a sprig of fresh basil to the pot. Simmer the soup for about 20-30 minutes, or until the tomatoes are tender and falling apart. Remove the basil sprig and use an immersion blender to puree the soup until smooth. Season with salt and pepper to taste before serving.",
    "To bake a decadent chocolate cake from scratch, start by preheating your oven to 350°F (175°C) and greasing and flouring two 9-inch round cake pans. In a large mixing bowl, cream together softened butter and granulated sugar until light and fluffy. Beat in eggs one at a time, making sure each egg is fully incorporated before adding the next. In a separate bowl, sift together all-purpose flour, cocoa powder, baking powder, baking soda, and salt. Divide the batter evenly between the prepared cake pans and bake for 25-30 minutes, or until a toothpick inserted into the center comes out clean.",
]

reference = [
    "The process of making spaghetti carbonara involves boiling pasta, crisping pancetta or guanciale, whisking together eggs and Parmesan cheese, and tossing everything together to create a creamy sauce.",
    "Preparing risotto entails sautéing onions and garlic, toasting Arborio rice, adding wine and broth gradually, and stirring until creamy and tender.",
    "Grilling a flavorful steak involves seasoning generously, preheating the grill, cooking to desired doneness, and letting it rest before slicing.",
    "Creating homemade tomato soup includes sautéing onions and garlic, simmering with tomatoes and broth, pureeing until smooth, and seasoning to taste.",
    "Baking a decadent chocolate cake requires creaming butter and sugar, beating in eggs and alternating dry ingredients with buttermilk before baking until done.",
]

eval_dataset = pd.DataFrame(
    {
        "context": context,
        "reference": reference,
        "instruction": [instruction] * len(context),
    }
)


prompt_templates = [
    "Instruction: {instruction}. Article: {context}. Summary:",
    "Article: {context}. Complete this task: {instruction}, in one sentence. Summary:",
    "Goal: {instruction} and give me a TLDR. Here's an article: {context}. Summary:",
]
    
    
    
generation_config = {
    "temperature": 0.3,
}

safety_settings = {
    HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
}

gemini_model = GenerativeModel(
    "gemini-2.0-flash",
    generation_config=generation_config,
    safety_settings=safety_settings,
)


experiment_name = "eval-sdk-prompt-engineering"  # @param {type:"string"}
metrics = [
    "rouge_1",
    "rouge_l_sum",
    "bleu",
    "fluency",
    "coherence",
    "safety",
    "groundedness",
    "summarization_quality",
    "verbosity",
]
summarization_eval_task = EvalTask(
    dataset=eval_dataset,
    metrics=metrics,
    experiment=experiment_name,
)
   

run_id = notebook_utils.generate_uuid(8)
eval_results = []


for i, prompt_template in enumerate(prompt_templates):
    experiment_run_name = f"eval-prompt-engineering-{run_id}-prompt-{i}"

    eval_result = summarization_eval_task.evaluate(
        prompt_template=prompt_template,
        experiment_run_name=experiment_run_name,
        model=gemini_model,
    )

    eval_results.append((f"Prompt #{i}", eval_result))
    

for title, eval_result in eval_results:
    notebook_utils.display_eval_result(title=title, eval_result=eval_result)
     
for title, eval_result in eval_results:
    notebook_utils.display_explanations(eval_result, metrics=["summarization_quality"])
    
    
notebook_utils.display_radar_plot(
    eval_results,
    metrics=metrics,
)
notebook_utils.display_bar_plot(
    eval_results,
    metrics=metrics,
)

summarization_eval_task.display_runs()
