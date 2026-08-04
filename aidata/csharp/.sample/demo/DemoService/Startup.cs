using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.OpenApi.Models;
using Swashbuckle.AspNetCore.Swagger;
using Swashbuckle.AspNetCore.SwaggerGen;
using ECCore;
using ECFramework.ECService;
using Microsoft.AspNetCore.Diagnostics;
using System.Net.Http;

namespace DemoService
{

    public class Startup:ECServiceStartup
    {
        public Startup(IWebHostEnvironment env, IConfiguration configuration):base(env,configuration)
        {
            
        }


        // This method gets called by the runtime. Use this method to add services to the container.
        public override void ConfigureServices(IServiceCollection services)
        {
            services.AddHttpClient("Default")
                .ConfigurePrimaryHttpMessageHandler(() => new HttpClientHandler { 
                    ClientCertificateOptions = ClientCertificateOption.Manual, 
                    ServerCertificateCustomValidationCallback = (httpRequestMessage, cert, cetChain, policyErrors) => { return true; }
                });
            base.ConfigureServices(services);

        }

        
        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public override void Configure(IApplicationBuilder app)
        {
            base.Configure(app);

        }
       
        

        
    }
}
