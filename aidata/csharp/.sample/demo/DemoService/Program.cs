using ECFramework.ECService;

namespace DemoService
{
    public class Program
    {
        public static void Main(string[] args)
        {
            EDASFramework.Bootstrap<Startup>(args);
        }

    }
}
