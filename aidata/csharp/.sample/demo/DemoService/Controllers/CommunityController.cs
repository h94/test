using System.Threading.Tasks;
using DemoService.Interface;
using DemoService.Model;
using ECFramework.ECService;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace DemoService.Controllers
{
    /// <summary>
    /// Community article APIs.
    /// </summary>
    [ApiController]
    [Route("/api/community")]
    [UrlFilter]
    public class CommunityController : ControllerBase
    {
        private readonly ICommunityArticleService _communityArticleService;

        public CommunityController(ICommunityArticleService communityArticleService)
        {
            _communityArticleService = communityArticleService;
        }

        /// <summary>取得球種文章分頁 — GET /api/community/{gameType}/articles</summary>
        /// <param name="gameType">Game type.</param>
        /// <param name="index">Start index.</param>
        /// <param name="page">Page size or page number (depends on upstream API).</param>
        /// <param name="showHidden">Whether hidden articles are included.</param>
        /// <param name="leagues">League filter.</param>
        /// <param name="articTopics">Article topic filter.</param>
        /// <param name="memberShips">Membership filter.</param>
        /// <returns>Paged article response.</returns>
        [HttpGet("{gameType}/articles")]
        [ProducesResponseType(typeof(ArticleListPageResponse), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ArticleListPageResponse> ListArticles(string gameType,
            [FromQuery(Name = "index")] string index,
            [FromQuery(Name = "page")] string page,
            [FromQuery(Name = "show_hidden")] bool? showHidden,
            [FromQuery(Name = "leagues")] string leagues,
            [FromQuery(Name = "articTopics")] string articTopics,
            [FromQuery(Name = "memberShips")] string memberShips)
        {
            return await _communityArticleService.ListArticlesAsync(gameType, index, page, showHidden, leagues,
                articTopics, memberShips);
        }

        /// <summary>取得單篇文章 — GET /api/community/{gameType}/articles/{articleId}</summary>
        /// <param name="gameType">Game type.</param>
        /// <param name="articleId">Article id.</param>
        /// <returns>Article document.</returns>
        [HttpGet("{gameType}/articles/{articleId}")]
        [ProducesResponseType(typeof(ArticleDocumentResponse), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<ArticleDocumentResponse> GetArticle(string gameType, string articleId)
        {
            return await _communityArticleService.GetArticleAsync(gameType, articleId);
        }

        /// <summary>新增文章 — POST /api/community/{gameType}/articles（上游為 form-urlencoded，此處收 JSON 後轉發）</summary>
        /// <param name="gameType">Game type.</param>
        /// <param name="request">Create article request.</param>
        /// <returns>Created article document.</returns>
        [HttpPost("{gameType}/articles")]
        [ProducesResponseType(typeof(ArticleDocumentResponse), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ArticleDocumentResponse> CreateArticle(string gameType,
            [FromBody] CreateCommunityArticleRequest request)
        {
            return await _communityArticleService.CreateArticleAsync(gameType, request);
        }

        /// <summary>編輯文章 — PUT /api/community/{gameType}/editArticles</summary>
        /// <param name="gameType">Game type.</param>
        /// <param name="request">Edit article request.</param>
        /// <returns>Updated article document.</returns>
        [HttpPut("{gameType}/editArticles")]
        [ProducesResponseType(typeof(ArticleDocumentResponse), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<ArticleDocumentResponse> UpdateArticle(string gameType,
            [FromBody] EditCommunityArticleRequest request)
        {
            return await _communityArticleService.UpdateArticleAsync(gameType, request);
        }

        /// <summary>刪除文章 — DELETE /api/community/{gameType}/articles/{id}</summary>
        /// <param name="gameType">Game type.</param>
        /// <param name="id">Article id.</param>
        /// <returns>Delete result.</returns>
        [HttpDelete("{gameType}/articles/{id}")]
        [ProducesResponseType(typeof(ArticleOkResponse), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<ArticleOkResponse> DeleteArticle(string gameType, string id)
        {
            return await _communityArticleService.DeleteArticleAsync(gameType, id);
        }
    }
}
