using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Policy;
using System.Threading.Tasks;
using Cassandra.Mapping;
using ECCore;
namespace DemoService.Model
{
    public class AppSettings : DefaultAppSettings
    {
        public string Flags { get; set; }
        public int MaxRetryTimes { get; set; }
        public string SystemFailMessage { get; set; }
        public string DefaultHelloMessage { get; set; }
        public List<CryptoList> CryptoList { get; set; }
        public List<StableList> StableList { get; set; }
        public List<ForexList> ForexList { get; set; }
        public Site[] Sites { get; set; }
        public Mapping[] Mapping { get; set; }
        public Mapping[] OtherMapping { get; set; }
        public CompanyAuthority[] CompanyAuthority { get; set; }
        public List<GameTypeLanguageDatumSiteSetting> GameTypeLanguageDatumSite { get; set; }
    }
    public class TestData
    {
        public string Test1 { get; set; }
        public string Test2 { get; set; }
        public string Test3 { get; set; }
    }
    public class Group
    {
        public string GroupID { get; set; }
        public int Enabled { get; set; }
        public int GroupType { get; set; }
        public string Description { get; set; }
    }
    public class Team
    {
        public string TeamName { get; set; }
        public string AuthToken { get; set; }
        public string Description { get; set; }
    }
    public class CryptoList
    {
        public string Site { get; set; }
        public List<string> FXRateNames { get; set; }
    }

    public class StableList
    {
        public string Site { get; set; }
        public List<string> FXRateNames { get; set; }
    }

    public class ForexList
    {
        public string Site { get; set; }
        public List<string> FXRateNames { get; set; }
    }

    public class Ticket
    {
        public int T1 { get; set; }
        public int T2 { get; set; }
        public int T3 { get; set; }
        public int T4 { get; set; }
        public int T5 { get; set; }
        public int T6 { get; set; }
        public int T7 { get; set; }
        public int T8 { get; set; }
        public int T9 { get; set; }
        public int T10 { get; set; }
        public string T11 { get; set; }
        public decimal T12 { get; set; }
        public decimal T13 { get; set; }
        public Int64 T14 { get; set; }
        public string T15 { get; set; }
    }
    public class IPTicket
    {
        public int T2 { get; set; }
        public string T16 { get; set; }
        public string T16C { get; set; }
        public IDictionary<string,string> tickets { get; set; }
    }
    public class TestTicket
    {
        public int T2 { get; set; }
        public string T16 { get; set; }
        public IList<string> tickets { get; set; }
    }
    public class AlertMessage
    {
        public string Topic { get; set; }
        public string Message { get; set; }
    }
    public class GeoInfo
    {
        public string IP { get; set; }
        public string Country { get; set; }
    }
    public class MachineInfo
    {
        public string MachineName { get; set; }
        public string AddDate { get; set; }
        public string Status { get; set; }
        public string ControllerStatus { get; set; }
        public string BwinCrawlerStatus { get; set; }
        public string KuCrawlerStatus { get; set; }
        public string PinnacleCrawlerStatus { get; set; }
        public string PinnacleInplayCrawlerStatus { get; set; }
        public string TWSLCrawlerStatus { get; set; }
        public IDictionary<string, string> CrawlerServiceStatus { get; set; }
        public string Bet365EStatus { get; set; }
        public string BwinEStatus { get; set; }
        public string PS3838EStatus { get; set; }
        public string HarStatus { get; set; }
        public string Bet365Command { get; set; }
        public string KUCommand { get; set; }
        public string B365CmdString { get; set; }
        public string KUCmdString { get; set; }
    }
}
