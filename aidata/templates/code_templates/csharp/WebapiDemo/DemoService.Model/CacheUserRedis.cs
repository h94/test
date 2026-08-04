namespace DemoService.Model
{
    /// <summary>CacheUser Redis key 前置與 Hash 欄位名（符合 Module:Feature:Key 慣例）。</summary>
    public static class CacheUserRedis
    {
        public const string KeyPrefix = "DemoService:CacheUser:";

        public const string HashFieldSubLogs = "SubLogs";
        public const string HashFieldBaseInfo = "BaseInfo";

        public static string ToRedisKey(string authKey) => $"{KeyPrefix}{authKey}";

        public static string ToKeyScanPattern(string listPattern)
        {
            var p = string.IsNullOrWhiteSpace(listPattern) ? "*" : listPattern.Trim();
            return $"{KeyPrefix}{p}";
        }

        public static string ToLogicalAuthKey(string redisKey)
        {
            if (string.IsNullOrEmpty(redisKey))
                return redisKey;
            return redisKey.StartsWith(KeyPrefix) ? redisKey.Substring(KeyPrefix.Length) : redisKey;
        }
    }
}
