import os
import json
import random

# 概率选择设置，p_minus代表选负数的概率，随着文件名开头变化
p_minus_map = {
    '5': 0.45,
    '6': 0.5,
    '7': 0.55,
    '8': 0.60
}

# 正数和负数的选择列表
negatives = [-25, -9, -1]
positives = [1, 9, 25]

def modify_json(json_data, p_minus):
    for key in json_data:
        for item in json_data[key]:
            last_reveal = item['reveals'][-1]
            if len(last_reveal) == 1:
                # 根据p_minus确定是选择负数还是正数
                if random.random() < p_minus:
                    random_value = random.choice(negatives)
                else:
                    random_value = random.choice(positives)
                
                # 修改最后的 reveals 数组
                last_reveal.append(random_value)
                # 将随机值加到对应的 score 字段中
                item['score'] += random_value
    return json_data

def process_files_in_folder(src_folder, dest_folder):
    # 检查目标文件夹是否存在，不存在则创建
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # 遍历源文件夹中的所有文件
    for filename in os.listdir(src_folder):
        if filename.endswith(".json") and filename[0] in p_minus_map:
            p_minus = p_minus_map[filename[0]]  # 根据文件名的首字母选择p_minus
            src_file = os.path.join(src_folder, filename)
            dest_file = os.path.join(dest_folder, filename)

            # 读取 JSON 文件
            with open(src_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 修改 JSON 数据
            modified_data = modify_json(data, p_minus)

            # 将修改后的数据写回到目标文件夹
            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(modified_data, f, ensure_ascii=False, indent=4)
            
            print(f"Processed {src_file}, saved to {dest_file}")

if __name__ == "__main__":
    # 源文件夹路径
    src_folder = "../json_data"  # 修改为你的源文件夹路径
    # 目标文件夹路径
    dest_folder = "../json_data/result"  # 修改为你的目标文件夹路径

    process_files_in_folder(src_folder, dest_folder)
