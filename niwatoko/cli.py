import click
import os
import openai
from niwatoko.foundation_model.interpretation.llm.claude import generate_response

@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('-m', '--model', type=click.Choice(['openai', 'claude']), default='openai', help='使用するモデルを選択します。')
@click.option('-o', '--output', type=click.Path(), help='生成されたコードの出力先ファイルを指定します。')
def main(file_path, model, output):
    """
    自然言語のソースコードを読み込んで実行するコマンドラインインターフェース。

    Args:
        file_path (str): 自然言語のソースコードが書かれたファイルのパス。
        model (str): 使用するモデル（OpenAIまたはClaude）。
        output (str): 生成されたコードの出力先ファイルのパス。
    """
    with open(file_path, 'r') as file:
        natural_language_code = file.read()

    if model == 'openai':
        openai.api_key = os.getenv("OPENAI_API_KEY")
        prompt = f"{natural_language_code}"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )
        generated_code = response.choices[0].text.strip()
    elif model == 'claude':
        prompt = f"{natural_language_code}"
        print(natural_language_code)
        print("=================================")
        generated_code = generate_response(
            # model='claude-3-haiku-20240307',
            model='claude-3-sonnet-20240229',
            # claude-3-sonnet-20240229
            # claude-3-haiku-20240307
            # claude-3-opus-20240229
            prompt=prompt,
            max_tokens=4000,
            temperature=0.2,
        )
    else:
        raise ValueError(f"無効なモデル: {model}")

    # print("生成されたPythonコード:")
    # print(generated_code)

    if output:
        with open(output, 'w') as file:
            file.write(generated_code)
            print(f"生成されたコードを {output} に書き出しました。")

    # exec(generated_code)