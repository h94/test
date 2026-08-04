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
    [DependencyInjection(typeof(IGmTeamService))]
    public class GmTeamService : IGmTeamService
    {
        private readonly IGmTeamProvider _gmTeamProvider;
        private readonly IGmTeamValidator _gmTeamValidator;
        private readonly IKafkaLogger _logger;

        public GmTeamService(IGmTeamProvider gmTeamProvider, IGmTeamValidator gmTeamValidator, IKafkaLogger logger)
        {
            _gmTeamProvider = gmTeamProvider;
            _gmTeamValidator = gmTeamValidator;
            _logger = logger;
        }

        public async Task<List<GmTeam>> ListGmTeamsAsync()
        {
            try
            {
                var list = await _gmTeamProvider.ListAsync();
                return list ?? new List<GmTeam>();
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error, $"{nameof(ListGmTeamsAsync)}: list GmTeam failed. {ex.Message}");
                throw;
            }
        }

        public async Task<GmTeam> GetGmTeamAsync(string teamName)
        {
            _gmTeamValidator.ValidateTeamName(teamName);

            try
            {
                var team = await _gmTeamProvider.GetAsync(teamName.Trim());
                if (team == null)
                    throw ECException.BuildNotFound("teamName");
                return team;
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(GetGmTeamAsync)}: get GmTeam failed. teamName={teamName}. {ex.Message}");
                throw;
            }
        }

        public async Task<GmTeam> CreateGmTeamAsync(CreateGmTeamRequest request)
        {
            _gmTeamValidator.ValidateCreateRequest(request);
            request.TeamName = request.TeamName.Trim();
            _gmTeamValidator.NormalizeCreateRequest(request);

            try
            {
                var created = await _gmTeamProvider.CreateAsync(request);
                if (created == null || string.IsNullOrEmpty(created.TeamName))
                {
                    _logger.Log(LogLevel.Warning,
                        $"{nameof(CreateGmTeamAsync)}: create GmTeam returned empty row. teamName={request.TeamName}");
                    throw ECException.Build(HttpStatusCode.BadRequest, "Failed to create team row.");
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
                    $"{nameof(CreateGmTeamAsync)}: create GmTeam failed. teamName={request.TeamName}. {ex.Message}");
                throw;
            }
        }

        public async Task<GmTeam> UpdateGmTeamAsync(string teamName, UpdateGmTeamRequest request)
        {
            _gmTeamValidator.ValidateUpdateRequest(teamName, request);
            var trimmedTeamName = teamName.Trim();
            _gmTeamValidator.NormalizeUpdateRequest(request);

            try
            {
                var updated = await _gmTeamProvider.UpdateAsync(trimmedTeamName, request);
                if (updated == null)
                {
                    _logger.Log(LogLevel.Warning,
                        $"{nameof(UpdateGmTeamAsync)}: update GmTeam not found. teamName={teamName}");
                    throw ECException.BuildNotFound("team");
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
                    $"{nameof(UpdateGmTeamAsync)}: update GmTeam failed. teamName={teamName}. {ex.Message}");
                throw;
            }
        }

        public async Task DeleteGmTeamAsync(string teamName)
        {
            _gmTeamValidator.ValidateTeamName(teamName);

            try
            {
                var deleted = await _gmTeamProvider.DeleteAsync(teamName.Trim());
                if (!deleted)
                {
                    _logger.Log(LogLevel.Warning,
                        $"{nameof(DeleteGmTeamAsync)}: delete GmTeam no row affected. teamName={teamName}");
                    throw ECException.BuildNotFound("teamName");
                }
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(DeleteGmTeamAsync)}: delete GmTeam failed. teamName={teamName}. {ex.Message}");
                throw;
            }
        }
    }
}
