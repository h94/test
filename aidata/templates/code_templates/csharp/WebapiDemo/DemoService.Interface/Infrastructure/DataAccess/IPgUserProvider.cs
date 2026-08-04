using System.Collections.Generic;
using System.Threading.Tasks;
using DemoService.Model;

namespace DemoService.Interface
{
    public interface IPgUserProvider
    {
        Task<List<PgUser>> ListAsync();

        Task<PgUser> GetAsync(int id);

        Task<PgUser> CreateAsync(CreatePgUserRequest request);

        Task<PgUser> UpdateAsync(int id, UpdatePgUserRequest request);

        Task<bool> DeleteAsync(int id);
    }
}
