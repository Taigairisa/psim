要件定義（ドラフト）

プロジェクト名（仮）: psim — Python Discrete-Event Simulation + Viewer
方針: モデルはすべてコード（Pythonオブジェクト）で定義。起動はコマンドで行い、引数で実行速度などを指定。コマンド実行で可視化（Viewer）とシミュレーション計算が開始される。


---

1. 目的（Why）

製造・物流プロセスの**離散事象シミュレーション（DES）**を、コード主導で高い再現性・拡張性とともに提供する。

コマンド一発で計算と可視化を起動し、**KPI（スループット、WIP、遅延、稼働率、滞留）**の計測・比較を容易にする。

Python生態系（統計・最適化・ML）との親和性を最優先する。


2. スコープ

2.1 MVP（Must / Should）

DESコア：Future Event List（最小次イベント駆動）、仮想時刻、乱数ストリーム、ウォームアップ、複数レプリケーション。

基本ブロック：Source / Sink / Buffer / Process（単機・並列能力）/ Conveyor（簡易）/ Router / Delay。

運用ロジック：キュー規則（FIFO/優先度）、処理時間分布、セットアップ時間、バッチ入出力。

リソース：Machine/Worker（能力1..N）、稼働カレンダー、故障・修理（MTBF/MTTR）。

可視化（Viewer 2D）：ノード＆エッジ表示、エンティティアニメーション、ズーム/パン、状態色分け、再生/一時停止。

CLI：psim run <model.py> にて起動。引数で実行速度・終了時刻・シード等を指定。

I/O：設定（YAML/JSON）任意、結果CSV/Parquet出力、イベントトレース任意。

分析：統計集計（平均/分位/信頼区間）、時間推移・ヒストグラムの描画（GUI or ファイル出力）。


2.2 将来拡張（Could / Later）

AGV・フォーク・ゾーン制御、レイアウト座標の物理搬送、品質・手直しループ、製番（Lot/BOM）。

スケジューラ連携（外部MIP/CP/ヒューリスティクス）と最適化ループ。

3D簡易ビュー、Web Viewer、プラグイン機構（カスタムブロック/分布）。



---

3. 非機能要件（NFR）

性能：描画なし（ヘッドレス）で高スループット。描画ありは実時間倍率（Real-Time Factor）を制御。

再現性：乱数シードをコマンド引数で固定可能。並列レプリケーション時の順序規約を明記。

拡張性：ブロック追加・分布追加・KPI追加が少ない結合で可能（Observer/Pluginパターン）。

可搬性：Windows/Linux/macOS（GUIはPySide6/DearPyGuiベース）。

テスト：単体、M/M/1等の解析解との統計的整合試験、回帰テスト。

可観測性：イベントトレース（段階的ON/OFF）、メトリクスロガー、プロファイルフック。



---

4. システム構成とアーキテクチャ

Core（psim.core）：

イベントスケジューラ：FEL（min-heap）、now（仮想時刻）、schedule(event, at)。

乱数：各ブロックごとの専用ストリーム（再現性向上）。

タイムアドバンス：最小次イベントにジャンプ。速度倍率はViewer側でスロットリング。


Model（psim.model）：

Model：ノード・エッジ・カレンダー・初期在庫等を保持。

Node抽象基底：on_enter(entity), on_exit(entity), on_event(evt) などのフック。

接続は Port 概念（out_port -> in_port）。


Blocks（psim.blocks）：Source/Sink/Process/Buffer/Conveyor/Router/Batch/Failure 等。

Metrics（psim.metrics）：WIP/滞留/スループット/稼働率/遅延/在庫切れ率をサンプリング or イベント積分。

Viewer（psim.viewer）：

Coreと分離（Pub-Sub/IPC or in-process Observer）。

RTF（real-time factor）制御：--speed 1x/10x/∞。∞は最速で計算、描画は間引き。

最小UI：Start/Stop/Step, シミュ時刻表示, FPS/RTF, オーバーレイ（WIP/流量）。




---

5. インターフェース仕様

5.1 Python API（モデル定義）

from psim import Model, connect
from psim.blocks import Source, Process, Buffer, Sink
from psim.dists import Exponential, Triangular

m = Model(seed=42, warmup="2h", until="80h")
src = Source(name="Source", interarrival=Exponential(mean=30))
mac = Process(name="Machine1", service=Triangular(20,30,50), capacity=1)
buf = Buffer(name="Buffer", capacity=50)
snk = Sink(name="Sink")

connect(src, mac)
connect(mac, buf)
connect(buf, snk)

m.register(src, mac, buf, snk)

5.2 CLI（コマンド）仕様（ドラフト）

psim run <model.py> [--until 80h] [--warmup 2h] [--rep 10]
         [--speed 20x|1x|inf] [--gui on|off] [--seed 123]
         [--export ./out] [--trace off|basic|full]
         [--render-interval 0.05] [--log-level INFO]

主要引数

引数	型/例	既定	説明

