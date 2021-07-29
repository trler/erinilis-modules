import datetime
from hoshino import Service, priv, MessageSegment
from ..util import filter_list, get_next_day
from .utils.gacha_info import gacha_info_list, gacha_info
from .modules.wish import wish, gacha_type_by_name
from .modules.wish_ui import wish_ui

sv_help = '''
[原神十连] 一次10连抽卡
[原神一单] 50连抽卡
'''.strip()

sv = Service(
    name='原神抽卡',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.ADMIN,  # 管理权限
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    # bundle = '娱乐', #分组归类
    help_=sv_help  # 帮助说明
)

gacha_info_data = {
    'runtime': get_next_day()
}


# @sv.on_prefix('原神单抽')
# async def gacha(bot, ev):
#     await check_gacha_data(ev.group_id)
#     wish_info = wish(ev.user_id, gacha_info_data[ev.group_id]['type'], gacha_info_data[ev.group_id]['data']).once()
#     await bot.send(ev, wish_info.data.item_name)


@sv.on_prefix('原神十连')
async def gacha(bot, ev):
    await check_gacha_data(ev.group_id)
    wish_info = wish(ev.user_id, gacha_info_data[ev.group_id]['type'], gacha_info_data[ev.group_id]['data']).ten()
    img = wish_ui.ten_b64_img(wish_info)

    await bot.send(ev, MessageSegment.image(img), at_sender=True)

    # msg = '\n'.join([x.data.item_name for x in wish_info])
    # msg += '\n\n已经%s发没出5星了' % (wish_info[len(wish_info) - 1].count_5 - 1)
    # await bot.send(ev, msg)


@sv.on_prefix('原神一单')
async def gacha(bot, ev):
    await check_gacha_data(ev.group_id)
    x5 = []
    for i in range(0, 5):
        x5.append(wish(ev.user_id, gacha_info_data[ev.group_id]['type'], gacha_info_data[ev.group_id]['data']).ten())
    img = wish_ui.ten_b64_img_xn(x5)
    await bot.send(ev, MessageSegment.image(img), at_sender=True)


@sv.on_prefix('原神切换卡池')
async def gacha(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        return
    msg = ev.message.extract_plain_text().strip()
    gacha_type = gacha_type_by_name(msg)
    if not gacha_type:
        await bot.finish(ev, '不存在此卡池: %s' % msg)
    await switch_gacha(ev.group_id, gacha_type)
    await bot.send(ev, '切换为[%s]卡池' % gacha_info_data[ev.group_id]['name'])


async def check_gacha_data(group_id):
    if not gacha_info_data.get(group_id):
        return await switch_gacha(group_id, 301)

    now = datetime.datetime.now().timestamp()
    if now > gacha_info_data['runtime']:
        return await switch_gacha(group_id, 301)


async def switch_gacha(group_id, gacha_type):
    data = await gacha_info_list()
    gacha_data = filter_list(data, lambda x: x.gacha_type == gacha_type)[0]
    gacha_info_data[group_id] = {}
    gacha_info_data[group_id]['id'] = gacha_data.gacha_id
    gacha_info_data[group_id]['name'] = gacha_data.gacha_name
    gacha_info_data[group_id]['type'] = gacha_data.gacha_type
    gacha_info_data[group_id]['data'] = await gacha_info(gacha_data.gacha_id)
