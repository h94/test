using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using ECCore;
using Microsoft.AspNetCore.Http;
using System.Diagnostics;

namespace WSDemo
{
    public class Worker : BackgroundService
    {
        private readonly IKafkaLogger _logger;
        private readonly IRestfulClient _restfulClient;
        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly IECConfig _eCConfig;
        private readonly IMySQLManager _mySQL;
        public Worker(IKafkaLogger logger, IRestfulClient restfulClient, IHttpContextAccessor httpContextAccessor, IECConfig eCConfig, IMySQLManager mySQL)
        {
            _logger = logger;
            _restfulClient = restfulClient;
            _httpContextAccessor = httpContextAccessor;
            _eCConfig = eCConfig;
            _mySQL = mySQL;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            int iSleep = 50;
            int iRunMins = 3 * 60 * 1000;
            int iRun = 0;
            while (iRun < iRunMins / iSleep)
            {
                //Debug.WriteLine(_eCConfig.GetAppSettings<AppSettings>().DefaultHelloMessage);
                //RestfulRequest req = new RestfulRequest(_httpContextAccessor, _eCConfig);
                //req.CreateRequest("GetAccounts");
                //var data = await _restfulClient.SendAsync<List<TelegramAccount>>(req);
                //Debug.WriteLine("APIToken="+data[0].APIToken);
                //var cmd = _mySQL.CreateDBCommand("GM");
                //cmd.CommandText = "SELECT APIName FROM APIs LIMIT 0,1";
                //var rtn = cmd.ExecuteScalar();

                _logger.Log(LogLevel.Information, "Test");
                await Task.Delay(iSleep, stoppingToken);
                iRun++;
            }
        }
    }
}