--until	"80h", "1d4h", 100000(秒)	必須	シミュ終了時刻（仮想時間）
--warmup	同上	0	ウォームアップ期間（KPI集計から除外）
--rep	整数	1	レプリケーション数（独立シード）
--speed	1x, 5x, 20x, inf	inf	実時間倍率。infは最速計算（描画間引き）
--gui	on/off	on	Viewer起動。offでヘッドレス（計算のみ）
--seed	整数	自動	ベースシード（ストリーム分配）
--export	パス	無効	KPI/トレースの保存先（CSV/Parquet/JSON）
--trace	列挙	off	イベントトレース粒度
--render-interval	秒	0.05	描画更新間隔（秒）


5.3 設定ファイル（任意）

psim.yaml を与えた場合、CLI引数 < 設定ファイル < モデル中デフォルト の優先度でマージ。



---

6. データモデル（概略）

Entity：id, 到着時刻, 属性dict（品目, 優先度, ルート等）。

Resource：能力, 状態（稼働/故障/セットアップ）, シフト, 速度係数。

Process：処理時間分布, セットアップ行列, バッチ規則。

Routing：確率/条件/属性ベース分岐、再加工ループ。

Metrics：時系列（WIP, 待ち, Throughput）、サマリ（平均, 分位, CI）。



---

7. 可視化要件（Viewer）

表示：ノード（アイコン/名称/稼働色）、エッジ（矢印/流量ヒート）、エンティティ（トークン）。

操作：Start/Stop、Step、速度倍率（1x/5x/20x/∞）切替、ズーム/パン、オブジェクト選択でプロパティパネル（読み取り専用MVP）。

パフォーマンス：描画は間引き更新（--render-interval）。計算は常にFEL主導で最速。

レイアウト：座標はコード側で指定（例：node.pos=(x,y)）。



---

8. KPI と分析

標準KPI：スループット、平均WIP、平均待ち時間、サイクルタイム、設備稼働率、在庫切れ率（Buffer空/需要未充足）。

統計：レプリケーション集計（平均/標準誤差/95%CI）、期間集計、時間窓ロールアップ。

出力：--export 指定で out/kpi.csv, out/trace.parquet などを生成。



---

9. テスト戦略

単体：FEL操作、分布サンプリング、キュー規則、故障/修理。

検証：M/M/1, M/M/c, D/D/1 等の理論値との比較（統計誤差内）。

回帰：乱数シード固定での再現、保存モデルの互換。

性能：イベント/秒、メモリフットプリント、描画FPS。



---

10. 受け入れ基準（MVP）

1. psim run examples/line1.py --until 80h --speed 20x --gui on が起動し、Viewerでアニメーションが見える。


2. --rep 10 --warmup 2h --export out/ で、CI付きのKPIレポート（CSV）が出力される。


3. --gui off --speed inf で可視化なし最速実行が可能。


4. 同一シードで結果が再現する。




---

11. 開発フェーズ計画

P0（2D Viewer + 最小ブロック）：Core/FEL、Source/Sink/Process/Buffer/Router、CLI、基本KPI、Viewer最小操作。

P1（運用拡張）：故障・修理、バッチ、カレンダー、Conveyor簡易、エクスポート強化、統計/CI。

P2（実験/最適化連携）：パラメータスイープAPI、OR-Tools連携、プラグイン枠、Web出力。



---

12. リスクと対策

描画と計算の干渉：スレッド/プロセス分離、描画間引き、バックプレッシャー。

パフォーマンス限界：ホットスポットをNumba/Cython/Rustで段階的に最適化。

仕様肥大：MoSCoWで段階導入、モデル互換性維持のためのバージョン管理。



---

13. 例：最小モデルと起動

examples/line1.py

from psim import Model, connect
from psim.blocks import Source, Process, Buffer, Sink
from psim.dists import Exponential, Triangular

m = Model(seed=7, warmup="2h", until="80h")
src = Source("Source", interarrival=Exponential(mean=30))
mac = Process("M1", service=Triangular(20,30,50), capacity=1)
buf = Buffer("Buf", capacity=50)
snk = Sink("Sink")

connect(src, mac); connect(mac, buf); connect(buf, snk)
m.register(src, mac, buf, snk)

# オプション：座標指定（Viewer表示用）
src.pos=(0,0); mac.pos=(2,0); buf.pos=(4,0); snk.pos=(6,0)

起動例

psim run examples/line1.py --until 80h --speed 20x --gui on --export out/ --seed 123


---

14. 用語集（抜粋）

FEL：Future Event List。次に発生するイベント群を保持する優先度キュー。

RTF：Real-Time Factor。実時間に対するシミュ時間の倍率（1x=等速、∞=最速）。

レプリケーション：同一パラメータで乱数のみ独立にした複数回試行。



---

補足

ドラフトのため、引数名・既定値・ブロックAPIは実装都合で微修正の可能性あり。

追加要望（AGV/品質/製番等）が確定すれば、P1/P2の優先順位を調整する。


