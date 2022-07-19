from rssparser import RSSParser

link = 'https://www.upwork.com/ab/feed/jobs/rss?q=automation+python&sort=recency&paging=0%3B50&api_params=1&securityToken=f361d2b991f52543cd5ebf1c1e2704d4c25415262392c9db8ad79cfea0df64c7d9d9abb5a8b46afb784a05f57269b724709e96aab8927334649e2f6fcfe23861&userUid=1034801991551606784&orgUid=1034801991555801089'
user_obj = {
    "id": 1,
    "rss": [],
    "settings": {
        "timezone": "UTC",
        "show_summary": "no",
        "chat": 364536,
    },
    "filters": {
        "exclude_countries": ['United States'],
        "add_skills": ['Selenium WebDrive'],
    }
}
posts = RSSParser(link, user_obj).parse_rss()
posts = posts[::-1]
show_summary = True
# rss is no filters
for post in posts:
    message = f"{post.to_str(show_summary)}"
    print(message)



