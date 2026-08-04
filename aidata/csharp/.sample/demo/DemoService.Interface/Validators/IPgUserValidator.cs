using DemoService.Model;

namespace DemoService.Interface
{
    public interface IPgUserValidator
    {
        void ValidateUserId(int id);

        void ValidateCreateRequest(CreatePgUserRequest request);

        void ValidateUpdateRequest(UpdatePgUserRequest request);
    }
}
