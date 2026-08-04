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
    [DependencyInjection(typeof(IPgUserService))]
    public class PgUserService : IPgUserService
    {
        private readonly IPgUserProvider _pgUserProvider;
        private readonly IPgUserValidator _pgUserValidator;
        private readonly IKafkaLogger _logger;

        public PgUserService(IPgUserProvider pgUserProvider, IPgUserValidator pgUserValidator, IKafkaLogger logger)
        {
            _pgUserProvider = pgUserProvider;
            _pgUserValidator = pgUserValidator;
            _logger = logger;
        }

        public async Task<List<PgUser>> ListPgUsersAsync()
        {
            try
            {
                var list = await _pgUserProvider.ListAsync();
                return list ?? new List<PgUser>();
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error, $"{nameof(ListPgUsersAsync)}: list PgUser failed. {ex.Message}");
                throw;
            }
        }

        public async Task<PgUser> GetPgUserAsync(int id)
        {
            _pgUserValidator.ValidateUserId(id);

            try
            {
                var user = await _pgUserProvider.GetAsync(id);
                if (user == null)
                    throw ECException.BuildNotFound("id");
                return user;
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error, $"{nameof(GetPgUserAsync)}: get PgUser failed. id={id}. {ex.Message}");
                throw;
            }
        }

        public async Task<PgUser> CreatePgUserAsync(CreatePgUserRequest request)
        {
            _pgUserValidator.ValidateCreateRequest(request);
            request.Username = request.Username.Trim();

            try
            {
                var created = await _pgUserProvider.CreateAsync(request);
                if (created == null || created.Id == 0)
                {
                    _logger.Log(LogLevel.Warning,
                        $"{nameof(CreatePgUserAsync)}: create PgUser returned empty row (check users table schema). username={request.Username}");
                    throw ECException.Build(HttpStatusCode.BadRequest, "Failed to create user row.");
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
                    $"{nameof(CreatePgUserAsync)}: create PgUser failed. username={request.Username}. {ex.Message}");
                throw;
            }
        }

        public async Task<PgUser> UpdatePgUserAsync(int id, UpdatePgUserRequest request)
        {
            _pgUserValidator.ValidateUserId(id);
            _pgUserValidator.ValidateUpdateRequest(request);
            request.Username = request.Username.Trim();

            try
            {
                var updated = await _pgUserProvider.UpdateAsync(id, request);
                if (updated == null || updated.Id == 0)
                {
                    _logger.Log(LogLevel.Warning, $"{nameof(UpdatePgUserAsync)}: update PgUser not found. id={id}");
                    throw ECException.BuildNotFound("pg user");
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
                    $"{nameof(UpdatePgUserAsync)}: update PgUser failed. id={id}. {ex.Message}");
                throw;
            }
        }

        public async Task DeletePgUserAsync(int id)
        {
            _pgUserValidator.ValidateUserId(id);

            try
            {
                var deleted = await _pgUserProvider.DeleteAsync(id);
                if (!deleted)
                {
                    _logger.Log(LogLevel.Warning, $"{nameof(DeletePgUserAsync)}: delete PgUser no row affected. id={id}");
                    throw ECException.BuildNotFound("id");
                }
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(DeletePgUserAsync)}: delete PgUser failed. id={id}. {ex.Message}");
                throw;
            }
        }
    }
}
