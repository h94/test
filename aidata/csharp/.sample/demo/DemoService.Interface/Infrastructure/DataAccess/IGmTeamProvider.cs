using System.Collections.Generic;
using System.Threading.Tasks;
using DemoService.Model;

namespace DemoService.Interface
{
    public interface IGmTeamProvider
    {
        Task<List<GmTeam>> ListAsync();

        Task<GmTeam> GetAsync(string teamName);

        Task<GmTeam> CreateAsync(CreateGmTeamRequest request);

        Task<GmTeam> UpdateAsync(string teamName, UpdateGmTeamRequest request);

        Task<bool> DeleteAsync(string teamName);
    }
}
