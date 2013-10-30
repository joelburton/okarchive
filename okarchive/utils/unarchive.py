import csv
import datetime

def import_journal(zfile):
    ...

def import_post(journal):
    with open('/tmp/test.csv') as fh:
        contents = iter(csv.reader(fh))

        _ = next(contents)
        _ = next(contents)

        _ = next(contents)
        title = _[0][len('TITLE: '):]

        _ = next(contents)
        body = _[0][len('CONTENT: '):]

        _ = next(contents)
        dateraw = _[0][len('Date posted: '):]
        dt = datetime.datetime.strptime(dateraw, '%A, %d %b %Y, %H:%M:%S ')

        post = journal.add_post(title=title,
                         text=body,
                         creation_date=dt,
                         modification_date=dt,
                         _flush=True)

        while True:
            try:
                _ = next(contents)
            except StopIteration:
                break

            _ = next(contents)
            user = _[0][len('USER: '):]

            _ = next(contents)
            text = _[0][len('Comment: '):]

            _ = next(contents)
            dateraw = _[0][len('Comment Date: '):]
            dt = datetime.datetime.strptime(dateraw, '%A, %d %b %Y, %H:%M:%S ')

            _ = next(contents)

            post.add_comment(text=text,
                             creation_date=dt,
                             modification_date=dt,
                             user_id=user,
                             )

if __name__ == '__main__':
    from okarchive.models import siteRoot
    import transaction
    import sys
    from sqlalchemy import engine_from_config

    from pyramid.paster import (
        get_appsettings,
        setup_logging,
        )

    from okarchive.models import (
        DBSession,
        Base,
        Journal,
        Post,
        User,
        )


    config_uri = sys.argv[1]
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    journal = siteRoot['journals']['distractionbike']
    import_post(journal)
    transaction.commit()