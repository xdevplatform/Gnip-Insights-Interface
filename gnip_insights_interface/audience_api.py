import requests
import json
import logging
import re
from math import ceil
from farmhash import hash64 as farmhash64

from .utils import get_query_setup
from .exceptions import *

logger = logging.getLogger('audience_api')


def add_users(user_ids, unique_id, max_upload_size = 100000, max_segment_size = 3000000):
    """
    Split the users into segments based on maximum segment size
    """

    segment_name_base = unique_id

    unique_user_ids = list(set(user_ids)) 
    num_user_ids = len(unique_user_ids)
    num_segments = int(ceil(len(unique_user_ids)/float(max_segment_size)))
    size_segments = int(ceil(len(unique_user_ids)/float(num_segments)))
   
    logger.debug('{num_user_ids} user ids requires {num_segments} segments of size {size_segments}'.format(**locals()))
    for i, user_id_chunk in enumerate(chunks(unique_user_ids, size_segments)):
        logger.debug('Processing segment: ' + segment_name_base + '_' + str(i) )
        add_segment(user_id_chunk, segment_name_base + '_' + str(i), max_upload_size) 

def get_segment_id_by_name(segment_name):
    """
    Iterate over all viewable segments and return segment ID
    corresponding to input segment name.
    If it doesn't exist, return None
    """
    creds,auth,json_header = get_query_setup()
    base_url = creds['url']
    
    segment_id = None
    next_token = ""
    while next_token is not None:
        # get a page of results
        segment_check_response = requests.get(base_url + '/segments?next=' + next_token 
                , auth = auth
                , headers = json_header
        )
        logger.debug('segment_check_response code: ' + str(segment_check_response.status_code) )
        #logger.debug('segment_check_response text: ' + segment_check_response.text)
        
        # get segment if existing
        if 'segments' not in segment_check_response.json():
            raise SegmentQueryException(segment_check_response.text) 
    
        for existing_segment in segment_check_response.json()['segments']:
            if segment_name == existing_segment['name']:
                segment_id = existing_segment['id']   
                num_users = existing_segment['num_user_ids']
                logger.debug('Found segment id {}; name {}, with {} user ids'.format(segment_id,segment_name,num_users))
                return segment_id
    
        if 'next' in segment_check_response.json():
            next_token = segment_check_response.json()['next']
        else:
            next_token = None

    return segment_id

def add_segment(user_ids, segment_name, max_upload_size = 100000):
    """
    Check if segment already exists. If not, create it and upload uids.
    """
    
    segment_id = get_segment_id_by_name(segment_name)

    # if not existing, create the new segment
    if segment_id is None:
        creds,auth,json_header = get_query_setup()
        base_url = creds['url']
    
        logger.info('Segment not created; adding it')
        segment_creation_response = requests.post(base_url + '/segments'
                , auth = auth
                , headers = json_header
                , data = json.dumps({'name': segment_name})
                )
        if segment_creation_response.status_code > 299:
            raise SegmentCreateException(segment_creation_response.text) 
        logger.debug('segment_creation_resonse text:\n' + segment_creation_response.text)
        segment_id = segment_creation_response.json()['id']
        
        # split ids into max upload size 
        user_id_chunks = chunks(list(set(user_ids)), max_upload_size)
        uids_json_encoded = []
        for uid_chunk in user_id_chunks:
            uids_json_encoded.append(json.dumps({'user_ids': [str(x) for x in uid_chunk]}))

        # upload the chunks of user ids to a segment
        for num,uid_chunk_json_encoded in enumerate(uids_json_encoded):
            segment_post_ids = requests.post(base_url + '/segments/' + segment_id + '/ids'
                    , auth = auth
                    , headers = json_header
                    , data = uid_chunk_json_encoded
                    )
            logger.debug('Uploaded chunk ' + str(num))
            if segment_post_ids.status_code > 299:
                raise SegmentPostIdsException(segment_post_ids.text)
        logger.debug('segment_post_response text:\n' + segment_post_ids.text)

def query_audience(unique_id, groupings):
    """
    Get segments associated with unique_id
    Create and query audience
    """
    creds,auth,json_header = get_query_setup()
    base_url = creds['url']
    
    audience_name = unique_id
    next_token = ""
    segment_ids = []

    while next_token is not None:
        # check for existence of segment
        segment_check_response = requests.get(base_url + '/segments?next=' + next_token
                , auth = auth
                , headers = json_header
                )
        for entry in segment_check_response.json()['segments']:
            if re.search(r'{}_\d*$'.format(unique_id),entry['name']) is not None:
                logger.debug('adding segment ' + entry['name'] + '/' + entry['id'] + ' to list of matching segments')
                segment_ids.append(entry['id'])
        if 'next' in segment_check_response.json():
            next_token = segment_check_response.json()['next']
        else:
            next_token = None
    if len(segment_ids) == 0:
        raise NoSegmentsFoundException('no segments found with base name {}'.format(audience_name))

    # look for existing audience
    next_token = ""
    audience_id = None
    while next_token is not None:
        # get a page of audiences
        audience_query_response = requests.get(base_url + '/audiences?next=' + next_token 
                , auth = auth
                , headers = json_header
                )
        logger.debug('audience_query_response status: ' + str(audience_query_response.status_code))

        # get audience if it exists on this page
        for existing_audience in audience_query_response.json()['audiences']:
            if audience_name == existing_audience['name']:
                audience_id = existing_audience['id']
                logger.debug('Found audience name: ' + audience_name + '/ id: ' + audience_id + ' in existing audiences with segment ids ' + str(existing_audience['segment_ids']))

        # get next token if existing
        if 'next' in audience_query_response.json():
            next_token = audience_query_response.json()['next']
        else:
            next_token = None

    # make the audience if not existing
    if audience_id is None:
        audience_post = requests.post(base_url + '/audiences'
                , auth = auth
                , headers = json_header
                , data = json.dumps({'name': audience_name, 'segment_ids': segment_ids})
                )
        if audience_post.status_code > 299:
            raise AudiencePostException(audience_post.text) 
        audience_id = audience_post.json()['id']

    # make a request for information about the audience
    audience_info = requests.post(base_url + '/audiences/' + audience_id + '/query'
            , auth = auth
            , headers = json_header
            , data = groupings
            )
    if audience_info.status_code > 299:
        raise AudienceInfoException(audience_info.text) 
    logger.debug(audience_info.json())
    return audience_info.json()

def get_unique_id(user_ids):
    """
    hash the concatenated user IDs and use as segment/audience names
    """
    hashable_str = ''.join([str(i) for i in sorted(user_ids) ] )
    return str(hex(farmhash64(hashable_str))[2:])

def query_users(user_ids,groupings):
    try:
        # ensure unique IDs
        user_ids = set(user_ids)
        # create a unique identifier by hashing set of IDs
        unique_id = get_unique_id(user_ids)
        # add users to segment(s), if necessary
        add_users(user_ids, unique_id)
        # create audience, if necessary, and query it
        return query_audience(unique_id,groupings) 
    except AudienceApiException as e:
        return {'error' : str(e)}

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]

    
