# Third party imports
import pandas

# Local imports
from database import db_logging as db

# TODO: Possibly copy these base classes into a file within mendeley_python
from mendeley.optional import PaperInfo
from mendeley.optional import base_objects as obj


def add_to_db(info):
    paper_info = _make_paper_info(info)
    db.log_info(paper_info=paper_info)


def update_db_entry(info):
    paper_info = _make_paper_info(info)
    table_obj = db.create_entry_table_obj(paper_info=paper_info)

    # Get the saved information that exists for a given entry
    saved_obj = db.get_saved_entry_obj(table_obj)

    # TODO: Compare the new updated entry with the saved version.
    # Can probably use the .fields attribute of the MainPaperInfo
    # class to only compare the values corresponding to those keys.
    # Need to turn paper_info into a dict or series of dicts.
    # Make a similar .fields attribute for Authors class.
    import pdb
    pdb.set_trace()


def _make_paper_info(info):
    if isinstance(info, PaperInfo):
        return info
    elif isinstance(info, dict):
        paper_info = _mendeley_json_to_paper_info(info)
        return paper_info
    elif isinstance(info, pandas.core.series.Series):
        paper_info = _mendeley_df_to_paper_info(info)
        return paper_info
    else:
        raise TypeError('Information could not be formatted for database entry.')


def _mendeley_df_to_paper_info(df_row):
    df_dict = df_row.to_dict()
    paper_info = PaperInfo()

    entry = obj.BaseEntry()
    entry.title = df_dict.get('title')
    entry.publication = df_dict.get('publisher')
    entry.year = df_dict.get('year')
    entry.volume = df_dict.get('volume')
    entry.issue = df_dict.get('issue')
    entry.pages = df_dict.get('pages')
    entry.keywords = df_dict.get('keywords')
    entry.abstract = df_dict.get('abstract')
    entry.notes = df_dict.get('notes')
    entry.pubmed_id = df_dict.get('pmid')
    entry.issn = df_dict.get('issn')

    entry.authors = []
    json_authors = df_dict.get('authors')
    if json_authors is not None:
        for auth in json_authors:
            author = obj.BaseAuthor()
            name = ' '.join([auth.get('first_name'), auth.get('last_name')])
            author.name = name
            entry.authors.append(author)

    ids = df_dict.get('identifiers')
    if ids is not None:
        if 'doi' in ids.keys():
            entry.doi = ids.get('doi')
            paper_info.doi = ids.get('doi')

    paper_info.entry = entry

    return paper_info



def _mendeley_json_to_paper_info(json):
    paper_info = PaperInfo()

    if 'Methylene-Atp' in json.get('title'):
        import pdb
        #pdb.set_trace()

    entry = obj.BaseEntry()
    entry.title = json.get('title')
    entry.publication = json.get('publisher')
    entry.year = json.get('year')
    entry.volume = json.get('volume')
    entry.issue = json.get('issue')
    entry.pages = json.get('pages')
    entry.keywords = json.get('keywords')
    entry.abstract = json.get('abstract')
    entry.notes = json.get('notes')

    entry.authors = []
    json_authors = json.get('authors')
    if json_authors is not None:
        for auth in json_authors:
            author = obj.BaseAuthor()
            name = ' '.join([auth.get('first_name'), auth.get('last_name')])
            author.name = name
            entry.authors.append(author)

    ids = json.get('identifiers')
    if ids is not None:
        if 'doi' in ids.keys():
            entry.doi = ids.get('doi')
            paper_info.doi = ids.get('doi')

    paper_info.entry = entry

    return paper_info
