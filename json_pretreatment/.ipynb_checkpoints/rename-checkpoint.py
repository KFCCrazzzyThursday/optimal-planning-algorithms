import os
import json
from docx import Document

def extract_json_from_docx(docx_file):
    # 打开并读取 .docx 文件内容
    doc = Document(docx_file)
    content = ""

    # 将所有段落的文本拼接成一个字符串
    for para in doc.paragraphs:
        content += para.text
    
    try:
        # 将字符串内容解析为JSON
        return json.loads(content)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {docx_file}")
        return None

def convert_docx_to_json(docx_file, json_file):
    # 提取 .docx 中的 JSON 数据
    json_data = extract_json_from_docx(docx_file)
    if json_data:
        # 将提取到的 JSON 数据写入 .json 文件
        with open(json_file, 'w', encoding='utf-8') as json_f:
            json.dump(json_data, json_f, ensure_ascii=False, indent=4)
        print(f"Converted {docx_file} to {json_file}")
    else:
        print(f"Failed to convert {docx_file}")

def convert_folder_docx_to_json(folder_path):
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith(".docx"):
            docx_file = os.path.join(folder_path, filename)
            json_file = os.path.join(folder_path, filename.replace(".docx", ".json"))
            
            # 将 .docx 文件转换为 .json
            convert_docx_to_json(docx_file, json_file)

if __name__ == "__main__":
    # 需要转换的文件夹路径
    folder_path = "../origin_Data"  # 修改为你的文件夹路径
    convert_folder_docx_to_json(folder_path)
