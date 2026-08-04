using System.Collections.Generic;
using System.Threading.Tasks;
using DemoService.Model;

namespace DemoService.Interface
{
    public interface IGmTeamService
    {
        Task<List<GmTeam>> ListGmTeamsAsync();

        Task<GmTeam> GetGmTeamAsync(string teamName);

        Task<GmTeam> CreateGmTeamAsync(CreateGmTeamRequest request);

        Task<GmTeam> UpdateGmTeamAsync(string teamName, UpdateGmTeamRequest request);

        Task DeleteGmTeamAsync(string teamName);
    }
}
