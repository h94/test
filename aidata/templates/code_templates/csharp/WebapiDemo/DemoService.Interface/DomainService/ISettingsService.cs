using System.Threading.Tasks;

namespace DemoService.Interface
{
    public interface ISettingsService
    {
        Task<string> GetFlagsAsync();

        Task<string> GetLangueAsync(string countryCode);
    }
}
