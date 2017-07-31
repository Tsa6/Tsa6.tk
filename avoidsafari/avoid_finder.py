import praw
import os
import warnings
import re

fifths = 'Ee€Œœ£ÆÈÉÊËæèéêëĒēĔĕĖėĘęĚěŒœƎƏƐƸƹǝǢǣǼǽȄȅȆȇȨȩɆɇɘəɚɛɜɝɶΈΕΣέεξϵ϶ЀЁЄЕЭеэѐёєѤѥҼҽҾҿӔӕӖӗӘәӚӛӬӭԐԑԘԙعغڠۼݝݞݟࡘ٤६੬ઇઈઘછદધ૯ଽల౬౯౿ಲ೪೬ຄຍခဆၔይደዴድዼዽᎬᓬᕮᗕᗛᗴᘍᘿᙍᙓᙙᙠᙦᢄᣧᣯᣰᤉᤎᥱᦊᦏᦕᦚᦷᦾᧉ៩ᨦᨭᨹᨺᩀ᪖᪗ᬫᰀᰚᳮᴁᴂᴇᴔᴭᴱᴲᵆᵉᵊᵋᵫᶒᶓᶕḔḕḖḗḘḙḚḛḜḝẸẹẺẻẼẽẾếỀềỂểỄễỆệἐἑἒἓἔἕἘἙἚἛἜἝὲέῈΈₑₔ₠€ℇ℈℡℮ℯℰ⅀ⅇ↋∃∄∈∉∊∋∌∍∑⋲⋳⋴⋵⋶⋷⋸⋹⋺⋻⋼⋽⋾⋿⍷␃␄␅␇␐␗␙␛␡⒠Ⓔⓔ⥺⨊⨋⪪⪬ⰤⰥⱔⱕⱸⱻⲈⲉⴹⴺⵉⵟモョヨㅌ㋍㋎㋲㋵ꏁꏂꑾꑿ꒰ꓰꓱꗋꗍꗨꗩꘒꘓꜪꜫꟹꡀꢄꢅꢘꤕꤢꦌꦍ꧖ꫀꯐＥｅｮﾓﾖ￡🇪📧🔚🆓🆕'
divider = '-'*15
user_agent = 'net.tsa6.avoidhighlighter:v0.1 (by /u/Tsa6)'
defaults = {
    'THREAD_POOL_SIZE': 3,
    'REQUIRED_UNIQUE_WORDS': 15
}
wordlist = frozenset(map(str.strip, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wordlist.txt')).readlines()))


class CommentProcessor:
    def __init__(self, required_unique_words, allow_nsfw=False):
        self.required_unique_words = required_unique_words
        self.allow_nsfw = allow_nsfw
    
    # Returns comment if valid, otherwise None
    def __call__(self, comment):
        # Requirements:
        #   Not on /r/AVoid5 (for redundancy, previous selector sometimes slips up)
        #   Comment length is at least {5 * required_unique_words}, not including links or punctuation
        #   If {not allow_nsfw}, submission is SFW
        #   Contains no fifthglyphs, excluding those in urls and usernames
        #   Contains at least {required_unique_words} unique words
        if (
            comment.subreddit.display_name.lower() != 'avoid5'
            and len(remove_punctuation(remove_links(comment.body))) >= 5 * self.required_unique_words
            and (self.allow_nsfw or not comment.submission.over_18)
            and not(any([fifth in remove_links(remove_usernames(comment.body)) for fifth in fifths]))
            and len(set(re.split('\s+',remove_links(comment.body)))) > self.required_unique_words
            and len(
                set(
                    filter(
                        wordlist.__contains__,
                        map(
                            lambda w: re.sub(
                                '[^a-z\d]',
                                '',
                                w
                            ),
                            map(
                                str.lower,
                                re.split(
                                    '\s+',
                                    remove_links(
                                        comment.body
                                    )
                                )
                            )
                        )
                    )
                )
            ) >= self.required_unique_words
        ):
            return comment


def remove_links(comment_body):
    return re.sub(
        '\[(.+?)\]\(.+?\)',
        '\g<1>',
        comment_body
    )


def remove_usernames(comment_body):
    return re.sub(
        r'/u/[a-zA-Z0-9]+',
        '/u/',
        comment_body
    )


def remove_punctuation(comment_body):
    return re.sub(
        '[^a-zA-Z 0-9]+',
        '',
        comment_body
    )


def get_iterable(client_id, client_secret, thread_pool_size=defaults['THREAD_POOL_SIZE'], required_unique_words=defaults['REQUIRED_UNIQUE_WORDS'], allow_nsfw=False):
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        return filter(
            bool,
            map( #multiprocessing.Pool.imap_unordered can be used here, but uses more ram.  Make sure to set chunk size high if you do.
                CommentProcessor(
                    required_unique_words,
                    allow_nsfw=allow_nsfw
                ),
                reddit.subreddit('all-avoid5').stream.comments()
            )
        )


def get_iterable_from_environment(allow_nsfw=False):
    if 'REDDIT_CLIENT_ID' not in os.environ:
        raise RuntimeError('Please set the REDDIT_CLIENT_ID environment variable to a valid client id.')
    elif 'REDDIT_CLIENT_SECRET' not in os.environ:
        raise RuntimeError('Please set the REDDIT_CLIENT_SECRET environment variable to the client secret corresponding to your client id.')
    else:
        if 'THREAD_POOL_SIZE' not in os.environ:
            warnings.warn('THREAD_POOL_SIZE environment variable not specified, defaulting to %d'%defaults['THREAD_POOL_SIZE'])
        if 'REQUIRED_UNIQUE_WORDS' not in os.environ:
            warnings.warn('REQUIRED_UNIQUE_WORDS environment variable not specified, defaulting to %d'%defaults['REQUIRED_UNIQUE_WORDS'])
        return get_iterable(
            os.environ['REDDIT_CLIENT_ID'],
            os.environ['REDDIT_CLIENT_SECRET'],
            int(os.environ.get('THREAD_POOL_SIZE', defaults['THREAD_POOL_SIZE'])),
            int(os.environ.get('REQUIRED_UNIQUE_WORDS', defaults['REQUIRED_UNIQUE_WORDS'])),
            allow_nsfw=allow_nsfw
        )


def main():
    for comment in get_iterable_from_environment(allow_nsfw=True):
        print('%s/%s: %s\n%s'%(comment.submission, comment, comment.body, divider))

if __name__ == '__main__':
    main()
