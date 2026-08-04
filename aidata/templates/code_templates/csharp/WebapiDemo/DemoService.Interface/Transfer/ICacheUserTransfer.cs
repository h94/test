using System.Collections.Generic;
using DemoService.Model;

namespace DemoService.Interface
{
    public interface ICacheUserTransfer
    {
        CacheUser FromRedisHash(string logicalAuthKey, IReadOnlyDictionary<string, string> hashEntries);

        CacheUserDTO Map(CacheUser user);

        List<CacheUserDTO> MapList(IReadOnlyList<CacheUser> users);
    }
}
