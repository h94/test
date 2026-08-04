using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using DemoService.Interface;
using DemoService.Model;
using ECCore;

namespace DemoService.Infrastructure.Transfer
{
    [DependencyInjection(typeof(ICacheUserTransfer))]
    public class CacheUserTransfer : ICacheUserTransfer
    {
        private static readonly JsonSerializerOptions JsonReadOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };

        public CacheUser FromRedisHash(string logicalAuthKey, IReadOnlyDictionary<string, string> hashEntries)
        {
            if (hashEntries == null)
                return null;

            hashEntries.TryGetValue(CacheUserRedis.HashFieldSubLogs, out var subLogsJson);
            hashEntries.TryGetValue(CacheUserRedis.HashFieldBaseInfo, out var baseInfoJson);
            if (string.IsNullOrWhiteSpace(subLogsJson) && string.IsNullOrWhiteSpace(baseInfoJson))
                return null;
            var user = new CacheUser { AuthKey = logicalAuthKey };
            if (!string.IsNullOrWhiteSpace(subLogsJson))
            {
                try
                {
                    user.SubLogs = JsonSerializer.Deserialize<List<SubLogEntry>>(subLogsJson, JsonReadOptions)
                                   ?? new List<SubLogEntry>();
                }
                catch (JsonException)
                {
                    user.SubLogs = new List<SubLogEntry>();
                }
            }
            else
                user.SubLogs = new List<SubLogEntry>();

            if (!string.IsNullOrWhiteSpace(baseInfoJson))
            {
                try
                {
                    user.BaseInfo = JsonSerializer.Deserialize<BaseInfo>(baseInfoJson, JsonReadOptions);
                }
                catch (JsonException)
                {
                    user.BaseInfo = null;
                }
            }

            return user;
        }

        public CacheUserDTO Map(CacheUser user)
        {
            if (user == null)
                return null;

            return mapToDto(user);
        }

        public List<CacheUserDTO> MapList(IReadOnlyList<CacheUser> users)
        {
            return users == null || users.Count == 0
                ? new List<CacheUserDTO>()
                : users.Select(Map).Where(dto => dto != null).ToList();
        }

        private static CacheUserDTO mapToDto(CacheUser user)
        {
            var latest = user.SubLogs == null || user.SubLogs.Count == 0
                ? null
                : user.SubLogs.OrderByDescending(entry => entry.AddTime).First();

            var baseInfo = user.BaseInfo;

            return new CacheUserDTO
            {
                AuthKey = user.AuthKey,
                AddTime = latest?.AddTime ?? 0,
                SubEndTime = latest?.SubEndTime,
                SubID = latest?.SubID,
                PayType = latest?.PayType,
                PayMethod = latest?.PayMethod,
                SubTime = latest?.SubTime,
                TradeNo = latest?.TradeNo,
                AutoSub = latest?.AutoSub ?? false,
                Account = baseInfo?.Account,
                Email = baseInfo?.Email,
                Focus_Account = baseInfo?.Focus_Account,
                Follow_Account = baseInfo?.Follow_Account,
                Black_Account = baseInfo?.Black_Account,
                GameCount = baseInfo?.GameCount ?? 0,
                HeadShotPath = baseInfo?.HeadShotPath
            };
        }
    }
}
