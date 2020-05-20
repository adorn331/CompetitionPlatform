from django.conf.urls import url
from apps.statistics.views import list_statistics, attendance_statistics, completion_statistics,\
    get_attended_participant_csv, get_unattended_participant_csv, get_compeltion_csv, summary_graph


urlpatterns = [
    url(r'list-statistics', list_statistics, name='list_statistics'), # 列出所有比赛，供选择查看统计详情
    url(r'(?P<cid>[0-9]{1,})/summary_graph', summary_graph, name='summary_graph'),  # 总览图
    url(r'(?P<cid>[0-9]{1,})/attendance-statistics', attendance_statistics, name='attendance_statistics'), # 出席状况统计
    url(r'(?P<cid>[0-9]{1,})/completion-statistics', completion_statistics, name='completion_statistics'), # 完成度统计
    url(r'(?P<cid>[0-9]{1,})/attended-participant-csv', get_attended_participant_csv, name='get_attended_participant_csv'), # 下载已出席选手csv名单
    url(r'(?P<cid>[0-9]{1,})/unattended-participant-csv', get_unattended_participant_csv, name='get_unattended_participant_csv'), # 下载缺席csv名单
    url(r'(?P<cid>[0-9]{1,})/compeltion-csv', get_compeltion_csv, name='get_compeltion_csv'), # 下载完成度统计csv
]
