from django.conf.urls import url
from apps.competition.views.competition import competition_create, competition_list_admin, \
    competition_delete, competition_detail, competition_update, competition_list_submission
from apps.competition.views.participants import participant_list, participant_delete, \
    participant_create, participant_update, tmp, get_participants_csv
from apps.competition.views.room import room_list, room_delete, room_create, room_update


urlpatterns = [
    # 参赛者相关接口
    url(r'(?P<cid>[0-9]{1,})/participants-list', participant_list, name='participant_list'), # 列出所有参赛者
    url(r'(?P<cid>[0-9]{1,})/participants-create', participant_create, name='participant_create'), # 创建参赛者
    url(r'(?P<cid>[0-9]{1,})/participant-(?P<pid>[0-9]{1,})-delete', participant_delete, name='participant_delete'), # 删除参赛者
    url(r'(?P<cid>[0-9]{1,})/participant-(?P<pid>[0-9]{1,})-update', participant_update, name='participant_update'), # 更新参赛者
    url(r'(?P<cid>[0-9]{1,})/participants-csv', get_participants_csv, name='get_participants_csv'), # 下载参赛者名单csv
    # url(r'tmp', tmp, name='tmp'),

    # 考场相关接口
    url(r'room-list', room_list, name='room_list'), # 列出所有考场
    url(r'room-(?P<rid>[0-9]{1,})-delete', room_delete, name='room_delete'), # 删除考场信息
    url(r'room-(?P<rid>[0-9]{1,})-update', room_update, name='room_update'), # 更新考场信息
    url(r'room-create', room_create, name='room_create'), # 创建考场信息

    # 赛事相关接口
    url(r'create', competition_create, name='competition_create'), # 创建比赛
    url(r'list-admin', competition_list_admin), # 列出所有比赛供维护
    url(r'list-submission', competition_list_submission, name='competition_list_submission'), # 列出所有比赛供选择查看提交情况
    url(r'(?P<cid>[0-9]{1,})/delete', competition_delete, name='competition_delete'), # 删除比赛
    url(r'(?P<cid>[0-9]{1,})/detail', competition_detail, name='competition_detail'), # 某个比赛的提交详情
    url(r'(?P<cid>[0-9]{1,})/update', competition_update, name='competition_update'), # 更新某个比赛信息
]
