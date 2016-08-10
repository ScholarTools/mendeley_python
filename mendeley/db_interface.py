# Third party imports
import pandas

# Local imports
from database import db_logging as db

# TODO: Possibly copy these base classes into a file within mendeley_python
from mendeley.optional import PaperInfo
from mendeley.optional import base_objects as obj
from mendeley.errors import *


def add_to_db(info):
    paper_info = _make_paper_info(info)
    has_file = info.get('file_attached')
    db.log_info(paper_info=paper_info, has_file=has_file)


def update_db_entry(info):
    new_info = _make_paper_info(info)

    # Get the saved information that exists for a given entry
    saved_info = db.get_saved_entry_obj(new_info)

    comparison_fields = saved_info.fields
    author_fields = saved_info.author_fields
    main_paper_id = saved_info.main_paper_id

    # Turn the new information into a combined dict
    new_full_dict = new_info.__dict__.copy()
    new_full_dict.update(new_info.entry.__dict__)
    if new_full_dict.get('authors') is not None:
        new_full_dict['authors'] = [author.__dict__ for author in new_full_dict['authors']]

    # Turn saved information into a combined dict
    saved_full_dict = saved_info.__dict__.copy()
    saved_full_dict.update(saved_info.entry.__dict__)
    if saved_full_dict.get('authors') is not None:
        saved_full_dict['authors'] = [author.__dict__ for author in saved_full_dict['authors']]

    updating_fields = []
    updating_values = []

    # Determine which fields have changed and need to be updated
    for field in comparison_fields:
        saved = saved_full_dict.get(field)
        new = new_full_dict.get(field)
        if saved == new:
            continue

        elif field == 'authors':
            # Each author is its own row in a separate Authors table.
            # This code replaces the saved bank of authors for a paper
            # with the new information. This covers creation and deletion
            # of authors, as well as updates to specific fields.
            for author in new:
                if author not in saved:
                    db.add_author(author, main_paper_id=main_paper_id)
            for author in saved:
                if author not in new:
                    db.delete_author(author, main_paper_id=main_paper_id)

        else:
            updating_fields.append(field)
            if saved is not None:
                updating_values.append(saved)
            else:
                updating_values.append(new)

    # Make the updating requests
    db.update_general_fields(new_full_dict.get('title'), updating_field=updating_fields,
                             updating_value=updating_values, filter_by_title=True)


def update_entry_field(identifying_value, updating_field, updating_value, filter_by_title=False, filter_by_doi=False):
    db.update_entry_field(identifying_value, updating_field, updating_value,
                          filter_by_title=filter_by_title, filter_by_doi=filter_by_doi)


def add_reference(refs, main_doi, main_title):
    db.add_references(refs=refs, main_paper_doi=main_doi, main_paper_title=main_title)


def update_reference_field(identifying_value, updating_field, updating_value, citing_doi=None, authors=None,
                           filter_by_title=False, filter_by_doi=False, filter_by_authors=False):
    db.update_reference_field(identifying_value, updating_field, updating_value, citing_doi=citing_doi, authors=authors,
                           filter_by_title=filter_by_title, filter_by_doi=filter_by_doi,
                              filter_by_authors=filter_by_authors)


def check_for_document(doi):
    try:
        docs = db.get_saved_info(doi)
    except MultipleDoiError:
        docs = None
        pass

    if docs is not None:
        return True
    else:
        return False


def follow_refs_forward(doi):
    return db.follow_refs_forward(doi)


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

    # Formatting
    if entry.year is not None:
        entry.year = str(entry.year)
    if entry.keywords is not None and isinstance(entry.keywords, list):
        entry.keywords = ', '.join(entry.keywords)

    entry.authors = []
    json_authors = df_dict.get('authors')
    if json_authors is not None:
        for auth in json_authors:
            author = obj.BaseAuthor()
            #TODO: This creates extra space if the first or last name is missing
            name = ' '.join([auth.get('first_name',''), auth.get('last_name','')])
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
            name = ' '.join([auth.get('first_name',''), auth.get('last_name','')])
            author.name = name
            entry.authors.append(author)

    ids = json.get('identifiers')
    if ids is not None:
        if 'doi' in ids.keys():
            entry.doi = ids.get('doi')
            paper_info.doi = ids.get('doi')

    paper_info.entry = entry

    return paper_info
