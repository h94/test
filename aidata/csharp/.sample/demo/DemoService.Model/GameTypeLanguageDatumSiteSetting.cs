using System;
using System.Collections.Generic;
using System.Text;

namespace DemoService.Model
{
    public class GameTypeLanguageDatumSiteSetting
    {
        public string TypeName { get; set; }
        public List<LanguageDatumSite> Languages { get; set; }
    }

    public class LanguageDatumSite
    {
        public string Code { get; set; }
        public string DatumSite { get; set; }
    }
}
