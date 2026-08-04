using DemoService.Interface;
using ECCore;
using ECFramework;

namespace DemoService.Infrastructure.Validators
{
    [DependencyInjection(typeof(ISettingsValidator))]
    public class SettingsValidator : ISettingsValidator
    {
        public void ValidateCountryCode(string countryCode)
        {
            if (string.IsNullOrWhiteSpace(countryCode))
                throw ECException.BuildBadRequest(nameof(countryCode));
        }
    }
}
