using System.Collections.Generic;
using System.Threading.Tasks;

namespace DemoService.Interface
{
    public interface ICacheUserProvider
    {
        Task<List<string>> ListAuthKeysAsync(string pattern);

        Task<IReadOnlyDictionary<string, string>> GetHashAsync(string authKey);

        Task<bool> ExistsAsync(string authKey);

        Task CreateAsync(string authKey, string subLogsJson, string baseInfoJson);

        Task UpdateAsync(string authKey, IReadOnlyDictionary<string, string> hashFields);

        Task DeleteAsync(string authKey);
    }
}
