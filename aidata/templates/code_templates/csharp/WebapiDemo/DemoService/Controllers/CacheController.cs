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
    /// CacheUser management APIs.
    /// </summary>
    [ApiController]
    [Route("/api/Cache")]
    [UrlFilter]
    public class CacheController : ControllerBase
    {
        private readonly ICacheUserService _cacheUserService;

        public CacheController(ICacheUserService cacheUserService)
        {
            _cacheUserService = cacheUserService;
        }

        /// <summary>
        /// List CacheUser records by key pattern.
        /// </summary>
        /// <param name="pattern">Redis key pattern. Default is "*".</param>
        /// <returns>CacheUser DTO list.</returns>
        [HttpGet("listCacheUsers")]
        [ProducesResponseType(typeof(List<CacheUserDTO>), StatusCodes.Status200OK)]
        public async Task<List<CacheUserDTO>> ListCacheUsers([FromQuery] string pattern = "*")
        {
            return await _cacheUserService.ListCacheUsersAsync(pattern);
        }

        /// <summary>
        /// Get a CacheUser by auth key.
        /// </summary>
        /// <param name="authKey">Target auth key.</param>
        /// <returns>CacheUser DTO.</returns>
        [HttpGet("getCacheUser/{authKey}")]
        [ProducesResponseType(typeof(CacheUserDTO), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<CacheUserDTO> GetCacheUser(string authKey)
        {
            return await _cacheUserService.GetCacheUserAsync(authKey);
        }

        /// <summary>
        /// Create a CacheUser.
        /// </summary>
        /// <param name="request">Create request body.</param>
        /// <returns>Created CacheUser DTO.</returns>
        [HttpPost("createCacheUser")]
        [ProducesResponseType(typeof(CacheUserDTO), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status409Conflict)]
        public async Task<CacheUserDTO> CreateCacheUser([FromBody] CreateCacheUserRequest request)
        {
            return await _cacheUserService.CreateCacheUserAsync(request);
        }

        /// <summary>
        /// Update a CacheUser.
        /// </summary>
        /// <param name="authKey">Target auth key.</param>
        /// <param name="request">Update request body.</param>
        /// <returns>Updated CacheUser DTO.</returns>
        [HttpPut("updateCacheUser/{authKey}")]
        [ProducesResponseType(typeof(CacheUserDTO), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<CacheUserDTO> UpdateCacheUser(string authKey,
            [FromBody] UpdateCacheUserRequest request)
        {
            return await _cacheUserService.UpdateCacheUserAsync(authKey, request);
        }

        /// <summary>
        /// Delete a CacheUser.
        /// </summary>
        /// <param name="authKey">Target auth key.</param>
        [HttpDelete("deleteCacheUser/{authKey}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task DeleteCacheUser(string authKey)
        {
            await _cacheUserService.DeleteCacheUserAsync(authKey);
        }
    }
}
