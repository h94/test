import { BackendSite, type ApiResponse } from "./index";

export interface GameItem {
  id: string;
  title: string;
  category: string;
  homeTeam: string;
  awayTeam: string;
  homeScore: number;
  awayScore: number;
  date: string;
  status: "completed" | "ongoing" | "upcoming";
  mvp: string;
  location: string;
  stadium: string;
  attendance: string;
  description: string;
  highlights: string[];
}

export const mockGames: GameItem[] = [
  {
    id: "1",
    title: "2026 電競世界盃 總決賽",
    category: "LOL 英雄聯盟",
    homeTeam: "T1",
    awayTeam: "Gen.G",
    homeScore: 3,
    awayScore: 2,
    date: "2026-07-30 20:00",
    status: "completed",
    mvp: "Faker",
    location: "沙烏地阿拉伯 利雅德",
    stadium: "Riyadh Esport Arena",
    attendance: "15,000 人",
    description:
      "總決賽 BO5 鏖戰五局，最終由 T1 在關鍵巴龍團戰打出 1 換 5 逆轉勝利，奪得 2026 電競世界盃總冠軍！",
    highlights: [
      "第一局：T1 主導下路對線，28 分鐘先拔頭籌",
      "第二局：Gen.G 中路極致發育，扳回一城",
      "第三局：Gen.G 戰術壓制，聽牌領先",
      "第四局：T1 遠古巨龍團戰大獲全勝，追平比分",
      "第五局：決賽局 Faker 關鍵開團完美控場，T1 成功奪冠",
    ],
  },
  {
    id: "2",
    title: "NBA 總冠軍賽 G7 搶七大戰",
    category: "籃球 NBA",
    homeTeam: "洛杉磯湖人",
    awayTeam: "波士頓塞爾提克",
    homeScore: 108,
    awayScore: 105,
    date: "2026-07-28 09:30",
    status: "completed",
    mvp: "LeBron James",
    location: "美國 洛杉磯",
    stadium: "Crypto.com Arena",
    attendance: "19,060 人",
    description:
      "歷史級黃綠大戰搶七大戰！湖人在第四節倒數 10 秒靠著壓哨三分球成功逆轉塞爾提克，斬獲總冠軍。",
    highlights: [
      "第一節：塞爾提克外線火力全開，領先 8 分",
      "第二節：湖人防守反擊拉近比數，半場落後 2 分",
      "第三節：雙方互有領先，12 次交替領先",
      "第四節：最後 10 秒湖人投進壓哨三分，最終 108:105 奪冠",
    ],
  },
  {
    id: "3",
    title: "歐洲冠軍聯賽 決賽",
    category: "足球 歐冠",
    homeTeam: "皇家馬德里",
    awayTeam: "曼城",
    homeScore: 2,
    awayScore: 1,
    date: "2026-07-25 03:00",
    status: "completed",
    mvp: "Vinicius Jr.",
    location: "英國 倫敦",
    stadium: "溫布利球場 (Wembley Stadium)",
    attendance: "86,211 人",
    description:
      "皇家馬德里在歐洲冠軍聯賽決賽中以 2:1 擊敗曼城，奪得隊史第 16 座歐冠金盃！",
    highlights: [
      "第 23 分鐘：曼城頭球先開紀錄 0:1",
      "第 54 分鐘：皇馬防守反擊追平 1:1",
      "第 88 分鐘：Vinicius Jr. 邊路突破絕殺進球 2:1",
    ],
  },
  {
    id: "4",
    title: "溫布頓網球錦標賽 男單決賽",
    category: "網球 溫網",
    homeTeam: "卡洛斯·艾卡拉茲",
    awayTeam: "諾瓦克·喬科維奇",
    homeScore: 3,
    awayScore: 1,
    date: "2026-07-20 21:00",
    status: "completed",
    mvp: "卡洛斯·艾卡拉茲",
    location: "英國 倫敦",
    stadium: "全英草地網球俱樂部 中央球場",
    attendance: "14,979 人",
    description:
      "艾卡拉茲歷經 3 小時 45 分鐘大戰，以 3:1 (6-4, 4-6, 7-6, 6-3) 擊敗喬科維奇成功衛冕溫網男單冠軍。",
    highlights: [
      "首盤：艾卡拉茲強勢發球局，6-4 先下一城",
      "次盤：喬科維奇破發反擊，4-6 追平",
      "第三盤：搶七大戰 7-6(5) 關鍵拿下",
      "第四盤：艾卡拉茲穩定發揮 6-3 鎖定勝局",
    ],
  },
  {
    id: "5",
    title: "MLB 美職棒大聯盟 明星賽",
    category: "棒球 MLB",
    homeTeam: "美國聯盟明星隊",
    awayTeam: "國家聯盟明星隊",
    homeScore: 5,
    awayScore: 4,
    date: "2026-07-15 08:00",
    status: "completed",
    mvp: "大谷翔平",
    location: "美國 洛杉磯",
    stadium: "道奇體育場 (Dodger Stadium)",
    attendance: "52,518 人",
    description:
      "2026 MLB 明星賽，美聯明星隊靠著大谷翔平單場雙響砲、4 打點的猛打賞演出，以 5:4 險勝國聯明星隊。",
    highlights: [
      "第 3 局：大谷翔平擊出一支 450 英尺特大號兩分砲",
      "第 7 局：大谷翔平再度開轟追加 2 分",
      "第 9 局下半：美聯救援投手滿壘成功三振關門",
    ],
  },
];

/**
 * 取得賽事歷史紀錄 API (目前使用 Mock 資料，真實 API 好之後替換為 BackendSite 呼叫)
 */
export const getHistoryGamesApi = async (): Promise<ApiResponse<GameItem[]>> => {
  // TODO: 當真實 API 完成時，取消下方範例註解並替換為實際 API 路徑：
  // return await BackendSite<GameItem[]>("GET", "/api/history/games");

  return {
    data: mockGames,
    error: null,
  };
};
