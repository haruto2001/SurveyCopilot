# SurveyCopilot



## Usage

1. リポジトリをクローンして移動

```bash
git clone https://github.com/haruto2001/SurveyCopilot.git
cd SurveyCopilot
```


2. `.env`ファイルの作成

```bash
echo "OPENAI_API_KEY=sk-..." > .env
```


3. dockerイメージのビルド

- `make`コマンドが使える場合

```bash
make build
```

- `make`コマンドが使えない場合

```bash
docker build . -t survey-copilot
```


4. dockerコンテナの立ち上げ

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
