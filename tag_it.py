import aiohttp
import asyncio
import argparse
import json
import pprint
from xml.dom import minidom


async def request(session, method, url, auth, data=None):
    try:
        async with session.request(method=method, url=url, auth=auth, json=data) as resp:
            await resp.read()
        text = await resp.text()
        json_val = json.loads(text)
        return json_val
    except Exception as ex:
        print(ex)
    return None


def extract_msg(test_file: str):
    try:
        tres = minidom.parse(test_file)
        itm = tres.getElementsByTagName('testsuite')[0]
        num_tests = int(itm.getAttribute('tests'))
        num_errors = int(itm.getAttribute('errors'))
        num_failures = int(itm.getAttribute('failures'))
        if num_failures + num_errors > 0:
            return False, f'{num_errors} Errors, {num_failures} Failures out of {num_tests} Tests.'
        return True, f'All {num_tests} Passed.'
    except Exception as ex:
        return 'Unknown'


async def main(uname: str, key: str, is_toxic: bool, test_file: str):
    print(f'Running with uname {uname}, key ******, toxic = {is_toxic}')
    success, msg = extract_msg(test_file)
    if not is_toxic and not success:
        is_toxic = True
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(uname, key)
        commits = await request(session, 'GET', 'https://api.github.com/repos/bball/testpy/commits/master', auth)
        tag_name = f"TOXIC-{commits['sha'][:6]}" if is_toxic else "v0.2"
        data = {'tag': tag_name,
                'message': msg,
                'object': commits['sha'],
                'type': 'commit'}
        success = await request(session, 'POST', 'https://api.github.com/repos/bball/testpy/git/tags', auth, data)
        pprint.pprint(success)
        if success:
            tag = success.get('tag', None)
            if tag:
                data = {'ref': f'refs/tags/{tag}',
                        'sha': success['sha']}
                success = await request(session, 'POST', 'https://api.github.com/repos/bball/testpy/git/refs', auth, data)
                pprint.pprint(success)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uname", dest='uname', help="Username")
    parser.add_argument("--key", dest='key', help="Key")
    parser.add_argument("--toxic", dest='toxic', help="IsToxic", action='store_true')
    parser.add_argument("--test_file", dest='test_file', help="Test Filename")
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.uname, args.key, args.toxic, args.test_file))
