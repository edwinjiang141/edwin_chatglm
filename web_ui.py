import torch
from transformers import AutoModel, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel, PeftConfig
import gradio as gr



def sql_standard_qa(query):
    # base_response, base_history = base_model.chat(tokenizer, query)

    inputs = tokenizer(query, return_tensors="pt").to(0)
    ft_out = model.generate(**inputs, max_new_tokens=512)
    ft_response = tokenizer.decode(ft_out[0], skip_special_tokens=True)
    
    # print(f"问题：{query}\n\n原始输出：\n{base_response}\n\n\nChatGLM3-6B微调后：\n{ft_response}")
    return ft_response


def launch_gradio():

    with gr.Blocks() as iface:
        gr.Markdown("SQL AIGC")

        with gr.Tab("SQL 开发规范"):
            with gr.Column():
                text_input=gr.Textbox(label="问题描述", value=" ")
                text_output=gr.Textbox(label="答案", value=" ")
                ask_button=gr.Button("搜索...")
         
        ask_button.click(sql_standard_qa,[text_input],outputs=text_output)     

        
    iface.launch(share=True, server_name="0.0.0.0",server_port=8501)

if __name__ == "__main__":
    # 模型ID或本地路径
    model_name_or_path = '/llm_model/chatglm3-6b'
    _compute_dtype_map = {
        'fp32': torch.float32,
        'fp16': torch.float16,
        'bf16': torch.bfloat16
    }

    # QLoRA 量化配置
    q_config = BitsAndBytesConfig(load_in_4bit=True,
                                bnb_4bit_quant_type='nf4',
                                bnb_4bit_use_double_quant=True,
                                bnb_4bit_compute_dtype=_compute_dtype_map['bf16'])
    # 加载量化后模型
    base_model = AutoModel.from_pretrained(model_name_or_path,
                                    quantization_config=q_config,
                                    device_map='auto',
                                    trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)

    peft_model_path = f"/llm_train_model/llm_model/chatglm3-6b-epoch10"

    config = PeftConfig.from_pretrained(peft_model_path)
    model = PeftModel.from_pretrained(base_model, peft_model_path)
    launch_gradio()