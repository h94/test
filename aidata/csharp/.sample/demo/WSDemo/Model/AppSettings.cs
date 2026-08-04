using System;
using System.Collections.Generic;
using System.Text;
using ECCore;
namespace WSDemo
{
    public class AppSettings : DefaultAppSettings
    {
        public int MaxRetryTimes { get; set; }
        public string SystemFailMessage { get; set; }
        public string DefaultHelloMessage { get; set; }
    }
    public class TelegramAccount
    {
        public int ID { get; set; }
        public int Enabled { get; set; }
        public string APIToken { get; set; }
    }
}
