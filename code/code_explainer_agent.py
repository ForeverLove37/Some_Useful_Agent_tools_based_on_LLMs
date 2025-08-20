import os
import requests
import json
import ast

# --- 配置区 ---
# 请在这里填入你的 DeepSeek API Key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# --- DeepSeek API 调用封装 ---
def call_deepseek_api(prompt):
    """调用 DeepSeek API 的通用函数"""
    if not DEEPSEEK_API_KEY or "xxxxxxxx" in DEEPSEEK_API_KEY:
        raise ValueError("请在 DEEPSEEK_API_KEY 变量中设置你的有效 API Key")

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1, # 使用较低的温度，让输出更稳定和精确
        "max_tokens": 16384,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        
        result_content = response.json()['choices'][0]['message']['content']
        return result_content
    except requests.exceptions.RequestException as e:
        print(f"调用 DeepSeek API 时发生网络错误: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"解析 DeepSeek API 响应时出错: {e}, 响应内容: {response.text}")
        return None

# --- 核心功能函数 ---

def analyze_and_explain_code(code_content):
    """
    使用 DeepSeek API 分析代码，生成功能总结、思路和LaTeX公式。
    """
    prompt = f"""
    你是一位顶级的软件工程师和数学家，擅长阅读复杂的代码并以清晰、结构化的方式解释其核心思想。
    现在，请分析以下 Python 代码。你的任务是生成一份详细的 Markdown 格式的分析报告。

    报告必须包含以下三个部分，并严格按照指定格式输出：

    ---
    
    ### 1. 功能总结 (Function Summary)
    
    * 在这部分，请用几句话简洁明了地概括这段代码的总体功能。说明它接收什么输入，执行什么计算，最终产出什么结果。
    
    ### 2. 实现思路 (Implementation Logic)
    
    * 在这部分，请分点、按步骤详细拆解代码的实现逻辑和算法流程。
    * 描述数据是如何被初始化、处理和转换的。
    * 解释关键函数或代码块的作用。
    * 如果代码中包含算法（如梯度下降、数据拟合等），请清晰地阐述其工作原理。
    
    ### 3. 核心数学公式与变量 (Core Mathematical Formulas and Variables)
    
    * **这是最重要的部分。**
    * 请仔细识别代码中实现的数学运算和公式。
    * 将这些公式以 **LaTeX 格式** 表达出来，并对方程式进行编号。
    * 列出代码中的主要变量，并解释它们对应的数学符号和含义。请使用 Markdown 表格进行展示。
    * **关键要求**: 变量名（如 `learning_rate`）应被正确地转换为对应的 LaTeX 符号（如 $\\alpha$）。代码中的运算（如 `np.dot(X, w) + b`）应被转换为标准的数学表达式（如 $X \cdot w + b$）。
    
    ---
    
    请开始分析下面的代码：
    
    ```python
    {code_content}
    ```
    """

    explanation = call_deepseek_api(prompt)
    return explanation

def process_code_file(filepath):
    """
    读取代码文件，调用分析函数，并将结果保存到 Markdown 文件中。
    """
    print(f"--- 开始分析文件: {filepath} ---")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code_content = f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return

    # 检查代码内容是否为空
    if not code_content.strip():
        print("文件为空，无需分析。")
        return
        
    print("代码读取成功，正在请求 AI 进行分析...")
    
    # 调用 API 进行分析
    analysis_report = analyze_and_explain_code(code_content)
    
    if not analysis_report:
        print("代码分析失败，终止处理。")
        return
        
    print("分析完成，正在保存报告...")

    # 保存到新的 .md 文件
    base, _ = os.path.splitext(filepath)
    report_filepath = f"{base}_analysis_report.md"
    
    try:
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(analysis_report)
        print(f"--- 分析报告已保存至: {report_filepath} ---")
    except Exception as e:
        print(f"保存报告文件失败: {e}")

# --- 主程序入口 ---
if __name__ == '__main__':
    file_to_process = input("请输入要分析的 Python 文件路径 (例如: linear_regression.py): ")

    if not os.path.exists(file_to_process):
        print(f"错误：文件 '{file_to_process}' 不存在。")
    else:
        process_code_file(file_to_process)
