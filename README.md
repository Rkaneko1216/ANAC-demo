# ANAC SCML Oneshotトラックの導入

# 関連サイト
- 申し込み，結果の確認など: https://scml.cs.brown.edu/  
	- トラックごとのチュートリアル，GitHubリポジトリもここから確認できます
- oneshotのチュートリアル: https://scml.readthedocs.io/en/latest/tutorials/notebooks/02.develop_agent_scml2024_oneshot.html  
	- 他のベースエージェントはここから確認できます
- 過去の上位エージェント: https://github.com/yasserfarouk/scml-agents?tab=readme-ov-file#oneshot-track

---

# 環境構築
実行環境
- Python 3.11.9
- Windows 11

## 1. 仮想環境の作成と有効化
Windows PowerShell の例:
```powershell
# 通常の仮想環境作成
python -m venv .venv
# 有効化
.venv\Scripts\activate
```

Python のバージョン指定が必要な場合（`py` ランチャーを使用）:
```powershell
py -3.11 -m venv .venv
```

> 注: Python 3.14.0 で実行したところ利用できないライブラリがあったので、バージョンを落とす必要があります。3.11や3.12であれば問題なく動かせるはずです。

## 2. 依存関係のインストール
必要なライブラリをインストールします:
```powershell
pip install negmas scml scml-agents
```
または:
'''powershell
pip install -r requirements.txt
'''


上記で必要なライブラリがすべてインストールされます。

## 3. エージェントの実装
- `SimpleAgent` と `BetterAgent` はベースエージェントの例です。これらを参考に自分のエージェントを実装してください。  
- 昨年の優勝エージェントは別のベースエージェントから継承しています。

主に `propose` と `respond` メソッドを実装します:
- `propose`: 交渉の開始時と自分のターンに呼ばれます（数量，価格，時間を返す必要があります）。
- `respond`: 相手の提案を受け取ったときに呼ばれます（受理，拒否，交渉終了のいずれかを返す必要があります）。

## 4. トーナメントの作成
コードの最後にある `tournament_types` リストに自分のエージェントクラスを追加してください。  
例:
```python
tournament_types = [SimpleAgent, BetterAgent, MyAgent]
```
`scml_agents.get_agents` 関数を使うと過去の優勝エージェントを簡単に追加できます（戻り値は tuple なのでリストに変換して追加してください）。

## 5. トーナメントの実行
`if __name__ == '__main__':` ブロックを実行するとトーナメントが開始されます。  
- 結果はコンソールに表示されます。
- スコアの推移をグラフで確認できます（mean が高いほど良いエージェントです）。

---

