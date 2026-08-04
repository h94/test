using System;
using System.Threading.Tasks;
using DemoService.Interface;
using ECCore;
using ECFramework;
using Microsoft.Extensions.Logging;

namespace DemoService.DomainService
{
    [DependencyInjection(typeof(ISettingsService))]
    public class SettingsService : ISettingsService
    {
        private readonly IAppSettingProvider _appSettingProvider;
        private readonly ISettingsValidator _settingsValidator;
        private readonly IKafkaLogger _logger;

        public SettingsService(IAppSettingProvider appSettingProvider, ISettingsValidator settingsValidator,
            IKafkaLogger logger)
        {
            _appSettingProvider = appSettingProvider;
            _settingsValidator = settingsValidator;
            _logger = logger;
        }

        public Task<string> GetFlagsAsync()
        {
            try
            {
                var flags = _appSettingProvider.GetFlags();
                return Task.FromResult(flags);
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error, $"{nameof(GetFlagsAsync)}: get flags failed. {ex.Message}");
                throw;
            }
        }

        public Task<string> GetLangueAsync(string countryCode)
        {
            _settingsValidator.ValidateCountryCode(countryCode);

            try
            {
                var lang = _appSettingProvider.GetLangue(countryCode.Trim());
                return Task.FromResult(lang);
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(GetLangueAsync)}: get langue failed. countryCode={countryCode}. {ex.Message}");
                throw;
            }
        }
    }
}
