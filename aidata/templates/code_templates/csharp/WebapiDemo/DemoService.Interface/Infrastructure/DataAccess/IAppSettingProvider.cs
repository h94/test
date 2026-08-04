using System.Collections.Generic;

namespace DemoService.Interface;

public interface IAppSettingProvider
{
    public string GetFlags();
    public string GetLangue(string countryCode);
}
