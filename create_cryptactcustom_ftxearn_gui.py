import PySimpleGUI as sg
import os
import pandas as pd
import datetime

# PySimpleGUIテーマ設定
sg.theme('Reddit')

# フォント設定
font_info = '游ゴシック Medium'

# [ 要ユーザー設定 ] ヘッダー情報 (クリプタクトカスタムファイル形式参照)
HEADER = ['Timestamp', 'Action', 'Source', 'Base', 'Volume', 'Price', 'Counter', 'Fee', 'FeeCcy', 'Comment']

# [ 要ユーザー設定 ] 固定値
ACTION  = 'STAKING'
SOURCE  = 'FTXJAPAN'
BASE    = ''
PRICE   = ''
COUNTER = 'JPY'
FEE     = 0
FEECCY  = 'JPY'
COMMENT = 'FTXEARN'

# [ 要ユーザー設定 ] ファイル情報
FILE_NAME = 'cryptact_custum'
FILE_PATH = 'trading_history/cryptact_custom/'

# [ 要ユーザー設定 ] 小数点以下の桁数を8桁に設定
pd.options.display.precision = 8

# [ 要ユーザー設定 ] 出力ファイル(.csv)を保存するパス
SAVE_OUTPUT_FILE_PATH = 'trading_history/csv/'

# window layout作成
layout = [
   [sg.Text('Create cryptact custom file from FTX Earn trading history(.csv)',font=(font_info,20))],
   [
      sg.InputText(key='-INPUT-',font=(font_info,20)),
      sg.FileBrowse(key='-FILE_BROWSE-',target='-INPUT-',button_text='Browse',font=(font_info,20))
   ],  
   [
      sg.Submit(button_text='Create',font=(font_info,20)), 
      sg.Cancel(button_text='Cancel',font=(font_info,20))
   ],
]

# window作成
window = sg.Window('createCryptactCustomFTXearn', layout)

# イベント受信待ち
while True:
   event, values = window.read()

   # CancelledまたはClosedイベント受信
   if event in (None, 'Cancel'):
      break

   # ファイル名と拡張子を取得
   filepath = values['-FILE_BROWSE-']
   filename, fileext = os.path.splitext(os.path.basename(filepath))

   # エラー処理（.csvのみ可）
   if fileext != '.csv':
      sg.popup_ok('[ ERROR ]\n\nファイル選択ではCSVファイルを指定してください。\nアプリケーションを終了します。\n',title='Result',button_color='red',font=(font_info,20))
      window.close()
      quit()

   # CSVファイル読み込み
   df_pu_trade = pd.read_csv(filepath, header=0)

   # エラー処理(FTXEarnの取引履歴ではない場合)
   if df_pu_trade.columns[0] != 'time' or df_pu_trade.columns[1] != 'amount' or df_pu_trade.columns[2] != 'currency':
      sg.popup_ok('[ ERROR ]\n\nファイル選択ではFTX Earnの取引履歴ファイル(CSV)を指定してください。\nアプリケーションを終了します。\n',title='Result',button_color='red',font=(font_info,20))
      window.close()
      quit()

   # 列名の変更(※列名に依存するため、仕様を確認すること)
   df_rename = df_pu_trade.rename(columns={'currency': 'Base','time': 'Timestamp','amount': 'Volume'})

   # 列名指定で昇順に並べ替え
   df_s = df_rename.sort_values(['Timestamp', 'Base'])

   # インデックスを連番で再割り当て（元のインデックスを削除）
   df_r = df_s.reset_index(drop=True)

   # yyyy/mm/dd HH:MM:SS 形式にフォーマット
   df_r['Timestamp'] = df_r['Timestamp'].str.replace('-', '/').str.replace(' JST', '')

   # Spreadsheetで自動置換されないようにシングルコーテーションマークで連結する。
   df_r['Timestamp'] = "'" + df_r['Timestamp']

   # Cryptactカスタムファイル用DataFrameの作成（ヘッダのみ）
   df_ct = pd.DataFrame(columns=HEADER)

   # Cryptactカスタムファイル用DataFrameの作成（値の設定）
   df_ct['Timestamp'] = df_r['Timestamp']
   df_ct['Base']      = df_r['Base']
   df_ct['Volume']    = df_r['Volume']
   df_ct['Action']    = ACTION
   df_ct['Source']    = SOURCE
   df_ct['Counter']   = COUNTER
   df_ct['Fee']       = FEE
   df_ct['FeeCcy']    = FEECCY
   df_ct['Comment']   = COMMENT

   # 本日日付指定で日付オブジェクトを取得する
   dt_today = datetime.date.today()

   # 出力ファイル名(.csv)
   filename = FILE_NAME + '_' + str(dt_today) + '.csv'

   # オブジェクトをCSVファイルに書き込む。
   # [ 要ユーザー設定 ]桁数に合わせてfloat_formatを変更する
   df_ct.to_csv(FILE_PATH + filename,index = False, float_format='%.8f')
   
   # 正常終了
   # カレントディレクトリ取得
   crd = os.getcwd()
   crd = crd + '/'
   # 出力ファイルパス表示
   sg.popup_scrolled('[ SUCCESS ]\n\n' + f'Path: {crd}{FILE_PATH}{filename}\n',title='Result',size=(60, 6),font=(font_info,20))
   break

# ウィンドウを閉じる(キャンセルまたは閉じる)
window.close()