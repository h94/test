using System;
using System.Collections.Generic;
using System.Text;

namespace DemoService.Model
{
    public class Mapping
    {
        public List<Souce> Souce { get; set; }
        public string Type { get; set; }
        public string Chinese { get; set; }
        public string System { get; set; }
    }
    public class Souce
    {
        public string Site { get; set; }
        public string PlayMode { get; set; }
    }
}
