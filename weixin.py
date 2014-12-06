#-*-coding:utf-8-*-

from flask import Flask
from flask_weixin import Weixin

from beijing_bus import BeijingBus


app = Flask(__name__)
app.config.from_object('config')

weixin = Weixin(app)

app.add_url_rule('/', view_func=weixin.view_func)


@weixin.register('*')
def query(**kwargs):
    username = kwargs.get('sender')
    sender = kwargs.get('receiver')
    content = kwargs.get('content')
    if content:
        data = BeijingBus.extract_line_and_stations(content)
        if data:
            reply = get_realtime_message(data['line'], 
                                         data['from_station'],
                                         data['to_station'])
            if not reply:
                reply = '目前还没有车要来呢'
        else:
            reply = '没有结果，可能还不支持这条线路呢'
    else:
        reply = '我好笨笨哦，还不懂你在说什么。\n查询示例： 847从西坝河到将台路口西'
        
    return weixin.reply(
        username, sender=sender, content=reply
    )


def get_realtime_message(line, from_station, to_station):
    realtime_data = line.get_realtime_data(from_station)
    realtime_data = filter(lambda d: d['station_arriving_time'], realtime_data)
    realtime_data.sort(key=lambda d: d['station_arriving_time'])
    if not realtime_data:
        return ''

    reply = '查询: %s  %s -> %s\n\n' % (line.short_name, from_station.name, to_station.name)
    for i, data in enumerate(realtime_data):
        reply += '车辆%s：' % (i+1)
        reply += '距离%s还有 %s米，' % (from_station.name, data['station_distance'])
        reply += '预计%s到达\n\n' % data['station_arriving_time'].strftime('%H:%M')
    return reply


if __name__ == '__main__':
    app.run(debug=True)