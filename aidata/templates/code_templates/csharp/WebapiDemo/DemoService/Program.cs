using ECFramework.ECService;
using Microsoft.AspNetCore.Hosting;

namespace DemoService
{
    public class Program
    {
        public static void Main(string[] args)
        {
            CreateWebHostBuilder(args).Build().Run();
        }

        public static IWebHostBuilder CreateWebHostBuilder(string[] args) =>
            EDASFramework.CreateWebHostBuilder<Startup>(args);
    }
}
