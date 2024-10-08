import os
import json

def find_files_with_route_length_4(folder):
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            file_path = os.path.join(folder, filename)
            
            # 打开并读取 JSON 文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 遍历JSON数据中的所有项目，检查route长度
            for key, value in data.items():
                for item in value:
                    if len(item.get('route', [])) == 4:
                        # 如果找到route长度为4的项，打印文件名
                        print(f"File: {filename} contains a route of length 4")
                        break  # 只要找到一个符合的route就停止检查该文件

if __name__ == "__main__":
    folder_path = "../json_data"  # 修改为你的文件夹路径
    find_files_with_route_length_4(folder_path)
