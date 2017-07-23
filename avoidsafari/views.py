from django.template.response import SimpleTemplateResponse
from django.views import View
import requests
import datetime
from .avoid_finder import user_agent
from .models import Comment

# Create your views here.
class MainView(View):
    
    embed_cache = {};
    
    def get(self, req):
        return SimpleTemplateResponse(
            'recent_comments.html',
            context={
                'comments':zip(
                    map(
                        MainView.comment_to_embed_text,
                        Comment.objects.order_by('-timestamp')[:5]
                    ),
                    map(
                        MainView.comment_to_embed_text,
                        Comment.objects.filter(
                            timestamp__date__gt=datetime.datetime.now(
                                datetime.timezone.utc
                            ) - datetime.timedelta(days=1)
                        ).order_by('-length')[:5]
                    )
                )
            }
        )
    
    def comment_to_embed_text(comment):
        if comment not in MainView.embed_cache:
            MainView.embed_cache[comment] = requests.get(
                'https://www.reddit.com/oembed?url=https://www.reddit.com/comments/%s//%s'%(
                    comment.post_id,
                    comment.comment_id
                ),
                headers={
                    'User-Agent':user_agent
                }
            ).json()['html'].replace('<script async src=\"https://www.redditstatic.com/comment-embed.js\"></script>','')
        return MainView.embed_cache[comment]