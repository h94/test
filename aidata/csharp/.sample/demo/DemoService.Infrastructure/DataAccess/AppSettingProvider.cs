using ECCore;
using DemoService.Interface;
using DemoService.Model;
using System;
using System.Collections.Generic;

namespace DemoService.Infrastructure.DataAccess;
[DependencyInjection(typeof(IAppSettingProvider))]

public class AppSettingProvider : IAppSettingProvider
{
    private readonly IECConfig _config;
    private readonly AppSettings _appSettings;

    public AppSettingProvider(IECConfig config)
    {
        _config = config;
        _appSettings = _config.GetAppSettings<AppSettings>();
    }

    public string GetFlags()
    {
        return _appSettings.Flags;
    }

    public string GetLangue(string countryCode)
    {
        string language = countryCode switch
        {
            "zh-CN" => "cn",
            "en-US" => "en",
            "ja-JP" => "jp",
            "ko-KR" => "kr",
            "th-TH" => "th",
            "zh-TW" => "tw",
            "vi-VN" => "vn",
            _ => "en"
        };
        return language;
    }

}
