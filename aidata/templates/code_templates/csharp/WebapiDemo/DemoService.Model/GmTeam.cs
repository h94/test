using System;

namespace DemoService.Model
{
    /// <summary>對應 GM 資料庫 teams 資料表（GM schema 尚未收錄於 aidata/db）。</summary>
    public class GmTeam
    {
        public string TeamName { get; set; }
        public string Description { get; set; }
        public string AuthToken { get; set; }
        public bool Enabled { get; set; }
        public string WhiteList { get; set; }
        public DateTime? LastUpdTime { get; set; }
    }

    public class CreateGmTeamRequest
    {
        public string TeamName { get; set; }
        public string Description { get; set; }
        public string AuthToken { get; set; }
        public bool Enabled { get; set; }
        public string WhiteList { get; set; }
    }

    public class UpdateGmTeamRequest
    {
        public string Description { get; set; }
        public string AuthToken { get; set; }
        public bool Enabled { get; set; }
        public string WhiteList { get; set; }
    }
}
