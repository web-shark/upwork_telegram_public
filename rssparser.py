import feedparser
import re
import pytz
import timeago
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass
class JobPost:
    url: str
    budget: str
    published: str
    title: str
    summary: str
    budget_numeric: int
    country: str
    skills: str
    hourly: bool

    def to_str(self, show_summary):
        job_type = "Hourly" if self.hourly else "Fixed-price"
        timenow = datetime.utcnow().replace(
            tzinfo=pytz.utc).astimezone(pytz.timezone("UTC"))

        if show_summary:
            return f"\n<b>Title</b>: {self.title}\n<b>Summary</b>: {self.summary[:500]}" \
                   f"\n<b>Budget</b>: {self.budget}\n<b>Type</b>: {job_type}" \
                   f"\n<b>Published</b>: {str(timeago.format(self.published, timenow))}" \
                   f"\n<b>Country</b>: {self.country}\n<b>Skills</b>: {self.skills} "
        else:
            return f"\n<b>Title</b>: {self.title}\n<b>Budget</b>: {self.budget}" \
                   f"\n<b>Type</b>: {job_type}\n<b>Published</b>: {str(timeago.format(self.published, timenow))}" \
                   f"\n<b>Country</b>: {self.country}\n<b>Skills</b>: {self.skills} "


class RSSParser:
    def __init__(self, url: str, user_obj: Dict[str, Any]) -> None:
        self.url = url
        self.user_settings = user_obj["settings"]
        self.user_filters = user_obj["filters"]
        self.user_id = user_obj["id"]

    def _load_rss(self):
        return feedparser.parse(self.url)

    def _parse_budget(self, summary):
        if "Hourly Range" in summary:
            budget = re.search(
                r'<b>Hourly Range</b>:([^\n]+)', summary).group(1)
            budget = budget.strip()
            budget_no_dollar = budget.replace('$', '')
            return budget, float(budget_no_dollar.split("-")[0]), True
        try:
            budget = '$' + re.search(
                r'<b>Budget</b>: \$(\d[0-9,.]+)',
                summary
            ).group(1)
            budget = re.sub('<[^<]+?>', '', budget)
        except AttributeError:
            budget = 'N/A'
        try:
            return budget, int(budget[:-1]), False
        except:
            return budget, None, (budget == "N/A")

    def _parse_skills(self, summary):
        try:
            skills = re.search(
                r'<b>Skills</b>:([^\n]+)', summary).group(1)
            skills = re.sub(' ', '', skills)
            return skills
        except:
            return 'N/A'

    def _parse_country(self, summary):
        try:
            return re.search(
                r'<b>Country</b>:([^\n]+)', summary).group(1)
        except:
            return 'N/A'

    def _clean_summary(self, summary):
        pattern = re.compile(r'<.*?>')
        summary = summary.split('<br /><b>')[0]
        return pattern.sub('', summary)

    def _parse_published(self, published_str):
        # Format Example: Sat, 24 Oct 2020 03:06:03 +0000
        user_timezone = self.user_settings.get("timezone", "UTC")
        published = datetime.strptime(
            published_str, '%a, %d %b %Y %H:%M:%S %z'
        ).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(user_timezone))
        timenow = datetime.utcnow().replace(
            tzinfo=pytz.utc).astimezone(pytz.timezone(user_timezone))
        return published

    def _filter_skills(self, job: JobPost):
        add_skills = self.user_filters.get("add_skills", None)
        if add_skills is not None:
            for skills in add_skills:
                if job.country.strip().lower() == skills.lower():
                    return True
        return False

    def _filter_job(self, job: JobPost):
        excluded_countries = self.user_filters.get("exclude_countries", None)

        if excluded_countries is not None:
            for country in excluded_countries:
                if job.country.strip().lower() == country.lower():
                    return False

        return True

    def parse_rss(self):
        entries = self._load_rss().entries
        job_posts = []
        for entry in entries:
            # if jobs_db.job_exits(entry['id'], self.user_id):
            #     continue
            budget, budget_numeric, hourly = self._parse_budget(
                entry['summary'])
            country = self._parse_country(entry['summary'])
            skills = self._parse_skills(entry['summary'])
            published = self._parse_published(entry['published'])
            job_post = JobPost(
                entry.get("id", "#"),
                budget,
                published,
                entry.get("title"),
                self._clean_summary(entry.get("summary")),
                budget_numeric,
                country,
                skills,
                hourly
            )
            if self._filter_job(job_post):
                job_posts.append(job_post)
            # jobs_db.insert_job(entry["id"], self.user_id)
        return job_posts
