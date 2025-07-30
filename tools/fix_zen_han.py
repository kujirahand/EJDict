# 全角と半角を統一する
import os
DIR_TOOLS = os.path.dirname(os.path.abspath(__file__))
DIR_ROOT = os.path.dirname(DIR_TOOLS)
DIR_SRC = os.path.join(DIR_ROOT, 'src')

def fix_zen_han(text):
    # (不要) 全角英数字を半角に変換
    # text = re.sub(r'[Ａ-Ｚａ-ｚ０-９]', lambda x: chr(ord(x.group(0)) - 0xFEE0), text)
    # 全角スペースを半角スペースに変換
    text = text.replace('　',' ')
    # 全角括弧を半角括弧に変換
    text = text.replace('（', '(').replace('）', ')')
    # 全角カンマを半角カンマに変換
    text = text.replace('，', ',')
    # 全角ピリオドを半角ピリオドに変換
    text = text.replace('．', '.')
    # 全角コロンを半角コロンに変換
    text = text.replace('：', ':')
    # 全角セミコロンを半角セミコロンに変換
    text = text.replace('；', ';')
    # 全角疑問符を半角疑問符に変換
    text = text.replace('？', '?')
    # 全角感嘆符を半角感嘆符に変換
    text = text.replace('！', '!')
    # 全角アポストロフィを半角アポストロフィに変換
    text = text.replace('＇', "'")
    # 全角ダッシュを半角ダッシュに変換
    text = text.replace('－', '-')    
    # 全角カッコを半角に変換
    text = text.replace('｛', '{').replace('｝', '}')
    text = text.replace('［', '[').replace('］', ']')
    # 全角アンダースコアを半角アンダースコアに変換
    text = text.replace('＿', '_')
    return text

def fix_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    fixed_text = fix_zen_han(text)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_text)


def main():
    #　全てファイルを処理
    for root, dirs, files in os.walk(DIR_SRC):
        for file in files:
            if file.endswith('.txt'):
                input_file = os.path.join(root, file)
                fix_file(input_file, input_file)
                print(f"Fixed: {input_file}")

if __name__ == "__main__":
    main()