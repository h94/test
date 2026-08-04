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
    [DependencyInjection(typeof(ICacheUserService))]
    public class CacheUserService : ICacheUserService
    {
        private readonly ICacheUserProvider _cacheUserProvider;
        private readonly ICacheUserValidator _cacheUserValidator;
        private readonly ICacheUserTransfer _cacheUserTransfer;
        private readonly IKafkaLogger _logger;

        public CacheUserService(
            ICacheUserProvider cacheUserProvider,
            ICacheUserValidator cacheUserValidator,
            ICacheUserTransfer cacheUserTransfer,
            IKafkaLogger logger)
        {
            _cacheUserProvider = cacheUserProvider;
            _cacheUserValidator = cacheUserValidator;
            _cacheUserTransfer = cacheUserTransfer;
            _logger = logger;
        }

        public async Task<List<CacheUserDTO>> ListCacheUsersAsync(string keyPattern)
        {
            try
            {
                var pattern = _cacheUserValidator.NormalizeListPattern(keyPattern);
                var keys = await _cacheUserProvider.ListAuthKeysAsync(pattern);
                var users = new List<CacheUser>();
                foreach (var key in keys)
                {
                    var user = await loadCacheUserAsync(key);
                    if (user != null)
                        users.Add(user);
                }

                return _cacheUserTransfer.MapList(users);
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error, $"{nameof(ListCacheUsersAsync)}: list CacheUser failed. {ex.Message}");
                throw;
            }
        }

        public async Task<CacheUserDTO> GetCacheUserAsync(string authKey)
        {
            _cacheUserValidator.ValidateAuthKey(authKey);

            try
            {
                var item = await loadCacheUserAsync(authKey.Trim());
                if (item == null)
                    throw ECException.BuildNotFound("authKey");
                return _cacheUserTransfer.Map(item);
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(GetCacheUserAsync)}: get CacheUser failed. authKey={authKey}. {ex.Message}");
                throw;
            }
        }

        public async Task<CacheUserDTO> CreateCacheUserAsync(CreateCacheUserRequest request)
        {
            _cacheUserValidator.ValidateCreateRequest(request);
            request.AuthKey = request.AuthKey.Trim();

            try
            {
                if (await _cacheUserProvider.ExistsAsync(request.AuthKey))
                {
                    _logger.Log(LogLevel.Warning,
                        $"{nameof(CreateCacheUserAsync)}: authKey already exists. authKey={request.AuthKey}");
                    throw ECException.Build(HttpStatusCode.Conflict, "authKey already exists.");
                }

                var (subLogsJson, baseInfoJson) = _cacheUserValidator.SerializeCreatePayload(request);
                await _cacheUserProvider.CreateAsync(request.AuthKey, subLogsJson, baseInfoJson);
                var created = await loadCacheUserAsync(request.AuthKey);
                if (created == null || string.IsNullOrEmpty(created.AuthKey))
                {
                    _logger.Log(LogLevel.Warning,
                        $"{nameof(CreateCacheUserAsync)}: create returned empty. authKey={request.AuthKey}");
                    throw ECException.Build(HttpStatusCode.BadRequest, "Failed to create CacheUser.");
                }

                return _cacheUserTransfer.Map(created);
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(CreateCacheUserAsync)}: create CacheUser failed. authKey={request.AuthKey}. {ex.Message}");
                throw;
            }
        }

        public async Task<CacheUserDTO> UpdateCacheUserAsync(string authKey, UpdateCacheUserRequest request)
        {
            _cacheUserValidator.ValidateAuthKey(authKey);
            _cacheUserValidator.ValidateUpdateRequest(request);
            var trimmedKey = authKey.Trim();

            try
            {
                var existing = await loadCacheUserAsync(trimmedKey);
                if (existing == null)
                {
                    _logger.Log(LogLevel.Warning,
                        $"{nameof(UpdateCacheUserAsync)}: update CacheUser not found. authKey={authKey}");
                    throw ECException.BuildNotFound("authKey");
                }

                var hashFields = _cacheUserValidator.BuildUpdateHashFields(request);
                await _cacheUserProvider.UpdateAsync(trimmedKey, hashFields);
                var updated = await loadCacheUserAsync(trimmedKey);
                if (updated == null)
                {
                    _logger.Log(LogLevel.Warning,
                        $"{nameof(UpdateCacheUserAsync)}: update CacheUser returned null. authKey={authKey}");
                    throw ECException.BuildNotFound("authKey");
                }

                return _cacheUserTransfer.Map(updated);
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(UpdateCacheUserAsync)}: update CacheUser failed. authKey={authKey}. {ex.Message}");
                throw;
            }
        }

        public async Task DeleteCacheUserAsync(string authKey)
        {
            _cacheUserValidator.ValidateAuthKey(authKey);
            var trimmedKey = authKey.Trim();

            try
            {
                var existing = await loadCacheUserAsync(trimmedKey);
                if (existing == null)
                {
                    _logger.Log(LogLevel.Warning,
                        $"{nameof(DeleteCacheUserAsync)}: delete CacheUser no key. authKey={authKey}");
                    throw ECException.BuildNotFound("authKey");
                }

                await _cacheUserProvider.DeleteAsync(trimmedKey);
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(DeleteCacheUserAsync)}: delete CacheUser failed. authKey={authKey}. {ex.Message}");
                throw;
            }
        }

        private async Task<CacheUser> loadCacheUserAsync(string logicalAuthKey)
        {
            var entries = await _cacheUserProvider.GetHashAsync(logicalAuthKey);
            return _cacheUserTransfer.FromRedisHash(logicalAuthKey, entries);
        }
    }
}
