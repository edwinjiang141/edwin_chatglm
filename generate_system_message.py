from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
import os
import csv
import docx
import re
from openpyxl import Workbook

# 初始化LangChain的GPT-3.5调用
chat = ChatOpenAI(model="gpt-4", #model="gpt-3.5-turbo-1106",
                  temperature=1,
                  max_tokens=4095,
                  openai_api_key = os.environ["OPENAI_API_KEY"],openai_api_base = "https://pro.aiskt.com/v1")

def generate_question_summary_pairs(raw_content):

    system_message = SystemMessage(
        content="""
        请根据输入的内容，理解内容的含义，然后生成5个提问句。例如如何理解，如何避免、如何实现、原理是什么 等方式表达
        """
    )
    # 人类消息包含原始数据样例
    human_message = HumanMessage(
        content=raw_content
    )
    # 构建消息列表并进行模型调用
    messages = [system_message, human_message]
    ai_message = chat(messages)
    return ai_message.content
#qa = generate_question_summary_pairs(f" 合理控制总连接数")

# lines = qa.strip().split('\n')
# for line in lines:
#     print(line)

def parse_word_structure(file_path):
    doc = docx.Document(file_path)

    structure = {}

    current_category = ""
    current_subcategories = []
    current_content = []

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()

        # 匹配标题编号
        match = re.match(r'^(\d+(\.\d+)*)\s+', text)
        if match:
            heading_number = match.group(1)

            # 处理之前的数据
            if current_category:
                structure[current_category] = {'Subcategories': current_subcategories, 'Content': current_content}

            # 更新当前分类
            current_category = heading_number
            current_subcategories = [text]
            current_content = []

        elif current_category and text:
            # 区分子分类和正文内容
            if text.startswith(current_category):
                current_subcategories.append(text)
            else:
                current_content.append(text)

    # 处理最后一组数据
    if current_category:
        structure[current_category] = {'Subcategories': current_subcategories, 'Content': current_content}

    return structure

def print_structure(structure,excel):
    wb = Workbook()
    ws = wb.worksheets[0]
    ws.append(['content','summary'])
    subcategories = ''
    for category, data in structure.items():
        cc = str(data['Subcategories']).split(maxsplit=1)[0]
        c = cc.count('.')
        if c>0 and not cc.isdigit():
            subcategories = "".join(str(data['Subcategories']).replace(cc,'').replace('''']''',''))
            #print(str(data['Subcategories']).replace(cc,'').replace('''']''',''))
            content = "   ".join(data['Content'])
            qa = generate_question_summary_pairs(subcategories)
            lines = qa.strip().split('\n')
            for line in lines:
                ws.append([line,content])
    wb.save(excel)


fn_word = 'sql_qa.docx'
fn_excel = fn_word[:-4]+'.xlsx'

document_structure = parse_word_structure(fn_word)
print_structure(document_structure,fn_excel)