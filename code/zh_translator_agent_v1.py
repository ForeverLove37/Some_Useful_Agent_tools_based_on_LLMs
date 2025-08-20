import os
import re
import requests
import json
import ast # Abstract Syntax Tree, a powerful tool for parsing Python code

# --- 配置区 ---
# 请在这里填入你的 DeepSeek API Key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 需要翻译的绘图函数和参数，可以根据你使用的库进行扩展
# We target both plt.title() and ax.set_title() style functions
TARGET_PLOT_FUNCTIONS = {
    'title', 'xlabel', 'ylabel', 'suptitle',
    'set_title', 'set_xlabel', 'set_ylabel', 'text', 'legend'
}

# --- DeepSeek API 调用封装 ---
def call_deepseek_api(prompt, is_json_mode=False):
    """调用 DeepSeek API 的通用函数"""
    if not DEEPSEEK_API_KEY or "xxxxxxxx" in DEEPSEEK_API_KEY:
        raise ValueError("请在 DEEPSEEK_API_KEY 变量中设置你的有效 API Key")

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
    }
    if is_json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=180)
        response.raise_for_status()  # 如果请求失败则抛出异常
        
        result_content = response.json()['choices'][0]['message']['content']
        
        # 打印 API 返回的原始数据，方便调试
        # print("--- API Response ---")
        # print(result_content)
        # print("--------------------")
        
        return result_content
    except requests.exceptions.RequestException as e:
        print(f"调用 DeepSeek API 时发生网络错误: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"解析 DeepSeek API 响应时出错: {e}, 响应内容: {response.text}")
        return None

# --- 核心功能函数 ---

def translate_texts(texts_to_translate):
    """
    使用 DeepSeek API 批量翻译文本。
    """
    # 使用 JSON 格式让大模型返回结构化数据，更稳定可靠
    prompt = f"""
    你是一个精准的翻译引擎。请将以下JSON对象中的英文文本翻译成简洁、专业、地道的中文。
    请确保JSON的key保持不变，只翻译value中的字符串。
    请以JSON格式返回结果，不要添加任何额外的解释或说明。

    输入:
    {json.dumps(texts_to_translate, indent=2, ensure_ascii=False)}

    输出:
    """
    
    translated_json_str = call_deepseek_api(prompt, is_json_mode=True)
    if translated_json_str:
        try:
            return json.loads(translated_json_str)
        except json.JSONDecodeError as e:
            print(f"无法解析翻译返回的JSON: {e}")
            print(f"原始字符串: {translated_json_str}")
            return None
    return None

def beautify_code_layout(code_content):
    """
    使用 DeepSeek API 对代码进行美化和重构。
    """
    prompt = f"""
    你是一位资深的Python数据可视化专家。请对以下Python代码进行重构和美化，目标是让最终生成的图表更专业、更美观。

    请遵循以下原则：
    1.  **布局优化**：如果代码中包含多个子图（subplots），且它们是按单列或单行排列的（例如4行1列），请将它们重构为一个更紧凑、更美观的网格布局（例如2行2列的四宫格）。
    2.  **视觉适配**：适当调整字体大小、线条粗细、颜色搭配等，使图表整体视觉效果更和谐。可以使用 `plt.style.use('seaborn-v0_8-paper')` 或类似风格。尽可能使字体更大、更清晰。一定要注意图表，文本不要超出显示范围。
    3.  **代码优雅**：在不改变核心逻辑的前提下，优化代码结构，使其更具可读性。
    4.  **保留功能**：确保所有的绘图逻辑、标题、注释等信息都完整保留。
    5.  **直接输出代码**：你的回复应该只有重构后的Python代码，不要包含任何你自己的解释、注释标记（如 ```python ... ```）或其他额外文本，无需你解释如何做到优化的。

    这是需要优化的代码:
    ```python
    {code_content}
    ```
    """
    beautified_code = call_deepseek_api(prompt)
    return beautified_code

def inject_chinese_font_support(code_lines):
    """
    在代码中注入 Matplotlib 中文支持的设置。
    """
    matplotlib_import_index = -1
    # 找到 `import matplotlib.pyplot as plt` 这一行
    for i, line in enumerate(code_lines):
        if re.search(r'import\s+matplotlib\.pyplot\s+as\s+plt', line):
            matplotlib_import_index = i
            break
            
    # 如果找到了，就在它下面插入代码
    if matplotlib_import_index != -1:
        font_config = [
            "\n# --- 解决中文显示问题 ---",
            "plt.rcParams['font.sans-serif'] = ['SimHei']  # 或者 'Microsoft YaHei', 'Heiti TC', 等",
            "plt.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题",
            "# --------------------------\n"
        ]
        # 从后往前插入，避免索引错乱
        for i, line in enumerate(font_config):
            code_lines.insert(matplotlib_import_index + 1 + i, line)
    else:
        print("警告：未找到 'import matplotlib.pyplot as plt'，无法自动注入中文支持代码。")
        
    return ["line.rstrip('\\n')" for line in code_lines] # 返回 list of strings

def process_python_file(filepath, beautify=False):
    """
    处理单个Python文件：翻译注释和绘图字符串，并可选地进行美化。
    """
    print(f"--- 开始处理文件: {filepath} ---")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_code = f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return

    # 使用 AST 解析代码，更精准安全
    try:
        tree = ast.parse(original_code)
    except SyntaxError as e:
        print(f"Python 代码语法错误，无法解析: {e}")
        return

    texts_to_translate = {}
    
    # 1. 提取绘图函数中的字符串
    # 【修正点】: 我们创建一个 key 和 value 相同的字典
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and hasattr(node.func, 'attr') and node.func.attr in TARGET_PLOT_FUNCTIONS:
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.strip():
                    texts_to_translate[arg.value] = arg.value
            for kw in node.keywords:
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str) and kw.value.value.strip():
                    texts_to_translate[kw.value.value] = kw.value.value

    # 2. 提取注释
    code_lines = original_code.split('\n')
    for line in code_lines:
        line_stripped = line.strip()
        if line_stripped.startswith('#'):
            comment_text = line_stripped[1:].strip()
            if comment_text: 
                # 检查是否是代码注释，而不是纯粹的符号
                if re.search('[a-zA-Z]', comment_text):
                    texts_to_translate[comment_text] = comment_text
    
    if not texts_to_translate:
        print("未找到需要翻译的英文文本。")
        # 即使没有翻译内容，仍然可以尝试美化
        if beautify:
            print("开始对原始代码进行布局美化...")
            beautified_result = beautify_code_layout(original_code)
            if beautified_result:
                final_code = beautified_result
                print("布局美化完成。")
            else:
                print("布局美化失败。")
                return
        else:
            print("没有需要执行的操作。")
            return

    else:
        print(f"找到 {len(texts_to_translate)} 条需要翻译的文本，正在请求翻译...")
        
        # 3. 调用 API 进行翻译
        # 【修正点】: 直接传递字典给翻译函数
        translation_map = translate_texts(texts_to_translate)
        
        if not translation_map:
            print("翻译失败，终止处理。")
            return
            
        print("翻译完成，开始重建代码...")

        # 4. 重建代码
        # 按长度倒序排序，避免 "Plot" 先被替换导致 "Subplot" 替换失败的问题
        sorted_eng_texts = sorted(translation_map.keys(), key=len, reverse=True)

        modified_code = original_code
        for eng_text in sorted_eng_texts:
            zh_text = translation_map.get(eng_text, eng_text) # 使用 .get() 更安全
            # 在替换时，我们需要精确匹配，包括引号和注释符号
            # 替换字符串
            modified_code = modified_code.replace(f'"{eng_text}"', f'"{zh_text}"')
            modified_code = modified_code.replace(f"'{eng_text}'", f"'{zh_text}'")
            # 替换注释
            # 为避免错误替换代码，只替换在行首的注释
            # 例如：re.sub(r'#\s*' + re.escape(eng_text), '# ' + zh_text, modified_code)
            # 一个更简单且安全的做法是逐行检查
            temp_lines = []
            for line in modified_code.split('\n'):
                stripped_line = line.strip()
                if stripped_line.startswith(f'# {eng_text}') or stripped_line.startswith(f'#{eng_text}'):
                    temp_lines.append(line.replace(eng_text, zh_text))
                else:
                    temp_lines.append(line)
            modified_code = '\n'.join(temp_lines)
            
        translated_code = modified_code

    # 5. 注入中文支持代码
    modified_code_lines = translated_code.split('\n')
    # 检查是否已经注入过，防止重复注入
    if not any("plt.rcParams['font.sans-serif']" in line for line in modified_code_lines):
        inject_chinese_font_support(modified_code_lines)
    
    final_code_with_font_support = '\n'.join(modified_code_lines)

    # 6. (可选) 布局美化
    if beautify:
        print("代码翻译和中文支持注入完成，开始请求布局美化...")
        beautified_result = beautify_code_layout(final_code_with_font_support)
        if beautified_result:
            final_code = beautified_result
            print("布局美化完成。")
        else:
            print("布局美化失败，将仅保存翻译后的版本。")
            final_code = final_code_with_font_support
    else:
        final_code = final_code_with_font_support

    # 7. 保存新文件
    base, ext = os.path.splitext(filepath)
    new_filepath = f"{base}_zh_revision{ext}"
    
    try:
        with open(new_filepath, 'w', encoding='utf-8') as f:
            f.write(final_code)
        print(f"--- 处理完成！修改后的文件已保存至: {new_filepath} ---")
    except Exception as e:
        print(f"保存文件失败: {e}")

# 【可选的额外修正】
# 为了让 `translate_texts` 函数更健壮，也可以稍微修改一下，虽然主要问题在上游。
# 在 `translate_texts` 函数中，将 `json.dumps(texts_to_translate, ...)` 改为 `json.dumps(dict.fromkeys(texts_to_translate, ""), ...)`
# 但最佳实践是修复 `process_python_file`，所以请优先采用上面的方案。

# 我还对代码做了一些小优化：
# 1.  在提取文本时，增加了对空字符串的过滤。
# 2.  在重建注释时，采用了更稳妥的逐行替换逻辑。
# 3.  增加了检查，防止重复注入中文字体支持代码。

# --- 主程序入口 ---
if __name__ == '__main__':
    # 获取用户输入
    file_to_process = input("请输入要处理的 Python 文件路径 (例如: 001.py): ")

    if not os.path.exists(file_to_process):
        print(f"错误：文件 '{file_to_process}' 不存在。")
    else:
        beautify_choice = input("是否需要进行AI布局美化？(这是一个实验性功能，可能会改变代码结构) [y/N]: ").lower()
        should_beautify = beautify_choice == 'y'
        
        process_python_file(file_to_process, beautify=should_beautify)