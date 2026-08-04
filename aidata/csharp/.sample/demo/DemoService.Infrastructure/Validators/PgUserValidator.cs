using System.Net;
using DemoService.Interface;
using DemoService.Model;
using ECCore;
using ECFramework;

namespace DemoService.Infrastructure.Validators
{
    [DependencyInjection(typeof(IPgUserValidator))]
    public class PgUserValidator : IPgUserValidator
    {
        public void ValidateUserId(int id)
        {
            if (id <= 0)
                throw ECException.BuildBadRequest("id");
        }

        public void ValidateCreateRequest(CreatePgUserRequest request)
        {
            if (request == null)
                throw ECException.Build(HttpStatusCode.BadRequest, "request is required.");
            if (string.IsNullOrWhiteSpace(request.Username))
                throw ECException.BuildBadRequest("username");
        }

        public void ValidateUpdateRequest(UpdatePgUserRequest request)
        {
            if (request == null)
                throw ECException.Build(HttpStatusCode.BadRequest, "request is required.");
            if (string.IsNullOrWhiteSpace(request.Username))
                throw ECException.BuildBadRequest("username");
        }
    }
}
