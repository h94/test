using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Threading.Tasks;
using DemoService.Interface;
using DemoService.Model;
using ECCore;
using ECFramework;
using StackExchange.Redis;

namespace DemoService.Infrastructure.DataAccess
{
    [DependencyInjection(typeof(ICacheUserProvider))]
    public class CacheUserProvider : ICacheUserProvider
    {
        private readonly IRedisManager _redisManager;

        public CacheUserProvider(IRedisManager redisManager)
        {
            _redisManager = redisManager;
        }

        public async Task<List<string>> ListAuthKeysAsync(string pattern)
        {
            var redis = createRedisOrThrow();
            var db = redis.Database;
            var server = getRedisServer(db);
            var keys = new List<string>();
            var scanPattern = CacheUserRedis.ToKeyScanPattern(pattern);
            await foreach (var key in server.KeysAsync(database: db.Database, pattern: scanPattern))
                keys.Add(CacheUserRedis.ToLogicalAuthKey(key.ToString()));
            return keys;
        }

        public async Task<bool> ExistsAsync(string authKey)
        {
            var redis = createRedisOrThrow();
            var redisKey = CacheUserRedis.ToRedisKey(authKey);
            return await redis.Database.KeyExistsAsync(redisKey);
        }

        public async Task<IReadOnlyDictionary<string, string>> GetHashAsync(string authKey)
        {
            var redis = createRedisOrThrow();
            var redisKey = CacheUserRedis.ToRedisKey(authKey);
            var dict = await redis.HashGetAsync(redisKey,
                new[] { CacheUserRedis.HashFieldSubLogs, CacheUserRedis.HashFieldBaseInfo });
            return dict;
        }

        public async Task CreateAsync(string authKey, string subLogsJson, string baseInfoJson)
        {
            var redis = createRedisOrThrow();
            var redisKey = CacheUserRedis.ToRedisKey(authKey);
            await redis.HashSetAsync(redisKey, CacheUserRedis.HashFieldSubLogs, subLogsJson);
            await redis.HashSetAsync(redisKey, CacheUserRedis.HashFieldBaseInfo, baseInfoJson);
        }

        public async Task UpdateAsync(string authKey, IReadOnlyDictionary<string, string> hashFields)
        {
            var redis = createRedisOrThrow();
            var redisKey = CacheUserRedis.ToRedisKey(authKey);
            foreach (var kv in hashFields)
                await redis.HashSetAsync(redisKey, kv.Key, kv.Value);
        }

        public async Task DeleteAsync(string authKey)
        {
            var redis = createRedisOrThrow();
            var redisKey = CacheUserRedis.ToRedisKey(authKey);
            await redis.Database.KeyDeleteAsync(redisKey);
        }

        private static IServer getRedisServer(IDatabase db)
        {
            var endpoints = db.Multiplexer.GetEndPoints();
            if (endpoints.Length == 0)
                throw ECException.Build(HttpStatusCode.InternalServerError, "Redis has no endpoints.");
            return db.Multiplexer.GetServer(endpoints.First());
        }

        private IRedisDB createRedisOrThrow()
        {
            try
            {
                return _redisManager.CreateDBConn("CacheUser");
            }
            catch (Exception ex)
            {
                throw ECException.Build(HttpStatusCode.InternalServerError,
                    $"Redis settings missing or invalid (ConnectId=CacheUser). {ex.Message}");
            }
        }
    }
}
