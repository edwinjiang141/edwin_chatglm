## 基于智谱AI ChatGlm3-6B 模型，在特定垂直领域进行模型微调。  
## 场景基于SQL语句开发规范
#### 说明: 该测试项目基于 SQL编写规范的一些常见规则作为训练语料，在Chatglm3-6b的模型基础上进行微调，达到可以对SQL书写规范的问题做出针对性的回答。    智谱AI ChatGlm3-6B 模型下载：https://huggingface.co/THUDM/chatglm3-6b
#### 本测试是把模型下载到本地后，采用量化技术加载。 采用T4 GPU 16GB测试。
#### 第一步：先对已有的QL编写规范或者规则的文档 《sql_qa.docx》进行解析，找出关键点(字段 content)和解释（字段 summary），并生成sql_qa.xlsx文件    由parse_word_test.py完成，
#### 第二步：基于解析出来的关键点（字段  content），用GPT-4 生成5个相似的提问句，并生成sql_qa.csv。 由generate_system_message.py完成  
#### 注意：这一步需要gpt4的 open_api key才能完成。具体如何获得，自行google。  本次测试使用的是代理OPENAI 
#### 例如：原始文档中 “在INSERT SQL语句中指定列名“，派生出如下问句：
##### 1、如何在INSERT SQL语句中指定列名？ 2、INSERT SQL语句中指定列名的语法是什么?, 3、为什么在INSERT SQL语句中需要指定列名？ 等
#### 第三步：用BitsAndBytes量化技术加载chatglm3-6b模型，用PEFT的QLORA技术，用生成的问答对语料数据，进行模型微调。 本次测试微调为10个epoch， 到232步的时候报错，但是training loss已经到了0.005。   由qlora_chatglm3.ipynb完成模型微调
#### 第四步：用Gradio生成简易的Web UI界面，实现SQL规范问题的解答。   由web_ui.py完成。
### 后续计划，继续使用更多的语料进行模型微调，再用LangChain （Conversation with Memory）实现基于上下文的对话聊天系统。

### 微调模型的回答 示例：
![image](https://github.com/edwinjiang141/edwin_chatglm/assets/152252397/729b1a04-d111-4c8e-bc29-a55a6847506e)
### 原始ChatGlm3-6B的回答 示例：
![image](https://github.com/edwinjiang141/edwin_chatglm/assets/152252397/784ea43f-16ba-42cd-91b1-54c2f0bbadd4)


### 微调模型的回答 示例：
![image](https://github.com/edwinjiang141/edwin_chatglm/assets/152252397/6dc0688b-84cb-4dca-acbc-fff2c8f73027)
### 原始ChatGlm3-6B的回答 示例：
![image](https://github.com/edwinjiang141/edwin_chatglm/assets/152252397/4a8e5406-5210-4d07-bc7d-d55384b873a8)


