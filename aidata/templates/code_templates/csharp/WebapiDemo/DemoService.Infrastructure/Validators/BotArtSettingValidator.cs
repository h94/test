using System.Net;
using DemoService.Interface;
using DemoService.Model;
using ECCore;
using ECFramework;

namespace DemoService.Infrastructure.Validators
{
    [DependencyInjection(typeof(IBotArtSettingValidator))]
    public class BotArtSettingValidator : IBotArtSettingValidator
    {
        public void ValidateAccount(string account)
        {
            if (string.IsNullOrWhiteSpace(account))
                throw ECException.BuildBadRequest("account");
        }

        public void ValidateCreateRequest(CreateBotArtSettingRequest request)
        {
            if (request == null)
                throw ECException.Build(HttpStatusCode.BadRequest, "request is required.");
            if (string.IsNullOrWhiteSpace(request.Account))
                throw ECException.BuildBadRequest("account");
        }

        public void ValidateUpdateRequest(string account, UpdateBotArtSettingRequest request)
        {
            ValidateAccount(account);
            if (request == null)
                throw ECException.Build(HttpStatusCode.BadRequest, "request is required.");
        }
    }
}
