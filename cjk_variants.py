#!/usr/bin/env python3
"""CJK character variants folded to one form before scoring.

Each pair maps a variant to the modern Japanese (shinjitai) form. Simplified
Chinese forms are deliberately absent: writing them is still a transcription
error. Applied after Unicode NFKC, which already folds compatibility ideographs.
"""

# Kyujitai -> shinjitai pairs from the Joyo kanji table. A few shinjitai merged
# formerly distinct characters (藝/芸, 缺/欠, 豫/予, 餘/余, 臺/台, 辨/辯/瓣 -> 弁);
# those fold together as well.
KYUJITAI = '''
亞亜 惡悪 壓圧 圍囲 爲為 醫医 壹壱 稻稲 飮飲 隱隠 營営 榮栄 衞衛 驛駅 圓円
鹽塩 緣縁 艷艶 應応 歐欧 毆殴 櫻桜 奧奥 橫横 溫温 穩穏 假仮 價価 畫画 會会
囘回 壞壊 懷懐 繪絵 槪概 擴拡 殼殻 覺覚 學学 嶽岳 樂楽 渴渇 勸勧 卷巻 寬寛
歡歓 罐缶 觀観 關関 陷陥 巖巌 顏顔 歸帰 氣気 龜亀 僞偽 戲戯 犧犠 卻却 舊旧
據拠 擧挙 虛虚 峽峡 挾挟 敎教 狹狭 鄕郷 曉暁 區区 驅駆 勳勲 薰薫 徑径 惠恵
揭掲 溪渓 經経 繼継 莖茎 螢蛍 輕軽 鷄鶏 藝芸 擊撃 缺欠 硏研 縣県 儉倹 劍剣
險険 圈圏 檢検 獻献 權権 顯顕 驗験 嚴厳 效効 廣広 恆恒 鑛鉱 號号 國国 黑黒
濟済 碎砕 齋斎 劑剤 雜雑 參参 慘惨 棧桟 蠶蚕 贊賛 殘残 絲糸 齒歯 兒児 辭辞
濕湿 實実 舍舎 寫写 釋釈 壽寿 收収 從従 澁渋 獸獣 縱縦 肅粛 處処 緖緒 敍叙
奬奨 將将 燒焼 稱称 證証 乘乗 剩剰 壤壌 孃嬢 條条 淨浄 狀状 疊畳 讓譲 釀醸
囑嘱 觸触 寢寝 愼慎 眞真 盡尽 圖図 粹粋 醉酔 隨随 髓髄 數数 樞枢 瀨瀬 聲声
靜静 齊斉 攝摂 竊窃 專専 戰戦 淺浅 潛潜 纖繊 踐践 錢銭 禪禅 雙双 壯壮 搜捜
插挿 揷挿 爭争 總総 聰聡 莊荘 裝装 騷騒 增増 藏蔵 臟臓 卽即 屬属 續続 墮堕
體体 對対 帶帯 滯滞 臺台 瀧滝 擇択 澤沢 擔担 膽胆 團団 彈弾 斷断 癡痴 遲遅
晝昼 蟲虫 鑄鋳 廳庁 徵徴 聽聴 敕勅 鎭鎮 遞逓 鐵鉄 轉転 點点 傳伝 黨党 盜盗
燈灯 當当 鬭闘 德徳 獨独 讀読 屆届 繩縄 貳弐 惱悩 腦脳 霸覇 廢廃 拜拝 賣売
麥麦 發発 髮髪 拔抜 晚晩 蠻蛮 祕秘 彥彦 濱浜 甁瓶 拂払 佛仏 竝並 變変 邊辺
辨弁 辯弁 瓣弁 舖舗 步歩 穗穂 寶宝 豐豊 萠萌 沒没 飜翻 每毎 萬万 滿満 默黙
彌弥 譯訳 藥薬 與与 豫予 餘余 譽誉 搖揺 樣様 謠謡 來来 賴頼 亂乱 覽覧 龍竜
兩両 獵猟 綠緑 壘塁 淚涙 勵励 禮礼 隸隷 靈霊 齡齢 戀恋 爐炉 勞労 樓楼 郞郎
祿禄 錄録 灣湾 歷歴 曆暦 涉渉 剝剥 塡填 頰頬 遙遥 瑤瑶 曾曽 峯峰 羣群 尙尚
'''

# The same character drawn to Taiwan/Hong Kong or Japanese glyph standards.
GLYPH = '''
內内 查査 產産 銳鋭 說説 稅税 悅悦 閱閲 脫脱 吳呉 娛娯 黃黄 靑青 淸清 旣既
鄉郷 戶戸 啟啓 姊姉 絕絶 顚顛
'''

def _pairs():
    pairs = {}
    for line in (KYUJITAI + GLYPH).split():
        variant, canonical = line
        if variant != canonical:
            pairs[variant] = canonical
    return pairs

VARIANTS = _pairs()
TABLE = str.maketrans(VARIANTS)

def fold(text):
    return text.translate(TABLE)
