using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace DemoService.Model
{
    /// <summary>Redis Hash：實體 key 見 <see cref="CacheUserRedis"/>（邏輯上仍以 AuthKey 識別）；欄位見 HashField 常數。</summary>
    public class CacheUser
    {
        public string AuthKey { get; set; }
        public List<SubLogEntry> SubLogs { get; set; }
        public BaseInfo BaseInfo { get; set; }
    }

    public class SubLogEntry
    {
        public long AddTime { get; set; }
        public string AuthKey { get; set; }
        public string SubEndTime { get; set; }
        public string SubID { get; set; }
        public string PayType { get; set; }
        public string PayMethod { get; set; }
        public string SubTime { get; set; }
        public string TradeNo { get; set; }
        public bool AutoSub { get; set; }
    }

    public class BaseInfo
    {
        [JsonPropertyName("Authkey")]
        public string Authkey { get; set; }
        public string Account { get; set; }
        public string AddTime { get; set; }
        public string AdSource { get; set; }
        public string Email { get; set; }
        public string Focus_Account { get; set; }
        public string Follow_Account { get; set; }
        public string Black_Account { get; set; }
        public int GameCount { get; set; }
        public string HeadShotPath { get; set; }
        public long LastActionTime { get; set; }
        public long LastCheckTime { get; set; }
        public string Memberships { get; set; }
        public string Password { get; set; }
        public int Rank { get; set; }
        public int RenameCount { get; set; }
        public string ShowCode { get; set; }
        public string SigninDate { get; set; }
        public int SigninDays { get; set; }
        public string Site { get; set; }
        public int Status { get; set; }
        public string SiteID { get; set; }
        public string UserName { get; set; }
    }

    public class CreateCacheUserRequest
    {
        public string AuthKey { get; set; }
        public List<SubLogEntry> SubLogs { get; set; }
        public BaseInfo BaseInfo { get; set; }
    }

    public class UpdateCacheUserRequest
    {
        public List<SubLogEntry> SubLogs { get; set; }
        public BaseInfo BaseInfo { get; set; }
    }
}
