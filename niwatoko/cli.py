import subprocess
import click
import os
from niwatoko.foundation_model.interpretation.llm.claude import generate_response
from niwatoko.foundation_model.interpretation.llm.gpt import generate_response as gpt_generate_response
from niwatoko.foundation_model.interpretation.llm.gpt import generate_response_gpt4o as gpt_generate_response_gpt4o
from niwatoko.foundation_model.interpretation.llm.litellm_tool import generate_response as litellm_enerate_response
import niwatoko
import re
from tqdm import tqdm
import itertools
import threading
import sys
import time

@click.command()
@click.argument('file_path', type=click.Path(exists=True), required=False)
@click.option('-m', '--model', type=click.STRING, default='claude-haiku', help='使用するモデルを選択します。例: openai, openai-gpt4o, claude, claude-sonnet, claude-opus, claude-haiku, litellm/modelname')
@click.option('-o', '--output', type=click.Path(), help='生成されたコードの出力先ファイルを指定します。')
@click.option('-v', '--version',  is_flag=True, help='バージョン情報を表示します。')

def main(file_path, model, output, version):
    # print("file_path:", file_path)
    """
    自然言語のソースコードを読み込んで実行するコマンドラインインターフェース。

    Args:
        file_path (str): 自然言語のソースコードが書かれたファイルのパス。
        model (str): 使用するモデル（OpenAIまたはClaude）。
        output (str): 生成されたコードの出力先ファイルのパス。
        version (bool): バージョン情報を表示するかどうか。
    """
    
    if not is_valid_model_name(model):
        valid_models = ['openai', 'openai-gpt4o', 'claude', 'claude-sonnet', 'claude-opus', 'claude-haiku']
        valid_models_str = ", ".join(valid_models)
        click.echo(f"無効なモデル名です: {model}")
        click.echo(f"使用可能なモデル: {valid_models_str}, または litellm/modelname の形式のモデル名")
        return
    
    if version:
        try:
            print(f"niwatoko version: {niwatoko.__version__}")
        except AttributeError:
            print("バージョン情報がniwatokoモジュールに存在しません。")
        return
    if not file_path:
        print("ファイルパスが指定されていません。")
        return

    processed_content = process_imports(file_path)

    print("実行中... (Processing...)")

    # ぐるぐるアニメーションを表示するスレッドを開始
    done = False
    spinner = threading.Thread(target=spin, args=(lambda: done,))
    spinner.start()

    if model == 'openai' or model == 'openai-gpt-turbo':
        generated_code = gpt_generate_response(
            model="gpt-4-turbo-2024-04-09",
            prompt=processed_content,
            max_tokens=1000,
            temperature=0.5,
        )
    elif model == 'openai-gpt4o':
        generated_code = gpt_generate_response_gpt4o(
            prompt=processed_content,
            max_tokens=2048,
            temperature=0.5,
        )
    elif 'litellm/' in model:
        model = model.replace("litellm/", "")
        print("litellm model:", model)
        generated_code = litellm_enerate_response(
            model=model,
            prompt=processed_content,
            max_tokens=2048,
            temperature=0.5,
        )
        
    else:
        if model == 'claude-sonnet':
            claude_model = 'claude-3-sonnet-20240229'
        elif model == 'claude-opus':
            claude_model = 'claude-3-opus-20240229'
        else:
            claude_model = 'claude-3-haiku-20240307'  # デフォルトはhaiku
        
        print("model:", claude_model)
        generated_code = generate_response(
            model=claude_model,
            prompt=processed_content,
            max_tokens=4000,
            temperature=0.2,
        )
    # ぐるぐるアニメーションを停止
    done = True
    spinner.join()

    if output:
        with open(output, 'w', encoding = "utf-8") as file:
            file.write(generated_code)
            print(f"生成されたコードを {output} に書き出しました。")
            print(f"Generated code has been written to {output}.")

def is_valid_model_name(model_name):
    valid_models = ['openai', 'openai-gpt4o', 'claude', 'claude-sonnet', 'claude-opus', 'claude-haiku']
    if model_name in valid_models:
        return True
    elif re.match(r'^litellm/\S+$', model_name):
        return True
    else:
        return False

def spin(done):
    """
    ぐるぐるアニメーションを表示する関数
    Args:
        done (function): アニメーションを停止するかどうかを判定する関数
    """
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done():
            break
        sys.stdout.write(f'\r{c}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!     \n')

