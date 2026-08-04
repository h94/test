using System.Collections.Generic;
using System.Threading.Tasks;
using DemoService.Model;

namespace DemoService.Interface
{
    public interface IPgUserService
    {
        Task<List<PgUser>> ListPgUsersAsync();

        Task<PgUser> GetPgUserAsync(int id);

        Task<PgUser> CreatePgUserAsync(CreatePgUserRequest request);

        Task<PgUser> UpdatePgUserAsync(int id, UpdatePgUserRequest request);

        Task DeletePgUserAsync(int id);
    }
}
