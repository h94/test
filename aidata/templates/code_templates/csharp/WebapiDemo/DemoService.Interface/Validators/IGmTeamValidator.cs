using DemoService.Model;

namespace DemoService.Interface
{
    public interface IGmTeamValidator
    {
        void ValidateTeamName(string teamName);

        void ValidateCreateRequest(CreateGmTeamRequest request);

        void ValidateUpdateRequest(string teamName, UpdateGmTeamRequest request);

        void NormalizeCreateRequest(CreateGmTeamRequest request);

        void NormalizeUpdateRequest(UpdateGmTeamRequest request);
    }
}
