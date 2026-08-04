using System.Collections.Generic;
using System.Threading.Tasks;
using DemoService.Model;

namespace DemoService.Interface
{
    public interface ICommunityProvider
    {
        Task<ArticleListPageResponse> ListArticlesAsync(string gameType, IReadOnlyDictionary<string, string> queryParameters);

        Task<ArticleDocumentResponse> GetArticleAsync(string gameType, string articleId);

        Task<ArticleDocumentResponse> CreateArticleAsync(string gameType,
            IReadOnlyList<KeyValuePair<string, string>> formFields);

        Task<ArticleDocumentResponse> UpdateArticleAsync(string gameType, EditCommunityArticleRequest request);

        Task<ArticleOkResponse> DeleteArticleAsync(string gameType, string id);
    }
}
