# edwin_chatglm
## 说明: 该测试项目基于 SQL编写规范的一些常见规则作为语料，在Chatglm3-6b的模型基础上进行微调，达到可以对SQL书写规范的问题做出针对性的回答。
### 第一步：先对已有的QL编写规范或者规则的文档 《sql_qa.docx》进行解析，找出关键点(字段 content)和解释（字段 summary），并生成sql_qa.xlsx文件    由parse_word_test.py完成，
### 第二步：基于解析出来的关键点（字段  content），用GPT-4 生成5个相似的提问句， 由generate_system_message.py完成
### 例如：原始文档中 “在INSERT SQL语句中指定列名“，派生出如下问句：
#### 1、如何在INSERT SQL语句中指定列名？ 2、INSERT SQL语句中指定列名的语法是什么?, 3、为什么在INSERT SQL语句中需要指定列名？ 等
### 第三步：用
