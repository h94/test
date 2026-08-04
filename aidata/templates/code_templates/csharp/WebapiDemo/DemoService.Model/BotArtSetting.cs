namespace DemoService.Model
{
    /// <summary>對應 Cassandra keyspace news 資料表 botartsettings（見 aidata/db/news.md）。</summary>
    public class BotArtSetting
    {
        public string Account { get; set; }
        public string Aihints { get; set; }
        public string Aimodes { get; set; }
        public string Articlesites { get; set; }
        public bool? Cansame { get; set; }
        public bool? Enabled { get; set; }
        public string Footers { get; set; }
        public string Gtypes { get; set; }
        public string Lastusetime { get; set; }
        public int? Maxpost { get; set; }
        public int? Mode { get; set; }
        public string Settings { get; set; }
        public string Titles { get; set; }
        public string Todohours { get; set; }
    }

    public class CreateBotArtSettingRequest
    {
        public string Account { get; set; }
        public string Aihints { get; set; }
        public string Aimodes { get; set; }
        public string Articlesites { get; set; }
        public bool? Cansame { get; set; }
        public bool? Enabled { get; set; }
        public string Footers { get; set; }
        public string Gtypes { get; set; }
        public string Lastusetime { get; set; }
        public int? Maxpost { get; set; }
        public int? Mode { get; set; }
        public string Settings { get; set; }
        public string Titles { get; set; }
        public string Todohours { get; set; }
    }

    public class UpdateBotArtSettingRequest
    {
        public string Aihints { get; set; }
        public string Aimodes { get; set; }
        public string Articlesites { get; set; }
        public bool? Cansame { get; set; }
        public bool? Enabled { get; set; }
        public string Footers { get; set; }
        public string Gtypes { get; set; }
        public string Lastusetime { get; set; }
        public int? Maxpost { get; set; }
        public int? Mode { get; set; }
        public string Settings { get; set; }
        public string Titles { get; set; }
        public string Todohours { get; set; }
    }
}
