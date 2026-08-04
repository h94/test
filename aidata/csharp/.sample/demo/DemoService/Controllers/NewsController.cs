using System.Collections.Generic;
using System.Threading.Tasks;
using DemoService.Interface;
using DemoService.Model;
using ECFramework.ECService;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace DemoService.Controllers
{
    /// <summary>
    /// BotArt settings APIs.
    /// </summary>
    [ApiController]
    [Route("/api/News")]
    [UrlFilter]
    public class NewsController : ControllerBase
    {
        private readonly IBotArtSettingService _botArtSettingService;

        public NewsController(IBotArtSettingService botArtSettingService)
        {
            _botArtSettingService = botArtSettingService;
        }

        /// <summary>
        /// List BotArt settings.
        /// </summary>
        /// <returns>BotArt setting list.</returns>
        [HttpGet("listBotArtSettings")]
        [ProducesResponseType(typeof(List<BotArtSetting>), StatusCodes.Status200OK)]
        public async Task<List<BotArtSetting>> ListBotArtSettings()
        {
            return await _botArtSettingService.ListBotArtSettingsAsync();
        }

        /// <summary>
        /// Get BotArt setting by account.
        /// </summary>
        /// <param name="account">Target account.</param>
        /// <returns>BotArt setting.</returns>
        [HttpGet("getBotArtSetting/{account}")]
        [ProducesResponseType(typeof(BotArtSetting), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<BotArtSetting> GetBotArtSetting(string account)
        {
            return await _botArtSettingService.GetBotArtSettingAsync(account);
        }

        /// <summary>
        /// Create BotArt setting.
        /// </summary>
        /// <param name="request">Create request body.</param>
        /// <returns>Created BotArt setting.</returns>
        [HttpPost("createBotArtSetting")]
        [ProducesResponseType(typeof(BotArtSetting), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status409Conflict)]
        public async Task<BotArtSetting> CreateBotArtSetting([FromBody] CreateBotArtSettingRequest request)
        {
            return await _botArtSettingService.CreateBotArtSettingAsync(request);
        }

        /// <summary>
        /// Update BotArt setting.
        /// </summary>
        /// <param name="account">Target account.</param>
        /// <param name="request">Update request body.</param>
        /// <returns>Updated BotArt setting.</returns>
        [HttpPut("updateBotArtSetting/{account}")]
        [ProducesResponseType(typeof(BotArtSetting), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<BotArtSetting> UpdateBotArtSetting(string account,
            [FromBody] UpdateBotArtSettingRequest request)
        {
            return await _botArtSettingService.UpdateBotArtSettingAsync(account, request);
        }

        /// <summary>
        /// Delete BotArt setting.
        /// </summary>
        /// <param name="account">Target account.</param>
        [HttpDelete("deleteBotArtSetting/{account}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task DeleteBotArtSetting(string account)
        {
            await _botArtSettingService.DeleteBotArtSettingAsync(account);
        }
    }
}
