#!/usr/bin/python
# __author__ = 'JasonSheh'
# __email__ = 'qq3039344@gmail.com'
# -*- coding:utf-8 -*-

import sqlite3
import datetime
from setting import user_path, item_size, sudomain_scan_size


class SrcList:
    def __init__(self):
        self.conn = sqlite3.connect(user_path + '/db/SiteScan.db')
        self.cursor = self.conn.cursor()

    # 创建src列表数据库
    def create_src_list(self):
        self.cursor.execute('create table src('
                            'id integer primary key,'
                            'name varchar(64),'
                            'src_id integer,'
                            'url varchar(128),'
                            'scan_time TEXT'
                            ')')
        self.conn.commit()
        self.clean()

    def init_data(self):
        src_list = [("阿里asrc", 1, "*.taobao.com"),
                    ("阿里asrc", 1, "*.tmall.com"),
                    ("阿里asrc", 1, "*.alipay.com"),
                    ("阿里asrc", 1, "*.etao.com"),
                    ("阿里asrc", 1, "*.aliexpress.com"),
                    ("阿里asrc", 1, "*.alibaba.com"),
                    ("阿里asrc", 1, "*.laiwang.com"),
                    ("阿里asrc", 1, "*.1688.com"),
                    ("阿里asrc", 1, "*.alimama.com"),
                    ("阿里asrc", 1, "*.aliyun.com"),
                    ("阿里asrc", 1, "*.dingtalk.com"),
                    ("阿里asrc", 1, "*.Yunos.com"),
                    ("阿里asrc", 1, "*.aliresearch.com"),
                    ("阿里asrc", 1, "*.alijijinhui.org"),
                    ("阿里asrc", 1, "*.amap.com"),
                    ("阿里asrc", 1, "*.uc.cn"),
                    ("阿里asrc", 1, "*.xiami.com"),
                    ("阿里asrc", 1, "*.cnzz.com"),
                    ("阿里asrc", 1, "*.taoban.com"),
                    ("百度bsrc", 2, "*.baidu.com"),
                    ("百度bsrc", 2, "*.hao123.com"),
                    ("顺丰sfsrc", 3, "*.sf-express.com"),
                    ("蚂蚁金服afsrc", 4, "*.alipay.com"),
                    ("蚂蚁金服afsrc", 4, "*.xin.xin"),
                    ("蚂蚁金服afsrc", 4, "*.antfortune.com"),
                    ("蚂蚁金服afsrc", 4, "*.mybank.cn"),
                    ("腾讯tsrc", 5, "*.qq.com"),
                    ("腾讯tsrc", 5, "*.tencent.com"),
                    ("腾讯tsrc", 5, "*.tenpay.com"),
                    ("360src", 6, "*.360.cn"),
                    ("京东jsrc", 7, "*.jd.com"),
                    ("京东jsrc", 7, "*.jd.hk"),
                    ("京东jsrc", 7, "*.jcloud.com"),
                    ("京东jsrc", 7, "*.yhd.com"),
                    ("京东jsrc", 7, "*.yihaodian.com"),
                    ("京东jsrc", 7, "*.1mall.com"),
                    ("京东jsrc", 7, "*.jdwl.com"),
                    ("京东jsrc", 7, "*.joybuy.com"),
                    ("京东jsrc", 7, "*.jd.ru"),
                    ("京东jsrc", 7, "*.jd.co.th"),
                    ("京东jsrc", 7, "*.jd.id"),
                    ("京东jsrc", 7, "*.healthjd.com"),
                    ("京东jsrc", 7, "*.yiyaojd.com"),
                    ("京东jsrc", 7, "*.7fresh.com"),
                    ("京东jsrc", 7, "*.jr.jd.com"),
                    ("京东jsrc", 7, "*.baitiao.com"),
                    ("京东jsrc", 7, "*.jdpay.com"),
                    ("京东jsrc", 7, "*.chinabank.com.cn"),
                    ("京东jsrc", 7, "*.wangyin.com"),
                    ("京东jsrc", 7, "*.jdcloud.com"),
                    ("菜鸟cnsrc", 8, "*.cainiao.com"),
                    ("平安psrc", 9, "*.pingan.com"),
                    ("平安psrc", 9, "*.pingan.cn"),
                    ("平安psrc", 9, "*.orangebank.com.cn"),
                    ("平安psrc", 9, "*.1qianbao.com"),
                    ("平安psrc", 9, "*.pinganfang.com"),
                    ("平安psrc", 9, "*.jk.cn"),
                    ("平安psrc", 9, "*.pinganwj.com"),
                    ("平安psrc", 9, "*.zhong.com"),
                    ("平安psrc", 9, "*.10100000.com"),
                    ("平安psrc", 9, "*.lu.com"),
                    ("网易nsrc", 10, "*.163.com"),
                    ("网易nsrc", 10, "*.126.com"),
                    ("网易nsrc", 10, "*.yeah.net"),
                    ("网易nsrc", 10, "*.188.com"),
                    ("网易nsrc", 10, "*.you.163.com"),
                    ("网易nsrc", 10, "*.kaola.com"),
                    ("网易nsrc", 10, "*.youdao.com"),
                    ("网易nsrc", 10, "*.netease.com"),
                    ("携程csrc", 11, "*.ctrip.com"),
                    ("携程csrc", 11, "*.suanya.cn"),
                    ("携程csrc", 11, "*.tieyou.com"),
                    ("携程csrc", 11, "*.hhtravel.com"),
                    ("携程csrc", 11, "*.elong.com"),
                    ("携程csrc", 11, "*.qunar.com"),
                    ("携程csrc", 11, "*.jointwisdom.cn"),
                    ("网信集团ncfsrc", 12, "*.firstp2p.cn"),
                    ("网信集团ncfsrc", 12, "*.wangxinlicai.com"),
                    ("网信集团ncfsrc", 12, "*.ncfwx.com"),
                    ("网信集团ncfsrc", 12, "*.ncfgroup.com"),
                    ("网信集团ncfsrc", 12, "*.ucfpay.com"),
                    ("网信集团ncfsrc", 12, "*.unitedmoney.com"),
                    ("网信集团ncfsrc", 12, "*.9888keji.com"),
                    ("网信集团ncfsrc", 12, "*.gongchangzx.com"),
                    ("网信集团ncfsrc", 12, "*.gongchangp2p.cn"),
                    ("网信集团ncfsrc", 12, "*.dougemall.com"),
                    ("网信集团ncfsrc", 12, "*.9888.cn"),
                    ("网信集团ncfsrc", 12, "*.ucfgroup.com"),
                    ("竞技世界jjsrc", 13, "*.jj.cn"),
                    ("滴滴dsrc", 14, "*.didiglobal.com"),
                    ("滴滴dsrc", 14, "*.didichuxing.com"),
                    ("同程ysrc", 15, "*.ly.com"),
                    ("苏宁snsrc", 16, "*.suning.com"),
                    ("苏宁snsrc", 16, "*.suningcloud.com"),
                    ("苏宁snsrc", 16, "*.redbaby.com.cn"),
                    ("苏宁snsrc", 16, "*.suningholdings.com"),
                    ("新浪ssrc", 17, "*.sina.com.cn"),
                    ("新浪ssrc", 17, "*.sina.cn"),
                    ("新浪ssrc", 17, "*.leju.com"),
                    ("新浪ssrc", 17, "*.vip9999.com"),
                    ("新浪ssrc", 17, "*.weibopay.com"),
                    ("新浪ssrc", 17, "*.17g.com"),
                    ("新浪ssrc", 17, "*.aicai.com"),
                    ("新浪ssrc", 17, "*.weimi.me"),
                    ("新浪ssrc", 17, "*.sinafenqi.com"),
                    ("搜狗sgsrc", 18, "*.sogou.com"),
                    ("欢聚时代(yy语音)ysrc", 19, "*.yy.com"),
                    ("去哪儿qsrc", 20, "*.qunar.com"),
                    ("猪八戒zsrc", 21, "*.zbj.com"),
                    ("猪八戒zsrc", 21, "*.tianpeng.com"),
                    ("猪八戒zsrc", 21, "*.kubanquan.com"),
                    ("斗鱼dysrc", 22, "*.douyu.com"),
                    ("陌陌mmsrc", 23, "*.immomo.com"),
                    ("陌陌mmsrc", 23, "*.igamesofficial.com"),
                    ("陌陌mmsrc", 23, "*.momogamechengdu.com"),
                    ("陌陌mmsrc", 23, "*.wemomo.com"),
                    ("陌陌mmsrc", 23, "*.immomogame.com"),
                    ("挖财wacsrc", 24, "*.wacai.com"),
                    ("挖财wacsrc", 24, "*.caimitech.com"),
                    ("挖财wacsrc", 24, "*.weijizhang.com"),
                    ("挖财wacsrc", 24, "*.qufaya.com"),
                    ("挖财wacsrc", 24, "*.caiwuapp.com"),
                    ("挖财wacsrc", 24, "*.wacaijijin.com"),
                    ("58src", 25, "*.58.com"),
                    ("58src", 25, "*.ganji.com"),
                    ("58src", 25, "*.anjuke.com"),
                    ("58src", 25, "*.jxedt.com"),
                    ("58src", 25, "*.chinahr.com"),
                    ("58src", 25, "*.zhuanzhuan.com"),
                    ("宜人贷yisrc", 26, "*.yirendai.com"),
                    ("小米misrc", 27, "*.mi.com"),
                    ("小米misrc", 27, "*.miui.com"),
                    ("小米misrc", 27, "*.xiaomi.com"),
                    ("小米misrc", 27, "*.duokan.com"),
                    ("小米misrc", 27, "*.miwifi.com"),
                    ("饿了么esrc", 28, "*.ele.me"),
                    ("美丽联合(蘑菇街)mlsrc", 29, "*.mogujie.com"),
                    ("美丽联合(蘑菇街)mlsrc", 29, "*.meilishuo.com"),
                    ("美丽联合(蘑菇街)mlsrc", 29, "*.uniny.com"),
                    ("美丽联合(蘑菇街)mlsrc", 29, "*.xiaodian.com"),
                    ("美丽联合(蘑菇街)mlsrc", 29, "*.weshop.com"),
                    ("唯品会vsrc", 30, "*.vip.com"),
                    ("唯品会vsrc", 30, "*.huahaicang.cn"),
                    ("唯品会vsrc", 30, "*.vipshop.com"),
                    ("唯品会vsrc", 30, "*.lefeng.com"),
                    ("唯品会vsrc", 30, "*.pjbest.com"),
                    ("唯品会vsrc", 30, "*.ebatong.com"),
                    ("点融dsrc", 31, "*.dianrong.com"),
                    ("vipkid vksrc", 32, "*.vipkid.com.cn"),
                    ("爱奇艺71src", 33, "*.iqiyi.com"),
                    ("爱奇艺71src", 33, "*.qiyi.com"),
                    ("爱奇艺71src", 33, "*.pps.tv"),
                    ("爱奇艺71src", 33, "*.ppstream.com"),
                    ("bilibili bilisrc", 34, "*.bilibili.com"),
                    ("bilibili bilisrc", 34, "*.biligame.com"),
                    ("bilibili bilisrc", 34, "*.bilibiligame.net"),
                    ("bilibili bilisrc", 34, "*.acg.tv"),
                    ("bilibili bilisrc", 34, "*.hdslb.net"),
                    ("东方财富emsrc", 35, "*.eastmoney.com"),
                    ("东方财富emsrc", 35, "*.langke.com"),
                    ("富友fsrc", 36, "*.fuiou.com"),
                    ("好未来src", 37, "*.100tal.com"),
                    ("好未来src", 37, "*.speiyou.com"),
                    ("好未来src", 37, "*.xueersi.com"),
                    ("好未来src", 37, "*.haibian.com"),
                    ("好未来src", 37, "*.weclassroom.com"),
                    ("好未来src", 37, "*.izhikang.com"),
                    ("好未来src", 37, "*.jiajiaoban.com"),
                    ("好未来src", 37, "*.jzb.com"),
                    ("好未来src", 37, "*.kaoyan.com"),
                    ("好未来src", 37, "*.bangxuetang.com"),
                    ("好未来src", 37, "*.muchong.com"),
                    ("好未来src", 37, "*.aoshu.com"),
                    ("好未来src", 37, "*.gaokao.com"),
                    ("好未来src", 37, "*.gaokaopai.com"),
                    ("好未来src", 37, "*.zuowen.com"),
                    ("好未来src", 37, "*.zhongkao.com"),
                    ("好未来src", 37, "*.mobby.cn"),
                    ("好未来src", 37, "*.yingyu.com"),
                    ("好未来src", 37, "*.lejiale.com"),
                    ("好未来src", 37, "*.lewaijiao.com"),
                    ("好未来src", 37, "*.firstleap.cn"),
                    ("好未来src", 37, "*.kmf.com"),
                    ("好未来src", 37, "*.shunshunliuxue.com"),
                    ("好未来src", 37, "*.youjiao.com"),
                    ("好未来src", 37, "*.yuer.com"),
                    ("好未来src", 37, "*.xiwang.com"),
                    ("焦点fsrc", 38, "*.made-in-china.com"),
                    ("焦点fsrc", 38, "*.crov.com"),
                    ("焦点fsrc", 38, "*.xyz.cn"),
                    ("焦点fsrc", 38, "*.91xinbei.cn"),
                    ("焦点fsrc", 38, "*.abiz.com"),
                    ("焦点fsrc", 38, "*.ttnet.net"),
                    ("焦点fsrc", 38, "*.jiankang51.cn"),
                    ("焦点fsrc", 38, "*.jdsxy.com"),
                    ("焦点fsrc", 38, "*.trademessenger.com"),
                    ("焦点fsrc", 38, "*.ipincai.com"),
                    ("焦点fsrc", 38, "*.leadong.com"),
                    ("魅族sec", 39, "*.meizu.com"),
                    ("千米src", 40, "*.qianmi.com"),
                    ("千米src", 40, "*.1000.com"),
                    ("途牛tnsrc", 41, "*.tuniu.com"),
                    ("完美世界pwsrc", 42, "*.wanmei.com"),
                    ("完美世界pwsrc", 42, "*.laohu.com"),
                    ("完美世界pwsrc", 42, "*.csgo.com.cn"),
                    ("完美世界pwsrc", 42, "*.dota2.com.cn"),
                    ("新浪微博wsrc", 43, "*.weibo.com"),
                    ("新浪微博wsrc", 43, "*.weibo.cn"),
                    ("微众wsrc", 44, "*.webank.com"),
                    ("万能钥匙wifisrc", 45, "*.wifi.com"),
                    ("中通src", 46, "*.zto.com")]
        sql = "insert into src (name, src_id, url, scan_time) values (?, ?, ?, ?)"
        for src_info in src_list:
            self.cursor.execute(sql,
                                (src_info[0], src_info[1], src_info[2], datetime.datetime.now().strftime("%Y-%m-%d")))
        self.conn.commit()
        self.clean()
        print("create src successfully")

    def update_scan_time(self, url):
        sql = "update src set scan_time = ? where url = ?"
        self.cursor.execute(sql, (datetime.datetime.now().strftime("%Y-%m-%d"), url))
        self.conn.commit()

    def insert_src_list(self, name, src_id, url):
        sql = "insert into src (name, src_id, url, scan_time) values (?, ?, ?, ?)"
        self.cursor.execute(sql, (name, src_id, url, datetime.datetime.now().strftime("%Y-%m-%d")))
        self.conn.commit()

    def select_src_list(self, page):
        sql = "select * from src order by id desc limit ?,?"
        self.cursor.execute(sql, ((page - 1) * item_size, item_size))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'name': result[1],
                    'src_id': result[2],
                    'url': result[3],
                    'scan_time': result[4]
                }
            )

        self.clean()
        return results_list

    def select_un_scan_src_list(self):
        sql = "select * from src order by scan_time desc limit ?"
        self.cursor.execute(sql, (sudomain_scan_size, ))
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'name': result[1],
                    'src_id': result[2],
                    'url': result[3],
                    'scan_time': result[4]
                }
            )

        self.clean()
        return results_list

    def count(self):
        self.cursor.execute('select count(*) from src')
        total = self.cursor.fetchone()
        return total[0]

    def delete(self, id):
        self.cursor.execute('delete from src where id = ?', (id,))
        self.conn.commit()
        self.clean()

    def clean(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    print(SrcList().select_un_scan_src_list())
