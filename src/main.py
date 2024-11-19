from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json
import re

class LocalAssistant:
    def __init__(self):
        self.commands = {
            "格式化json": self.format_json,
            "帮助": self.show_help,
            "聊天": self.chat
        }
        
        # 初始化模型
        print("正在加载模型，请稍候...")
        try:
            # 使用非量化版本
            self.tokenizer = AutoTokenizer.from_pretrained(
                "Qwen/Qwen-1_8B-Chat",  # 使用普通版本
                trust_remote_code=True
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                "Qwen/Qwen-1_8B-Chat",
                trust_remote_code=True,
                torch_dtype=torch.float32,
                device_map='auto'
            )
            
            # CPU优化设置
            torch.set_num_threads(4)
            self.model = self.model.eval()
            print("模型加载完成！")
        except Exception as e:
            print(f"模型加载错误：{str(e)}")
            raise
    
    def chat(self, text):
        try:
            # 使用通义千问的对话格式
            response, history = self.model.chat(
                self.tokenizer,
                text,
                history=[]
            )
            return response
        except Exception as e:
            return f"对话出错：{str(e)}"
    
    def format_json(self, text):
        try:
            # 尝试直接解析JSON
            try:
                data = json.loads(text)
            except:
                # 如果失败，尝试将字符串转换为合法的JSON格式
                text = re.sub(r"'", '"', text)  # 将单引号替换为双引号
                data = json.loads(text)
            
            # 返回格式化的JSON字符串
            return json.dumps(data, indent=2, ensure_ascii=False)
        except:
            return "无法将输入转换为JSON格式，检查输入是否正确。"
    
    def show_help(self, _=None):
        return """可用命令：
1. 格式化json：将文本转换为格式化的JSON
2. 帮助：显示此帮助信息
3. 聊天：与AI进行对话
输入 '退出' 结束程序"""
    
    def process_input(self, user_input):
        if not user_input.strip():
            return "请输入有效的内容"
            
        for cmd, func in self.commands.items():
            if cmd in user_input:
                # 提取命令后的文本
                text = user_input.replace(cmd, "").strip()
                return func(text)
        
        # 默认使用聊天功能
        return self.chat(user_input)

def main():
    assistant = LocalAssistant()
    print("欢迎使用本地AI助手！输入'帮助'查看可用命令。")
    
    while True:
        user_input = input("\n请输入(输入'退出'结束程序)：").strip()
        if user_input == '退出':
            print("再见！")
            break
            
        response = assistant.process_input(user_input)
        print("\n" + response)

if __name__ == "__main__":
    main() 