"""
This script creates an interactive web demo for the ChatGLM3-6B model using Gradio, a Python library for building quick and easy UI components for machine learning models. It's designed to showcase the capabilities of the ChatGLM3-6B model in a user-friendly interface, allowing users to interact with the model through a chat-like interface.

Usage:
- Run the script to start the Gradio web server.
- Interact with the model by typing questions and receiving responses.

Requirements:
- Gradio (required for 4.12.0 and later, 3.x is not support now) should be installed.

Note: The script includes a modification to the Chatbot's postprocess method to handle markdown to HTML conversion,
ensuring that the chat interface displays formatted text correctly.

"""

import os
import gradio as gr
import torch
from transformers import AutoModel, AutoTokenizer, StoppingCriteria, StoppingCriteriaList, TextIteratorStreamer,BitsAndBytesConfig
from threading import Thread
from peft import PeftModel, PeftConfig

# MODEL_PATH = os.environ.get('MODEL_PATH', 'THUDM/chatglm3-6b')
# TOKENIZER_PATH = os.environ.get("TOKENIZER_PATH", MODEL_PATH)

# tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH, trust_remote_code=True)
# model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, device_map="auto").eval()


model_name_or_path = '/llm_model/chatglm3-6b'   # 模型ID或本地路径
peft_model_path = f"/llm_train_model/llm_model/chatglm3-6b-epoch10"


_compute_dtype_map = {
    'fp32': torch.float32,
    'fp16': torch.float16,
    'bf16': torch.bfloat16
}



q_config = BitsAndBytesConfig(load_in_4bit=True,
                              bnb_4bit_quant_type='nf4',
                              bnb_4bit_use_double_quant=True,
                              bnb_4bit_compute_dtype=_compute_dtype_map['bf16'])
                              #bnb_4bit_compute_dtype=torch.float32)

base_model = AutoModel.from_pretrained(model_name_or_path,
                                       quantization_config=q_config,
                                       trust_remote_code=True,
                                       device_map='auto')

model = PeftModel.from_pretrained(base_model, peft_model_path)
config = PeftConfig.from_pretrained(peft_model_path)
tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)


class StopOnTokens(StoppingCriteria):
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        stop_ids = [0, 2]
        for stop_id in stop_ids:
            if input_ids[0][-1] == stop_id:
                return True
        return False


def parse_text(text):
    lines = text.split("\n")
    lines = [line for line in lines if line != ""]
    count = 0
    for i, line in enumerate(lines):
        if "```" in line:
            count += 1
            items = line.split('`')
            if count % 2 == 1:
                lines[i] = f'<pre><code class="language-{items[-1]}">'
            else:
                lines[i] = f'<br></code></pre>'
        else:
            if i > 0:
                if count % 2 == 1:
                    line = line.replace("`", "\`")
                    line = line.replace("<", "&lt;")
                    line = line.replace(">", "&gt;")
                    line = line.replace(" ", "&nbsp;")
                    line = line.replace("*", "&ast;")
                    line = line.replace("_", "&lowbar;")
                    line = line.replace("-", "&#45;")
                    line = line.replace(".", "&#46;")
                    line = line.replace("!", "&#33;")
                    line = line.replace("(", "&#40;")
                    line = line.replace(")", "&#41;")
                    line = line.replace("$", "&#36;")
                lines[i] = "<br>" + line
    text = "".join(lines)
    return text

def sql_standard_qa(query):
    # base_response, base_history = base_model.chat(tokenizer, query)

    #inputs = tokenizer(query, return_tensors="pt").to(0)
    ft_out = model.generate(query, max_new_tokens=512)
    ft_response = tokenizer.decode(ft_out[0], skip_special_tokens=True)
    
    # print(f"问题：{query}\n\n原始输出：\n{base_response}\n\n\nChatGLM3-6B微调后：\n{ft_response}")
    #return ft_response

def predict(history, max_length, top_p, temperature):
    stop = StopOnTokens()
    messages = []
    for idx, (user_msg, model_msg) in enumerate(history):
        if idx == len(history) - 1 and not model_msg:
            messages.append({"role": "user", "content": user_msg})
            break
        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        if model_msg:
            messages.append({"role": "assistant", "content": model_msg})

    print("\n\n====conversation====\n", messages)
    model_inputs = tokenizer.apply_chat_template(messages,
                                                 add_generation_prompt=True,
                                                 tokenize=True,
                                                 return_tensors="pt").to(next(model.parameters()).device)
    streamer = TextIteratorStreamer(tokenizer, timeout=60, skip_prompt=True, skip_special_tokens=True)
    generate_kwargs = {
        "input_ids": model_inputs,
        "streamer": streamer,
        "max_new_tokens": max_length,
        "do_sample": True,
        "top_p": top_p,
        "temperature": temperature,
        "stopping_criteria": StoppingCriteriaList([stop]),
        "repetition_penalty": 1.2,
    }

    #t = Thread(target=model.generate, kwargs=generate_kwargs)
    t = Thread(target=model.generate,kwargs=generate_kwargs)
    t.start()

    for new_token in streamer:
        if new_token != '':
            history[-1][1] += new_token
            yield history


with gr.Blocks() as demo:
    gr.HTML("""<h1 align="center">ChatGLM3-6B Gradio Simple Demo</h1>""")
    chatbot = gr.Chatbot()

    with gr.Row():
        with gr.Column(scale=4):
            with gr.Column(scale=12):
                user_input = gr.Textbox(show_label=False, placeholder="Input...", lines=10, container=False)
            with gr.Column(min_width=32, scale=1):
                submitBtn = gr.Button("Submit")
        with gr.Column(scale=1):
            emptyBtn = gr.Button("Clear History")
            max_length = gr.Slider(0, 32768, value=8192, step=1.0, label="Maximum length", interactive=True)
            top_p = gr.Slider(0, 1, value=0.8, step=0.01, label="Top P", interactive=True)
            temperature = gr.Slider(0.01, 1, value=0.6, step=0.01, label="Temperature", interactive=True)


    def user(query, history):
        return "", history + [[parse_text(query), ""]]

    submitBtn.click(user, [user_input, chatbot], [user_input, chatbot], queue=False).then(
        predict, [chatbot, max_length, top_p, temperature], chatbot
    )
    emptyBtn.click(lambda: None, None, chatbot, queue=False)

demo.queue()
demo.launch(server_name="0.0.0.0", server_port=8501, inbrowser=True, share=False)
