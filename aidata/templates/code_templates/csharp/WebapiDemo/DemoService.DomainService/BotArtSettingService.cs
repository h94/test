using System;
using System.Collections.Generic;
using System.Net;
using System.Threading.Tasks;
using DemoService.Interface;
using DemoService.Model;
using ECCore;
using ECFramework;
using Microsoft.Extensions.Logging;

namespace DemoService.DomainService
{
    [DependencyInjection(typeof(IBotArtSettingService))]
    public class BotArtSettingService : IBotArtSettingService
    {
        private readonly IBotArtSettingProvider _botArtSettingProvider;
        private readonly IBotArtSettingValidator _botArtSettingValidator;
        private readonly IKafkaLogger _logger;

        public BotArtSettingService(
            IBotArtSettingProvider botArtSettingProvider,
            IBotArtSettingValidator botArtSettingValidator,
            IKafkaLogger logger)
        {
            _botArtSettingProvider = botArtSettingProvider;
            _botArtSettingValidator = botArtSettingValidator;
            _logger = logger;
        }

        public async Task<List<BotArtSetting>> ListBotArtSettingsAsync()
        {
            try
            {
                var list = await _botArtSettingProvider.ListAsync();
                return list ?? new List<BotArtSetting>();
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error, $"{nameof(ListBotArtSettingsAsync)}: list botartsettings failed. {ex.Message}");
                throw;
            }
        }

        public async Task<BotArtSetting> GetBotArtSettingAsync(string account)
        {
            _botArtSettingValidator.ValidateAccount(account);

            try
            {
                var setting = await _botArtSettingProvider.GetAsync(account.Trim());
                if (setting == null)
                    throw ECException.BuildNotFound("account");
                return setting;
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(GetBotArtSettingAsync)}: get botartsettings failed. account={account}. {ex.Message}");
                throw;
            }
        }

        public async Task<BotArtSetting> CreateBotArtSettingAsync(CreateBotArtSettingRequest request)
        {
            _botArtSettingValidator.ValidateCreateRequest(request);
            request.Account = request.Account.Trim();

            try
            {
                var exists = await _botArtSettingProvider.GetAsync(request.Account);
                if (exists != null)
                {
                    _logger.Log(LogLevel.Warning,
                        $"{nameof(CreateBotArtSettingAsync)}: account already exists. account={request.Account}");
                    throw ECException.Build(HttpStatusCode.Conflict, "account already exists.");
                }

                var created = await _botArtSettingProvider.CreateAsync(request);
                if (created == null || string.IsNullOrEmpty(created.Account))
                {
                    _logger.Log(LogLevel.Warning,
                        $"{nameof(CreateBotArtSettingAsync)}: create returned empty row. account={request.Account}");
                    throw ECException.Build(HttpStatusCode.BadRequest, "Failed to create botartsettings row.");
                }

                return created;
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(CreateBotArtSettingAsync)}: create botartsettings failed. account={request.Account}. {ex.Message}");
                throw;
            }
        }

        public async Task<BotArtSetting> UpdateBotArtSettingAsync(string account, UpdateBotArtSettingRequest request)
        {
            _botArtSettingValidator.ValidateUpdateRequest(account, request);
            var trimmedAccount = account.Trim();

            try
            {
                var existing = await _botArtSettingProvider.GetAsync(trimmedAccount);
                if (existing == null)
                {
                    _logger.Log(LogLevel.Warning,
                        $"{nameof(UpdateBotArtSettingAsync)}: update botartsettings not found. account={account}");
                    throw ECException.BuildNotFound("account");
                }

                var updated = await _botArtSettingProvider.UpdateAsync(trimmedAccount, request);
                if (updated == null)
                {
                    _logger.Log(LogLevel.Warning,
                        $"{nameof(UpdateBotArtSettingAsync)}: update botartsettings returned null. account={account}");
                    throw ECException.BuildNotFound("account");
                }

                return updated;
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(UpdateBotArtSettingAsync)}: update botartsettings failed. account={account}. {ex.Message}");
                throw;
            }
        }

        public async Task DeleteBotArtSettingAsync(string account)
        {
            _botArtSettingValidator.ValidateAccount(account);
            var trimmedAccount = account.Trim();

            try
            {
                var existing = await _botArtSettingProvider.GetAsync(trimmedAccount);
                if (existing == null)
                {
                    _logger.Log(LogLevel.Warning,
                        $"{nameof(DeleteBotArtSettingAsync)}: delete botartsettings no row. account={account}");
                    throw ECException.BuildNotFound("account");
                }

                await _botArtSettingProvider.DeleteAsync(trimmedAccount);
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(DeleteBotArtSettingAsync)}: delete botartsettings failed. account={account}. {ex.Message}");
                throw;
            }
        }
    }
}
