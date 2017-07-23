from django.db import IntegrityError
import datetime
from . import avoid_finder
from .models import Comment


def main():
    for comment in avoid_finder.get_iterable_from_environment():
        try:
            Comment(
                post_id=str(comment.submission),
                comment_id=str(comment),
                timestamp=datetime.datetime.fromtimestamp(comment.created, datetime.timezone.utc),
                length=len(avoid_finder.remove_links(comment.body))
            ).save()
            print('%s/%s: %s\n' % (comment.submission, comment, comment.body))
        except IntegrityError:
            print('[Redundant] %s/%s\n' % (comment.submission, comment, comment.body))

if __name__ == '__main__':
    main()
