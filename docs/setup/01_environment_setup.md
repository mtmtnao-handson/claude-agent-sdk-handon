# 環境セットアップ

## 概要

このセクションでは、Claude Agent SDK (Python) を使用するための環境を構築します。

---

## 手順1: Python のインストール確認

### 1. Python バージョンの確認

Claude Agent SDK は Python 3.10 以上が必要です。

**コマンド:**

```bash
python --version
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
Python 3.11.5
```

</details>

<div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #856404; line-height: 1;">&#x26A0;</span>
    <span style="font-weight: bold; color: #856404; font-size: 15px;">注意</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    Python 3.9 以下を使用している場合は、Python 3.10 以上にアップグレードしてください。
  </div>
</div>

---

## 手順2: Claude Code CLI のインストール

Claude Agent SDK は Claude Code CLI をランタイムとして使用します。

### 1. インストールコマンド

お使いの環境に合わせて、以下のいずれかの方法でインストールしてください。

**macOS (Homebrew):**

```bash
brew install --cask claude-code
```

**npm (クロスプラットフォーム):**

```bash
npm install -g @anthropic-ai/claude-code
```

**curl (Linux/macOS):**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

### 2. インストール確認

**コマンド:**

```bash
claude --version
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
claude-code version 1.0.0
```

</details>

---

## 手順3: Claude Agent SDK のインストール

### 1. pip でインストール

**コマンド:**

```bash
pip install claude-agent-sdk
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
Collecting claude-agent-sdk
  Downloading claude_agent_sdk-0.1.0-py3-none-any.whl (50 kB)
Successfully installed claude-agent-sdk-0.1.0
```

</details>

### 2. インストール確認

**コード:**

```python
import claude_agent_sdk
print(claude_agent_sdk.__version__)
```

---

## 手順4: 認証設定

Claude Agent SDK は以下の認証方法に対応しています。お使いの環境に合わせて設定してください。

### 方法1: Anthropic API Key

最もシンプルな方法です。

**環境変数の設定:**

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 方法2: Amazon Bedrock

AWS 環境を使用している場合。

**環境変数の設定:**

```bash
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION="us-east-1"
# AWS 認証情報は AWS CLI で設定済みであること
```

### 方法3: Google Vertex AI

GCP 環境を使用している場合。

**環境変数の設定:**

```bash
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION="us-central1"
export ANTHROPIC_VERTEX_PROJECT_ID="your-project-id"
# gcloud auth application-default login で認証済みであること
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    認証情報は <code>.bashrc</code> や <code>.zshrc</code> に追記しておくと、毎回設定する必要がありません。
  </div>
</div>

---

## 手順5: 動作確認

### 1. テストスクリプトの作成

以下のコードを `test_sdk.py` として保存します。

**コード:**

```python
import asyncio
from claude_agent_sdk import query

async def main():
    print("Claude Agent SDK テスト開始...")

    async for message in query(prompt="こんにちは！簡単に自己紹介してください。"):
        print(message)

    print("\nテスト完了！")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. 実行

**コマンド:**

```bash
python test_sdk.py
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
Claude Agent SDK テスト開始...
AssistantMessage(content=[TextBlock(text='こんにちは！私は Claude です。...')])
ResultMessage(cost_usd=0.001, ...)

テスト完了！
```

</details>

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    初回実行時は Claude Code の起動に数秒かかる場合があります。
  </div>
</div>

---

## トラブルシューティング

### CLINotFoundError が発生する場合

Claude Code がインストールされていないか、PATH が通っていません。

```python
# エラー例
CLINotFoundError: Claude Code CLI not found. Please install it first.
```

**解決方法:**

1. Claude Code CLI が正しくインストールされているか確認
2. `claude --version` が実行できるか確認
3. シェルを再起動して PATH を更新

### 認証エラーが発生する場合

API キーが設定されていないか、無効です。

**解決方法:**

1. 環境変数が正しく設定されているか確認: `echo $ANTHROPIC_API_KEY`
2. API キーが有効か Anthropic Console で確認
3. Bedrock/Vertex を使用する場合は、対応する環境変数も設定

---

## 次のステップ

環境構築が完了しました！次は [query() 関数](../basics/01_query_function.md) で、基本的な使い方を学びましょう。
