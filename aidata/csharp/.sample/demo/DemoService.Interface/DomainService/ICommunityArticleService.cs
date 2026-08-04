using System.Threading.Tasks;
using DemoService.Model;

namespace DemoService.Interface
{
    public interface ICommunityArticleService
    {
        Task<ArticleListPageResponse> ListArticlesAsync(string gameType, string index, string page, bool? showHidden,
            string leagues, string articTopics, string memberShips);

        Task<ArticleDocumentResponse> GetArticleAsync(string gameType, string articleId);

        Task<ArticleDocumentResponse> CreateArticleAsync(string gameType, CreateCommunityArticleRequest request);

        Task<ArticleDocumentResponse> UpdateArticleAsync(string gameType, EditCommunityArticleRequest request);

        Task<ArticleOkResponse> DeleteArticleAsync(string gameType, string id);
    }
}
