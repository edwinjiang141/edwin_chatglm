# edwin_chatglm
### 说明: 该测试项目基于 SQL编写规范的一些常见规则作为语料，在Chatglm3-6b的模型基础上进行微调，达到可以对SQL书写规范的问题做出针对性的回答。
#### 第一步：先对已有的QL编写规范或者规则的文档 《sql_qa.docx》进行解析，找出关键点(字段 content)和解释（字段 summary），并生成sql_qa.xlsx文件    由parse_word_test.py完成，
#### 第二步：基于解析出来的关键点（字段  content），用GPT-4 生成5个相似的提问句，并生成sql_qa.csv。 由generate_system_message.py完成  
#### 注意：这一步需要gpt4的 open_api key才能完成。具体如何获得，自行google。  我使用的是代理。 
#### 例如：原始文档中 “在INSERT SQL语句中指定列名“，派生出如下问句：
##### 1、如何在INSERT SQL语句中指定列名？ 2、INSERT SQL语句中指定列名的语法是什么?, 3、为什么在INSERT SQL语句中需要指定列名？ 等
#### 第三步：用BitsAndBytes量化技术加载chatglm3-6b模型，用PEFT的QLORA技术，用生成的问答对语料数据，进行模型微调。 本次测试微调伟10个epoch。 到232步的时候报错，但是training loss已经到了0.005。   由qlora_chatglm3.ipynb完成模型微调
#### 第四步：用Gradio生成建议Web UI界面，实现SQL规范问题的解答。   由web_ui.py完成。
### 后续计划，继续使用更多的语料进行模型微调，再用LangChain （Conversation with Memory）实现基于上下文的对话聊天系统。
