using System.Threading.Tasks;
using DemoService.Interface;
using ECFramework.ECService;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace DemoService.Controllers
{
    /// <summary>
    /// Application settings APIs.
    /// </summary>
    [ApiController]
    [Route("/api/Settings")]
    [UrlFilter]
    public class SettingsController : ControllerBase
    {
        private readonly ISettingsService _settingsService;

        public SettingsController(ISettingsService settingsService)
        {
            _settingsService = settingsService;
        }

        /// <summary>
        /// Get Flags setting from AppSettings.
        /// </summary>
        /// <returns>Flags value.</returns>
        [HttpGet("getFlags")]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        public async Task<string> GetFlags()
        {
            return await _settingsService.GetFlagsAsync();
        }

        /// <summary>
        /// Get language code by country code.
        /// </summary>
        /// <param name="countryCode">Country code, such as zh-TW or en-US.</param>
        /// <returns>Mapped language code.</returns>
        [HttpGet("getLangue/{countryCode}")]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<string> GetLangue([FromRoute] string countryCode)
        {
            return await _settingsService.GetLangueAsync(countryCode);
        }
    }
}
