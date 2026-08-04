using System.Collections.Generic;
using DemoService.Model;

namespace DemoService.Interface
{
    public interface ICacheUserValidator
    {
        void ValidateAuthKey(string authKey);

        string NormalizeListPattern(string keyPattern);

        void ValidateCreateRequest(CreateCacheUserRequest request);

        void ValidateUpdateRequest(UpdateCacheUserRequest request);

        /// <summary>僅包含要寫入 Redis Hash 的欄位（SubLogs / BaseInfo）與 JSON 字串。</summary>
        IReadOnlyDictionary<string, string> BuildUpdateHashFields(UpdateCacheUserRequest request);

        (string SubLogsJson, string BaseInfoJson) SerializeCreatePayload(CreateCacheUserRequest request);
    }
}
