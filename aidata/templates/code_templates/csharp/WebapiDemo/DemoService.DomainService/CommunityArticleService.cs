using System;
using System.Threading.Tasks;
using DemoService.Interface;
using DemoService.Model;
using ECCore;
using ECFramework;
using Microsoft.Extensions.Logging;

namespace DemoService.DomainService
{
    [DependencyInjection(typeof(ICommunityArticleService))]
    public class CommunityArticleService : ICommunityArticleService
    {
        private readonly ICommunityProvider _communityProvider;
        private readonly ICommunityArticleValidator _communityArticleValidator;
        private readonly IKafkaLogger _logger;

        public CommunityArticleService(
            ICommunityProvider communityProvider,
            ICommunityArticleValidator communityArticleValidator,
            IKafkaLogger logger)
        {
            _communityProvider = communityProvider;
            _communityArticleValidator = communityArticleValidator;
            _logger = logger;
        }

        public async Task<ArticleListPageResponse> ListArticlesAsync(string gameType, string index, string page,
            bool? showHidden, string leagues, string articTopics, string memberShips)
        {
            _communityArticleValidator.ValidateGameType(gameType);
            var queryParameters =
                _communityArticleValidator.BuildListArticleQueryParameters(index, page, showHidden, leagues,
                    articTopics, memberShips);

            try
            {
                return await _communityProvider.ListArticlesAsync(gameType.Trim(), queryParameters);
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(ListArticlesAsync)}: list articles failed. gameType={gameType}. {ex.Message}");
                throw;
            }
        }

        public async Task<ArticleDocumentResponse> GetArticleAsync(string gameType, string articleId)
        {
            _communityArticleValidator.ValidateGameType(gameType);
            _communityArticleValidator.ValidateArticleId(articleId);

            try
            {
                return await _communityProvider.GetArticleAsync(gameType.Trim(), articleId.Trim());
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(GetArticleAsync)}: get article failed. gameType={gameType}, articleId={articleId}. {ex.Message}");
                throw;
            }
        }

        public async Task<ArticleDocumentResponse> CreateArticleAsync(string gameType, CreateCommunityArticleRequest request)
        {
            _communityArticleValidator.ValidateGameType(gameType);
            _communityArticleValidator.ValidateCreateRequest(request);
            var formFields = _communityArticleValidator.BuildCreateArticleFormFields(request);

            try
            {
                return await _communityProvider.CreateArticleAsync(gameType.Trim(), formFields);
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(CreateArticleAsync)}: create article failed. gameType={gameType}. {ex.Message}");
                throw;
            }
        }

        public async Task<ArticleDocumentResponse> UpdateArticleAsync(string gameType, EditCommunityArticleRequest request)
        {
            _communityArticleValidator.ValidateGameType(gameType);
            _communityArticleValidator.ValidateEditRequest(request);

            try
            {
                return await _communityProvider.UpdateArticleAsync(gameType.Trim(), request);
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(UpdateArticleAsync)}: update article failed. gameType={gameType}, id={request.Id}. {ex.Message}");
                throw;
            }
        }

        public async Task<ArticleOkResponse> DeleteArticleAsync(string gameType, string id)
        {
            _communityArticleValidator.ValidateGameType(gameType);
            _communityArticleValidator.ValidateDeleteId(id);

            try
            {
                return await _communityProvider.DeleteArticleAsync(gameType.Trim(), id.Trim());
            }
            catch (HttpResponseException)
            {
                throw;
            }
            catch (Exception ex)
            {
                _logger.Log(LogLevel.Error,
                    $"{nameof(DeleteArticleAsync)}: delete article failed. gameType={gameType}, id={id}. {ex.Message}");
                throw;
            }
        }
    }
}
