import os
import requests
import json

# --- 配置区  ---
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

# --- DeepSeek API 调用封装  ---
def call_deepseek_api(prompt):
    """调用 DeepSeek API 的通用函数"""
    if not DEEPSEEK_API_KEY or "xxxxxxxx" in DEEPSEEK_API_KEY:
        raise ValueError("请在 DEEPSEEK_API_KEY 变量中设置你的有效 API Key")
    # ... (此函数内部逻辑与上一个 Agent 完全相同，为简洁省略)
    payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"调用 DeepSeek API 时发生网络错误: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"解析 DeepSeek API 响应时出错: {e}, 响应内容: {response.text}")
        return None

# --- 核心功能函数 ---

def generate_analysis_markdown(code_content, requested_sections):
    """
    功能 1 & 2: 生成代码分析的 Markdown 文档。
    """
    instructions = []
    if 'structure' in requested_sections:
        instructions.append(
            "1. **代码建构思路**: 详细分析此脚本的整体结构和设计思路。描述其主要步骤，例如数据输入、核心计算、最终输出等，解释各个函数或代码块的作用和它们之间的联系。"
        )
    if 'math' in requested_sections:
        instructions.append(
            "2. **数学公式与变量总结**: 识别并提取代码中实现或注释中提及的所有数学公式。使用标准的 LaTeX 格式进行排版（例如，使用 `$` 或 `$$` 分隔符）。同时，列出这些公式中关键数学变量的含义。"
        )
    
    if not instructions:
        return ""

    prompt = f"""
你是一名资深的科研软件工程师，擅长阅读和理解科学计算代码，并为其撰写清晰的技术文档。

你的任务是分析下面提供的 Python 脚本，并根据以下要求生成一份详细的 Markdown 格式的分析报告。

**分析要求**:
{"\n".join(instructions)}

**输出规则**:
- 你的回答必须是纯粹的 Markdown 格式内容。
- 不要包含任何前言、结语或与文档内容无关的文字。

**需要分析的 Python 脚本**:
111python
{code_content}
111
"""
    print("正在请求 AI 生成代码分析文档...")
    analysis_content = call_deepseek_api(prompt)
    return analysis_content if analysis_content else "# 分析失败\nAI 未能成功生成分析文档。"


def redefine_variables_in_code(code_content, standards_content):
    """
    功能 3: 根据规范文档，重构代码中的变量名。
    """
    prompt = f"""
你是一名代码重构专家，严格遵守团队的编码规范。你的任务是接收一段 Python 脚本和一个变量命名规范文档，然后将脚本中的变量名修改为符合规范的名称。

**核心指令**:
1.  **严格遵循规范**: 仔细阅读下面的“变量命名规范”，并将其应用到“原始 Python 脚本”中。
2.  **仅重命名变量**: 你的唯一任务是重命名变量。绝对不能修改任何代码的执行逻辑、算法、函数调用、控制流或输出结果。
3.  **智能匹配**: 你需要理解变量在代码中的上下文含义，并与规范文档中的描述进行语义匹配。例如，如果规范说“标准差使用`sigma`”，而代码中使用了`std_dev`，你需要将其重命名为`sigma`。
4.  **保留原样**: 所有注释、字符串内容、函数名以及导入的库（如 `np`, `pd`, `plt`）必须保持原样。
5.  **全局一致**: 确保一个变量在整个脚本中的所有出现都被一致地重命名。

**输出规则**:
- 你的回复必须且只能是经过重构后的完整 Python 代码。
- 不要包含任何解释或格式化标记，例如 111python ... 111。

**变量命名规范**:
111plaintext
{standards_content}
111

**原始 Python 脚本**:
111python
{code_content}
111
"""
    print("正在请求 AI 重构变量名...")
    refactored_code = call_deepseek_api(prompt)
    return refactored_code

def analyze_codebase(filepath, naming_standards_path, options):
    """
    主处理函数，根据用户选项调度各项功能。
    """
    print(f"--- 开始处理文件: {filepath} ---")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code_content = f.read()
    except Exception as e:
        print(f"读取 Python 脚本 '{filepath}' 失败: {e}")
        return

    # --- 处理功能 1 和 2: 生成 Markdown 文档 ---
    markdown_sections = []
    if '1' in options:
        markdown_sections.append('structure')
    if '2' in options:
        markdown_sections.append('math')

    if markdown_sections:
        markdown_content = generate_analysis_markdown(code_content, markdown_sections)
        if markdown_content:
            base, _ = os.path.splitext(filepath)
            md_filepath = f"{base}_analysis.md"
            try:
                with open(md_filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                print(f"√ 功能 1/2 完成: 分析文档已保存至 -> {md_filepath}")
            except Exception as e:
                print(f"保存 Markdown 文件失败: {e}")
    
    # --- 处理功能 3: 重构变量名 ---
    if '3' in options:
        if not naming_standards_path or not os.path.exists(naming_standards_path):
            print(f"X 功能 3 失败: 变量命名规范文件未提供或路径错误 '{naming_standards_path}'。")
            return
            
        try:
            with open(naming_standards_path, 'r', encoding='utf-8') as f:
                standards_content = f.read()
        except Exception as e:
            print(f"读取规范文件 '{naming_standards_path}' 失败: {e}")
            return
            
        refactored_code = redefine_variables_in_code(code_content, standards_content)
        if refactored_code and ('import' in refactored_code or 'def' in refactored_code):
            base, ext = os.path.splitext(filepath)
            redefined_filepath = f"{base}_redefined{ext}"
            try:
                with open(redefined_filepath, 'w', encoding='utf-8') as f:
                    f.write(refactored_code)
                print(f"√ 功能 3 完成: 变量重构后的代码已保存至 -> {redefined_filepath}")
            except Exception as e:
                print(f"保存重构代码文件失败: {e}")
        else:
            print("X 功能 3 失败: AI 未能成功生成重构代码。")

    print("--- 所有任务处理完毕 ---")


# --- 主程序入口 ---
if __name__ == '__main__':
    py_file = input("请输入要分析的 Python 文件路径 (例如: 003.py): ")
    if not os.path.exists(py_file):
        print(f"错误: 文件 '{py_file}' 不存在。")
    else:
        print("\n请选择要启用的功能 (可多选，用逗号,隔开):")
        print("  [1] 生成代码建构思路描述")
        print("  [2] 总结数学公式与变量 (LaTeX格式)")
        print("  [3] 根据规范文件重定义变量名")
        choices = input("请输入选项 (例如: 1,3 或 2): ")
        
        options = {c.strip() for c in choices.split(',')}
        
        naming_file = ""
        if '3' in options:
            naming_file = input("请输入变量命名规范文件的路径 (例如: naming_standards.txt): ")

        analyze_codebase(py_file, naming_file, options)