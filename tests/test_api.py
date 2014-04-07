import os, sys, shutil
from time import time

import pytest

inc_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, inc_path)
from internetarchive.api import *
import internetarchive.config

try:
    import internetarchive.mine
    can_test_mine = True
except ImportError:
    can_test_mine = False

def test_api_get_item():
    item = get_item('iacli-test-item')
    assert item.metadata['identifier'] == 'iacli-test-item'

def test_api_get_files():
    files = get_files('nasa', 'nasa_meta.xml')
    assert files[0].name == 'nasa_meta.xml'

    md_files = ['nasa_meta.xml', 'nasa_files.xml']
    files = get_files('nasa', md_files)
    assert all(f.name in md_files for f in files)
    
    og_files = ['NASAarchiveLogo.jpg', 'globe_west_540.jpg']
    files = get_files('nasa', source='original')
    assert all(f.name in og_files for f in files)

    og_files = ['NASAarchiveLogo.jpg', 'globe_west_540.jpg']
    files = get_files('nasa', formats='Archive BitTorrent')
    assert files[0].name == 'nasa_archive.torrent'

    xml_files = ['nasa_meta.xml', 'nasa_reviews.xml', 'nasa_files.xml']
    files = get_files('nasa', glob_pattern='*xml')
    assert all(f.name in xml_files for f in files)

def test_api_iter_files():
    file_generator = iter_files('nasa')
    assert not isinstance(file_generator, list)
    all_files = ['NASAarchiveLogo.jpg', 'globe_west_540.jpg', 'nasa_reviews.xml',
                 'nasa_meta.xml', 'nasa_archive.torrent', 'nasa_files.xml']
    assert all(f.name in all_files for f in list(file_generator))

def test_api_download(tmpdir):
    with tmpdir.as_cwd():
        r = download('iacli-test-item')
        assert os.path.exists('iacli-test-item')

def test_api_download_file(tmpdir):
    with tmpdir.as_cwd():
        r = download('nasa', 'nasa_meta.xml')

def test_api_search():
    s = search_items('identifier:nasa')
    assert s.num_found == 1

@pytest.mark.skipif('internetarchive.config.get_config().get("cookies") == None',
                    reason='requires authorization.')
class TestFunctionsNeedingCookies:
    def test_api_modify_metadata():
        valid_key = "foo-{k}".format(k=int(time()))
        md = {
            valid_key: 'test value'
        }
        r = modify_metadata('iacli-test-item', md)

    def test_api_remove_tag():
        md = {
            valid_key: 'REMOVE_TAG'
        }
        r = modify_metadata('iacli-test-item', md)

    def test_api_get_tasks():
        tasks = get_tasks()
        red_rows = get_tasks(task_type='red')

@pytest.mark.skipif('internetarchive.config.get_config().get("s3") == None',
                    reason='requires authorization.')
def test_funtions_needing_s3_keys():
    r = upload('iacli-test-item', 'setup.py', key='testsetup.py')



@pytest.mark.skipif('can_test_mine == False', reason='needs `internetarchive.mine` installed')
def test_mine():
    ids = ['iacli-test-item', 'nasa']
    miner = get_data_miner(ids)
    for i, item in miner:
        assert item.exists