import os
def process_imports(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    output = []
    for line in lines:
        output.extend(process_variable_imports(line))
        if line.startswith('- '):
            parts = line.strip().split(' = ')
            if len(parts) == 2:
                import_path = parts[1].strip()
                print('import_path:', import_path)
                if '[' in import_path and not import_path.startswith('['):
                    # ブラケットで囲まれたパスを抽出
                    path_within_brackets = import_path[1:-1]
                    # print("ブラケット内のパス:", path_within_brackets)  # デバッグ用print
                    # 拡張子を取得
                    extension = path_within_brackets.split('.')[-1]
                    # print("拡張子:", extension)  # デバッグ用print
                    # 拡張子に応じた処理を行う
                    if extension == 'md':
                        # print("Markdownファイルとして処理")  # デバッグ用print
                        # print(import_path)
                        output.extend(process_md_import(import_path, line))
                    elif extension == 'py':
                        # print("Pythonファイルとして処理")  # デバッグ用print
                        output.extend(process_py_import(import_path, line))
                    elif extension == 'rst':
                        # print("reStructuredTextファイルとして処理")  # デバッグ用print
                        output.extend(process_rst_import(import_path, line))
                    else:
                        # その他の拡張子の場合
                        # print("その他のファイルタイプとして処理")  # デバッグ用print
                        output.extend(process_other_import(import_path, line))
                elif import_path.startswith('[') and import_path.endswith(']'):
                    # ブラケットで囲まれたパスを抽出
                    path_within_brackets = import_path[1:-1]
                    # print("ブラケット内のパス:", path_within_brackets)  # デバッグ用print
                    # 拡張子を取得
                    extension = path_within_brackets.split('.')[-1]
                    # print("拡張子:", extension)  # デバッグ用print
                    if extension in ['png', 'jpg', 'jpeg', 'gif']:
                        print("画像ファイルとして処理")  # デバッグ用print
                        output.extend(process_image_import(import_path, line))
                    elif extension in ['mp4', 'mov', 'avi']:
                        print("動画ファイルとして処理")  # デバッグ用print
                        output.extend(process_video_import(import_path, line))
                    # 拡張子が指定されていない場合、新しい関数を使用して処理
                    else:
                        # print("拡張子が指定されていないため、process_no_extension_importを使用")  # デバッグ用print
                        output.extend(process_no_extension_import(import_path, line))
            else:
                output.append(line)
        else:
            output.append(line)
    
    return ''.join(output)
def process_variable_imports(line):
    """
    {{}}で囲まれた変数のインポートを処理する関数

    Args:
        line (str): ファイルの行

    Returns:
        list: 処理後の出力行のリスト
    """
    output = []
    if '{{' in line and '}}' in line:
        # {{ }} で囲まれた変数を抽出
        variable = line[line.index('{{') + 2:line.index('}}')]
        # 変数名を小文字に変換し、拡張子.mdを追加
        import_path = variable.lower() + '.md'
        # 同一階層内のファイルの内容を取得
        import_content = get_file_content(import_path)
        output.extend([line, '```\n', import_content, '```\n'])
    else:
        output.append(line)
    return output

def process_no_extension_import(import_path, line):
    """
    拡張子が指定されていないインポートを処理する関数

    Args:
        import_path (str): インポートするファイルのパス
        line (str): インポート文の行

    Returns:
        list: 処理後の出力行のリスト
    """
    import_path = import_path[1:-1]
    import_content = get_file_content(import_path)
    return [line, '```\n', import_content, '```\n']

def process_md_import(import_path, line):
    """
    Markdownファイルのインポートを処理する関数

    Args:
        import_path (str): インポートするファイルのパス
        line (str): インポート文の行

    Returns:
        list: 処理後の出力行のリスト
    """
    import_path = import_path[4:-1] + '.md'  # 拡張子を追加
    print(import_path)
    import_content = get_file_content(import_path)
    return [line, '```\n', import_content, '```\n']

def process_py_import(import_path, line):
    """
    Pythonファイルのインポートを処理する関数

    Args:
        import_path (str): インポートするファイルのパス
        line (str): インポート文の行

    Returns:
        list: 処理後の出力行のリスト
    """
    import_path = import_path[4:-1] + '.py'  # 拡張子を追加
    import_content = get_file_content(import_path)
    return [line, '```python\n', import_content, '```\n']

def process_rst_import(import_path, line):
    """
    reStructuredTextファイルのインポートを処理する関数

    Args:
        import_path (str): インポートするファイルのパス
        line (str): インポート文の行

    Returns:
        list: 処理後の出力行のリスト
    """
    import_path = import_path[5:-1] + '.rst'  # 拡張子を追加
    import_content = get_file_content(import_path)
    return [line, '```rst\n', import_content, '```\n']

def process_other_import(import_path, line):
    """
    md, py, rst以外の拡張子のインポートを処理する関数

    Args:
        import_path (str): インポートするファイルのパス
        line (str): インポート文の行

    Returns:
        list: 処理後の出力行のリスト
    """
    extension = import_path.split('[')[0].strip()  # 文字列の一番左から [ の一文字前までを拡張子として取得
    import_path = import_path.split('[')[1].split(']')[0].strip() + '.' + extension  # [ と ] の間にあるパスに拡張子を追加
    import_content = get_file_content(import_path)
    return [line, f'```{extension}\n', import_content, '```\n']

def process_image_import(import_path, line):
    """
    画像ファイルのインポートを処理する関数

    Args:
        import_path (str): インポートするファイルのパス
        line (str): インポート文の行

    Returns:
        list: 処理後の出力行のリスト
    """
    import_path = import_path[1:-1]
    recognized_text = recognize_image_text(import_path)
    return [line, '```\n', recognized_text, '```\n']

def process_video_import(import_path, line):
    """
    動画ファイルのインポートを処理する関数

    Args:
        import_path (str): インポートするファイルのパス
        line (str): インポート文の行

    Returns:
        list: 処理後の出力行のリスト
    """
    import_path = import_path[1:-1]
    recognized_text = recognize_video_text(import_path)
    return [line, '```\n', recognized_text, '```\n']

def get_file_content(file_path):
    # print(file_path)
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as file:
            return file.read().decode('utf-8')
    else:
        error_message = f"ファイルが見つかりません: {file_path}"
        # print(error_message)
        raise FileNotFoundError(error_message)

import base64
import requests

# OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
def encode_image(image_path):
    """
    画像ファイルをBase64エンコードする関数

    Args:
        image_path (str): 画像ファイルのパス

    Returns:
        str: Base64エンコードされた画像データ
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def recognize_image_text(image_path):
    """
    画像ファイルからテキストを認識する関数

    Args:
        image_path (str): 画像ファイルのパス

    Returns:
        str: 認識されたテキスト
    """
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "この画像には何が写っていますか？"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
    print(content)
    print('')

    return content



import cv2
from moviepy.editor import VideoFileClip
import time
import base64

def recognize_video_text(video_path, seconds_per_frame=1):
    """
    動画ファイルからフレームを抽出し、テキストのサマリーを生成する関数

    Args:
        video_path (str): 動画ファイルのパス
        seconds_per_frame (int): フレームを抽出する間隔（秒）

    Returns:
        str: 動画のテキストサマリー
    """
    import tqdm

    base64Frames = []
    base_video_path, _ = os.path.splitext(video_path)

    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * seconds_per_frame)
    curr_frame = 0

    # 指定された間隔でフレームを抽出
    with tqdm.tqdm(total=total_frames, desc="フレーム抽出中") as pbar:
        while curr_frame < total_frames - 1:
            video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
            success, frame = video.read()
            if not success:
                break
            _, buffer = cv2.imencode(".jpg", frame)
            base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
            curr_frame += frames_to_skip
            pbar.update(frames_to_skip)
    video.release()

    # 動画から音声を抽出
    audio_path = f"{base_video_path}.mp3"
    clip = VideoFileClip(video_path)
    if clip.audio is not None:
        clip.audio.write_audiofile(audio_path, bitrate="32k")
        clip.audio.close()
        print(f"音声を抽出: {audio_path}")
    else:
        print("音声が見つかりませんでした。")
    clip.close()

    print(f"抽出されたフレーム数: {len(base64Frames)}")

    # 抽出したフレームと音声を使用してテキストのサマリーを生成
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 実行中のバーを追加
    with tqdm.tqdm(total=1, desc="APIリクエスト送信中") as pbar:
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": "You are generating a video summary. Please provide a summary of the video. Respond in Markdown."
                },
                {
                    "role": "user",
                    "content": [
                        "These are the frames from the video.",
                        *map(lambda x: {"type": "image_url", 
                                        "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, base64Frames)
                    ]
                }
            ],
            "max_tokens": 300
        }
        pbar.update(1)
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    summary = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
    print(summary)
    print('')

    return summary
