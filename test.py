import requests
import re
import json
from bs4 import BeautifulSoup
import sys


def get_users(links, iter_count=3):
    users = []

    for link in links:

        url = link + '?__a=1'

        request = requests.get(url).text
        page_info = json.loads(request)

        posts = page_info['graphql']['location']['edge_location_to_media']['edges']
        id = page_info['graphql']['location']['id']

        users.extend(extract_users(posts))

        has_next_page = page_info['graphql']['location']['edge_location_to_media']['page_info']['has_next_page']
        end_cursor = page_info['graphql']['location']['edge_location_to_media']['page_info']['end_cursor']

        i = 0
        while has_next_page and i < iter_count:
            i += 1
            print(i)


            url = 'https://www.instagram.com/graphql/query/?query_hash=ac38b90f0f3981c42092016a37c59bf7&variables={"id":"' + id + '","first":12,"after":"' + end_cursor + '"}'
            context = {
                'Cookie': r'TODO'
            }

            request = requests.get(url, headers=context).text
            page_info = json.loads(request)

            posts = page_info['data']['location']['edge_location_to_media']['edges']

            users.extend(extract_users(posts))

            has_next_page = page_info['data']['location']['edge_location_to_media']['page_info']['has_next_page']
            end_cursor = page_info['data']['location']['edge_location_to_media']['page_info']['end_cursor']

    validated = []
    for user in users:
        if validate_user(user):
            validated.append(user)

    phones = {}
    print(validated)

    for user in validated:
        num = find_phone_number(user)
        if num is not None:
            phones[user] = num
        else:
            phones[user] = 'nodata'

    return phones


def extract_users(posts):
    users = []
    for post in posts:
        post = post['node']
        user = get_user_name_by_post(post['shortcode'])
        users.append(user)

    return users


def validate_user(username):
    url = 'https://www.instagram.com/' + username

    html = requests.get(url).text

    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find_all('meta', attrs={'property': 'og:description'
                                        })
    followers = data[0].get('content').split()[0]
    followers = followers.replace(',', '')
    followers = followers.replace(',', '')

    if 'k' in followers:
        return True

    if int(followers) > 1000:
        return True
    else:
        return False


def find_phone_number(username):
    url = 'https://www.instagram.com/' + username

    html = requests.get(url).text

    description = re.search(r'description":(.*)"', html)
    if description is not None:
        description = description.group(0)
        phone_num = re.search(r'\+\d{9,13}', description)

        if phone_num is not None:
            return phone_num.group(0)
        else:
            return None


def get_user_name_by_post(shortcode):
    url = 'https://instagram.com/p/' + shortcode + '/?__a=1'

    request = requests.get(url).text
    page_info = json.loads(request)

    username = page_info['graphql']['shortcode_media']['owner']['username']

    return username


if __name__ == '__main__':

    iter_count = int(sys.argv[1])

    with open('input.txt', 'r') as f:
        links = f.readlines()

    links = [x.strip() for x in links]

    phones = get_users(links, iter_count)

    with open('output.txt', 'a') as f:
        for user in phones.keys():
            f.write('{}:{}\n'.format(user, phones[user]))
