using System.Collections.Generic;

namespace DemoService.Model
{
    public class CompanyAuthority
    {
        public string CompanyCode { get; set; }
        public List<Subscribe> Subscribes { get; set; }
    }

    public class Subscribe
    {
        public string Site { get; set; }
        public List<SubscribeCategory> SubscribeCategories { get; set; }
    }

    public class SubscribeCategory
    {
        public string GameType { get; set; }
        public string[] SubscribeTypes { get; set; }
    }


}