# AWS ハンズオンテンプレート

このリポジトリは、新しいハンズオンを作成するためのテンプレートです。

## クイックスタート

### 1. このテンプレートからリポジトリを作成

GitHub で「Use this template」ボタンをクリックするか、以下のコマンドを実行：

```bash
# Organization 内にリポジトリを作成
gh repo create mtmtnao-handson/my-new-handson \
  --template mtmtnao-handson/aws-handson-template \
  --private

# ローカルにクローン
gh repo clone mtmtnao-handson/my-new-handson
cd my-new-handson
```

> **Note**: `mtmtnao-handson` Organization 内に作成すると、**AWS認証情報の設定は不要**です。Organization Secrets が自動で使用されます。

### 2. リポジトリ名を決める

リポジトリ名がそのままURLのパスになります。

```
https://d2g4vxtyjwu8ha.cloudfront.net/{リポジトリ名}/
```

例：`eks-workshop` → `https://d2g4vxtyjwu8ha.cloudfront.net/eks-workshop/`

### 3. handson-meta.json を編集（ポータル自動登録用）

```json
{
  "name": "あなたのハンズオン名",
  "description": "ハンズオンの説明文",
  "icon": "material-school",
  "duration": "約60分",
  "level": "初級",
  "order": 100,
  "enabled": true
}
```

| フィールド | 説明 |
|-----------|------|
| `name` | ポータルに表示されるハンズオン名 |
| `description` | ポータルに表示される説明文 |
| `icon` | Material Designアイコン名（[一覧](https://pictogrammers.com/library/mdi/)） |
| `duration` | 所要時間 |
| `level` | 難易度（初級/中級/上級） |
| `order` | 表示順（小さいほど上に表示） |
| `enabled` | `false`にすると非表示 |

### 4. mkdocs.yml を編集

```yaml
# ハンズオン名を変更
site_name: "あなたのハンズオン名"

# 説明を変更
site_description: "ハンズオンの説明"

# site_url のリポジトリ名を変更
site_url: https://d2g4vxtyjwu8ha.cloudfront.net/your-repo-name/
```

### 5. コンテンツを作成

`docs/` ディレクトリ内のファイルを編集してハンズオンを作成します。

```
docs/
├── index.md            # トップページ
├── 01_overview.md      # 概要
├── 02_step1.md         # ステップ1
├── 03_step2.md         # ステップ2
├── ...
└── assets/             # 画像など
```

### 6. ローカルでプレビュー

```bash
# MkDocs をインストール（初回のみ）
pip install mkdocs-material

# プレビュー起動
mkdocs serve
# http://127.0.0.1:8000 でプレビュー
```

### 7. デプロイ

`main` ブランチにプッシュすると自動的にデプロイされます。

```bash
git add .
git commit -m "Add handson content"
git push
```

- デプロイ後のURL: `https://d2g4vxtyjwu8ha.cloudfront.net/{リポジトリ名}/`
- ポータルへの登録: 毎時自動更新（手動トリガーも可能）

---

## ディレクトリ構成

```
aws-handson-template/
├── mkdocs.yml              # MkDocs設定（ハンズオン情報を編集）
├── handson-meta.json       # ポータル登録用メタデータ
├── docs/
│   ├── index.md            # トップページ
│   ├── 01_overview.md      # 概要ページ
│   └── assets/             # 画像などのアセット
├── .github/
│   └── workflows/
│       └── deploy.yml      # 自動デプロイ設定
└── README.md               # このファイル
```

---

## ローカル開発

### セットアップ

```bash
# MkDocs Material をインストール
pip install mkdocs-material

# または pipx を使用
pipx install mkdocs-material --include-deps
```

### プレビュー

```bash
mkdocs serve
# http://127.0.0.1:8000 でプレビュー
```

### ビルド

```bash
mkdocs build --clean
```

---

## Markdown 記法

### アドモニション（注意書き）

```markdown
!!! note "タイトル"
    ノートの内容

!!! warning "警告"
    警告の内容

!!! tip "ヒント"
    ヒントの内容
```

### コードブロック

````markdown
```bash
aws s3 ls
```

```python title="example.py" linenums="1"
def hello():
    print("Hello, World!")
```
````

### タブ

```markdown
=== "AWS CLI"
    ```bash
    aws s3 ls
    ```

=== "マネジメントコンソール"
    1. S3 コンソールを開く
    2. バケットを選択
```

### 折りたたみ

```markdown
??? note "クリックして展開"
    隠れている内容
```

---

## ポータルへの登録

`handson-meta.json` を設定してデプロイすると、**ポータルに自動的にカードが表示されます**。

手動での登録作業は不要です。ポータルは毎時S3をスキャンしてハンズオン一覧を更新します。

すぐに反映させたい場合：

```bash
gh workflow run deploy.yml --repo mtmtnao-handson/aws-handson-portal
```

---

## 関連リポジトリ

| リポジトリ | 役割 |
|-----------|------|
| [aws-handson-portal](https://github.com/mtmtnao-handson/aws-handson-portal) | ポータル本体 + インフラ管理 |
| [q-ec2-gitlab](https://github.com/mtmtnao-handson/q-ec2-gitlab) | Amazon Q + GitLab ハンズオン（参考実装） |

---

## トラブルシューティング

### デプロイが失敗する

1. `mtmtnao-handson` Organization 内にリポジトリがあるか確認
2. Organization Secrets が設定されているか確認
   ```bash
   gh secret list -o mtmtnao-handson
   ```
3. Actions タブでエラーログを確認

### ポータルにカードが表示されない

1. `handson-meta.json` が存在するか確認
2. `enabled: true` になっているか確認
3. ポータルのワークフローを手動実行
   ```bash
   gh workflow run deploy.yml --repo mtmtnao-handson/aws-handson-portal
   ```

### ローカルでビルドが失敗する

```bash
# 依存関係を再インストール
pip install --upgrade mkdocs-material
```

---

## ライセンス

MIT License
