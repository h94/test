using System.Collections.Generic;
using System.Threading.Tasks;
using DemoService.Model;

namespace DemoService.Interface
{
    public interface IBotArtSettingService
    {
        Task<List<BotArtSetting>> ListBotArtSettingsAsync();

        Task<BotArtSetting> GetBotArtSettingAsync(string account);

        Task<BotArtSetting> CreateBotArtSettingAsync(CreateBotArtSettingRequest request);

        Task<BotArtSetting> UpdateBotArtSettingAsync(string account, UpdateBotArtSettingRequest request);

        Task DeleteBotArtSettingAsync(string account);
    }
}
