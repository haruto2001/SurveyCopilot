# SurveyCopilot

SurveyCopilotは，研究における論文のサーベイを効率化するツールです．
このツールは，arXivやACL Anthologyに公開されている論文情報を取得し，ユーザーが設定したクエリに基づいてフィルタリングを行います．
また，フィルタリングされた論文はSlackに通知されます．


## Installation

リポジトリをクローンして移動

```bash
git clone https://github.com/haruto2001/SurveyCopilot.git
cd SurveyCopilot
```


## Usage

1. `.env`ファイルの作成

```bash
touch .env
echo "OPENAI_API_KEY=sk-..." >> .env
echo "SLACK_BOT_TOKEN=xoxb-..." >> .env
echo "OPENREVIEW_USERNAME=..." >> .env
echo "OPENREVIEW_PASSWORD=..." >> .env
```

> [!NOTE]
> `SLACK_BOT_TOKEN`を取得するには，Slack Botを作成する必要があります．（参考：[Slack API Quickstart](https://api.slack.com/quickstart)）
> また，`SLACK_BOT_TOKEN`の設定は任意です．設定しない場合，標準出力にのみ出力されます．


2. dockerイメージのビルド

- `make`コマンドが使える場合

```bash
make build
```

- `make`コマンドが使えない場合

```bash
docker build . -t survey-copilot
```


3. dockerコンテナの立ち上げ

- `make`コマンドが使える場合

```bash
make run-cpu
```

- `make`コマンドが使えない場合

```bash
docker run -it --rm \
--env-file ./.env \
--mount type=bind,src=./pyproject.toml,dst=/work/pyproject.toml \
--mount type=bind,src=./uv.lock,dst=/work/uv.lock \
--mount type=bind,src=./.python-version,dst=/work/.python-version \
--mount type=bind,src=./data,dst=/work/data \
--mount type=bind,src=./src,dst=/work/src \
survey-copilot bash
```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.