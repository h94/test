namespace DemoService.Model
{
    public class CacheUserDTO
    {
        public string AuthKey { get; set; }

        public long AddTime { get; set; }
        public string SubEndTime { get; set; }
        public string SubID { get; set; }
        public string PayType { get; set; }
        public string PayMethod { get; set; }
        public string SubTime { get; set; }
        public string TradeNo { get; set; }
        public bool AutoSub { get; set; }

        public string Account { get; set; }
        public string Email { get; set; }
        public string Focus_Account { get; set; }
        public string Follow_Account { get; set; }
        public string Black_Account { get; set; }
        public int GameCount { get; set; }
        public string HeadShotPath { get; set; }
    }
}
