using System.Net;
using DemoService.Interface;
using DemoService.Model;
using ECCore;
using ECFramework;

namespace DemoService.Infrastructure.Validators
{
    [DependencyInjection(typeof(IGmTeamValidator))]
    public class GmTeamValidator : IGmTeamValidator
    {
        private const int MaxTeamNameLength = 10;

        public void ValidateTeamName(string teamName)
        {
            if (string.IsNullOrWhiteSpace(teamName))
                throw ECException.BuildBadRequest("teamName");
            if (teamName.Trim().Length > MaxTeamNameLength)
                throw ECException.Build(HttpStatusCode.BadRequest, $"teamName exceeds {MaxTeamNameLength} characters.");
        }

        public void ValidateCreateRequest(CreateGmTeamRequest request)
        {
            if (request == null)
                throw ECException.Build(HttpStatusCode.BadRequest, "request is required.");
            ValidateTeamName(request.TeamName);
        }

        public void ValidateUpdateRequest(string teamName, UpdateGmTeamRequest request)
        {
            ValidateTeamName(teamName);
            if (request == null)
                throw ECException.Build(HttpStatusCode.BadRequest, "request is required.");
        }

        public void NormalizeCreateRequest(CreateGmTeamRequest request)
        {
            request.Description ??= string.Empty;
            request.AuthToken ??= string.Empty;
            request.WhiteList ??= string.Empty;
        }

        public void NormalizeUpdateRequest(UpdateGmTeamRequest request)
        {
            request.Description ??= string.Empty;
            request.AuthToken ??= string.Empty;
            request.WhiteList ??= string.Empty;
        }
    }
}
