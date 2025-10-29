import mlx_lm as mlx

model = None
tokenizer = None

def load_model(fileName: str) -> bool:
    global model, tokenizer
    model, tokenizer = mlx.load("Models/" + fileName)
    if (model is None) or (tokenizer is None):
        return False
    return True


def generate_response(prompt: str):
    global model, tokenizer
    if (model is None) or (tokenizer is None):
        return None

    # for response in mlx.stream_generate(model=model, tokenizer=tokenizer, prompt="What is the square root of 762?"):
    #     print(response.text, end="", flush=True)
    text = mlx.generate(model=model, tokenizer=tokenizer, prompt=prompt)
    return text

