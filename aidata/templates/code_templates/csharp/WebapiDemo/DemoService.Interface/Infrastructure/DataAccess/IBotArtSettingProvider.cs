using System.Collections.Generic;
using System.Threading.Tasks;
using DemoService.Model;

namespace DemoService.Interface
{
    public interface IBotArtSettingProvider
    {
        Task<List<BotArtSetting>> ListAsync();

        Task<BotArtSetting> GetAsync(string account);

        Task<BotArtSetting> CreateAsync(CreateBotArtSettingRequest request);

        Task<BotArtSetting> UpdateAsync(string account, UpdateBotArtSettingRequest request);

        Task DeleteAsync(string account);
    }
}
