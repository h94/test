using System.Collections.Generic;
using System.Threading.Tasks;
using DemoService.Model;

namespace DemoService.Interface
{
    public interface ICacheUserService
    {
        Task<List<CacheUserDTO>> ListCacheUsersAsync(string keyPrefix);

        Task<CacheUserDTO> GetCacheUserAsync(string authKey);

        Task<CacheUserDTO> CreateCacheUserAsync(CreateCacheUserRequest request);

        Task<CacheUserDTO> UpdateCacheUserAsync(string authKey, UpdateCacheUserRequest request);

        Task DeleteCacheUserAsync(string authKey);
    }
}
