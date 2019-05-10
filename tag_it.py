import aiohttp
import asyncio
import argparse
import json
import pprint


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


async def main(uname: str, key: str):
    print(f'Running with uname {uname}, key {key}')
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(uname, key)
        commits = await request(session, 'GET', 'https://api.github.com/repos/bball/testpy/commits/master', auth)
        pprint.pprint(commits)
        tags = await request(session, 'GET', 'https://api.github.com/repos/bball/testpy/tags', auth)
        pprint.pprint(tags)
        data = {'tag': f"TOXIC-{commits['sha'][:6]}",
                'message': 'TEST MSG',
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
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.uname, args.key))
