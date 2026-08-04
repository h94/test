using DemoService.Model;

namespace DemoService.Interface
{
    public interface IBotArtSettingValidator
    {
        void ValidateAccount(string account);

        void ValidateCreateRequest(CreateBotArtSettingRequest request);

        void ValidateUpdateRequest(string account, UpdateBotArtSettingRequest request);
    }
}
