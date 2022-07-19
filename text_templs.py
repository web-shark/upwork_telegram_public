btn_back = 'Back'


btn_start_1 = '📒Jobs parsing on/off'
btn_start_2 = '📑List rss'
btn_start_3 = '⚙️Settings'
btn_start_4 = '📲Help'

templ_start = ('Hey there! It is a telegram upwork scapper\n'
               'This bot can parse jobs from rss feeds from Upwork and send new jobs fastly for you\n'
               '[Where can I find code?](https://github.com/web-shark/upwork_telegram)')
templ_main = ('📒Jobs parsing - $working\n'
              '📑List rss - show rss feed parsed\n'
              '🛠Settings - timezone and time update feed\n'
              '📲Help - help info what do this')

templ_menu = '📝Edit feeds menu'
templ_list_rss = '\n📑Working rss:'
templ_filters = ('\n🧹Filters:'
                 '\n🇷🇼Exclude countries: $exclude_countries'
                 '\n🦾Skills: $add_skills')
templ_list_rss_link = "\n🔎[$link_title]($link)"
templ_list_rss_no = '\nNo rss avanble, add links to scrap\!'
btn_rsslist_1 = '📝Add new rss'
btn_rsslist_2 = '📝Edit filters'
btn_rsslist_3 = '🗑Delete rss'

templ_list_rssadd = ('Write rss name and link for upwork'
                     '\nex:add Linkname https://www.upwork.com/ab/feed/topics/rss?')
templ_list_rssadd_good = '✅Feed add succsesfully!'
templ_list_rssadd_bad_link = '❌Bad link, try againg.'
templ_list_rssadd_bad_command = '❌Bad link. Try again.'+templ_list_rssadd

templ_list_rssdelete = ('Write name of link to delete'
                        '\nex:del LinkName')
templ_list_rssdelete_good = '✅Feed delete succsesfully!'
templ_list_rssdelete_bad = "❌Bad feed name."
templ_list_rss_edit = ('Choise filters and write string of filters(use space as in ex)'
                         '\nAvailable filters: exclude_countries, add_skills'
                         '\nEx:filter exclude_countries India,China')
btn_list_rss_edit_1 = 'Countries'
btn_list_rss_edit_2 = 'Skills'

templ_list_rss_edit_rss_info = 'RSS link, how to add here, write true link'
templ_list_rss_edit_rss_good = '✅RSS change_succsesfully'
templ_list_rss_edit_filter = 'Write  $filter, in coma, ALL filters will be changed'
templ_setting = ('⚙️Setting menu:'
                 '\nℹ️Show summary: $show_summary'
                 '\n💬Chat id to send: $chat_id')
btn_setting_1 = 'ℹ️Show/hide summary'
btn_setting_2 = '💬Chat to send jobs'
templ_send_chat = ('Chat id to send jobs, usefull for teams'
                   '\n ex:chat -1412365234')
templ_help = ('ℹ️[How to find rss link?](https://telegra.ph/How-to-find-rss-link-07-19)'
              '\n💻[Where can I find code?](https://github.com/web-shark/upwork_telegram_public)'
              '\n💸[Send money on cap of coffee.](https://www.buymeacoffee.com/serhiibliakhars)'
              '\n📲[Find error or need telegram bot? Write me.](https://t.me/sergey_bliacharskiy)')

text_command_1 = 'add'
text_command_2 = 'del'
text_command_3 = 'filter'
text_command_4 = 'chat'

templ_send_chat_good = '✅Chat changed successfully!'

error_notype = '❌Bad command('
test_type = '✅good command)'
error_bad_filter = '❌Sorry, bad filter, try again.'
templ_add_filter = "✅Successfully set filter $keyword = $value"
ALLOWED_FILTERS = [
    "exclude_countries",
    "add_skills"
]

ALLOWED_SETTINGS = {
    "timezone": {
        "type": int,
        "error": "Allowed chat id only int, get chat id: https://t.me/getmyid_bot"
    },
    "show_summary": {
        "type": str,
        "error": "Allowed show_summary values are yes/no."
    }
}