using System.Collections.Generic;
using System.Net;
using System.Text.Json;
using DemoService.Interface;
using DemoService.Model;
using ECCore;
using ECFramework;

namespace DemoService.Infrastructure.Validators
{
    [DependencyInjection(typeof(ICacheUserValidator))]
    public class CacheUserValidator : ICacheUserValidator
    {
        private static readonly JsonSerializerOptions SerializeOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };

        public void ValidateAuthKey(string authKey)
        {
            if (string.IsNullOrWhiteSpace(authKey))
                throw ECException.BuildBadRequest("authKey");
        }

        public string NormalizeListPattern(string keyPattern)
        {
            return string.IsNullOrWhiteSpace(keyPattern) ? "*" : keyPattern.Trim();
        }

        public void ValidateCreateRequest(CreateCacheUserRequest request)
        {
            if (request == null)
                throw ECException.Build(HttpStatusCode.BadRequest, "request is required.");
            if (string.IsNullOrWhiteSpace(request.AuthKey))
                throw ECException.BuildBadRequest("authKey");
        }

        public void ValidateUpdateRequest(UpdateCacheUserRequest request)
        {
            if (request == null)
                throw ECException.Build(HttpStatusCode.BadRequest, "request is required.");
            if (request.SubLogs == null && request.BaseInfo == null)
                throw ECException.Build(HttpStatusCode.BadRequest, "SubLogs or BaseInfo is required for update.");
        }

        public IReadOnlyDictionary<string, string> BuildUpdateHashFields(UpdateCacheUserRequest request)
        {
            var d = new Dictionary<string, string>();
            if (request.SubLogs != null)
                d[CacheUserRedis.HashFieldSubLogs] = JsonSerializer.Serialize(request.SubLogs, SerializeOptions);
            if (request.BaseInfo != null)
                d[CacheUserRedis.HashFieldBaseInfo] = JsonSerializer.Serialize(request.BaseInfo, SerializeOptions);
            return d;
        }

        public (string SubLogsJson, string BaseInfoJson) SerializeCreatePayload(CreateCacheUserRequest request)
        {
            var subLogsJson = JsonSerializer.Serialize(request.SubLogs ?? new List<SubLogEntry>(), SerializeOptions);
            var baseInfoJson = request.BaseInfo != null
                ? JsonSerializer.Serialize(request.BaseInfo, SerializeOptions)
                : "{}";
            return (subLogsJson, baseInfoJson);
        }
    }
}
