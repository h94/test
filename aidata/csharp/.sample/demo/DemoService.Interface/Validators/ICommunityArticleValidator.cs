using System.Collections.Generic;
using DemoService.Model;

namespace DemoService.Interface
{
    public interface ICommunityArticleValidator
    {
        void ValidateGameType(string gameType);

        void ValidateArticleId(string articleId);

        void ValidateCreateRequest(CreateCommunityArticleRequest request);

        void ValidateEditRequest(EditCommunityArticleRequest request);

        void ValidateDeleteId(string id);

        IReadOnlyDictionary<string, string> BuildListArticleQueryParameters(string index, string page, bool? showHidden,
            string leagues, string articTopics, string memberShips);

        IReadOnlyList<KeyValuePair<string, string>> BuildCreateArticleFormFields(CreateCommunityArticleRequest request);
    }
}
