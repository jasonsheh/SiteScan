#!/usr/bin/python
# __author__ = 'JasonSheh'
# __email__ = 'qq3039344@gmail.com'
# -*- coding:utf-8 -*-


import sqlite3
import datetime
from setting import user_path, item_size


class GitLeak:
    def __init__(self):
        self.conn = sqlite3.connect(user_path + '/db/GitLeak.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_range(self):
        self.cursor.execute(
            'create table range ('
            'id integer primary key,'
            'domain_id integer, '
            'domain varchar(255), '
            'sign varchar(255), '
            'scan_time text'
            ')')
        print("create range successfully")

    def create_leak(self):
        """
        type default -1 未知/unknown
        type 0 忽略/无危害
        type 1 确认/相关
        type 2 确认/不相关
        :return:
        """
        self.cursor.execute(
            'create table leak ('
            'id integer primary key,'
            'domain_id integer, '
            'domain varchar(255), '
            'repository_name varchar(255), '
            'repository_url varchar(255), '
            'code text, '
            'scan_time text, '
            'type integer, '
            'update_time text'
            ')')

        print("create leak successfully")

    def create_rule(self):
        self.cursor.execute(
            'create table rule ('
            'id integer primary key,'
            'keyword varchar(255), '
            'pattern varchar(255)'
            ')')
        print("create rule successfully")

    def init_range(self):
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
        sql = "insert into range (domain_id, domain, sign, scan_time) values (?, ?, ?, ?)"
        i = 0
        for src_info in src_list:
            i += 1
            self.cursor.execute(sql,
                                (i, src_info[2][2:], "", datetime.datetime.now().strftime("%Y-%m-%d")))
        self.conn.commit()
        print("init range successfully")

    def create_database(self):
        self.create_range()
        self.create_leak()
        self.init_range()

    def select_range(self, page=0, count=0):
        if count != 0:
            sql = "select * from range order by scan_time asc limit ?"
            self.cursor.execute(sql, (count,))
        if page != 0:
            sql = "select * from range order by scan_time desc limit ?,?"
            self.cursor.execute(sql, ((page - 1) * item_size, item_size))
        if page == 0 and count == 0:
            sql = "select * from range order by scan_time desc"
            self.cursor.execute(sql)
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'domain_id': result[1],
                    'domain': result[2],
                    'sign': result[3],
                    'scan_time': result[4]
                }
            )
        return results_list

    def select_rules(self, page=0):
        if page != 0:
            sql = "select * from rule limit ?,?"
            self.cursor.execute(sql, ((page - 1) * item_size, item_size))
        else:
            sql = "select * from rule"
            self.cursor.execute(sql)
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'keyword': result[1],
                    'pattern': result[2],
                }
            )
        return results_list

    def select_leak(self, page=0, domain_id=-1):
        if page != 0:
            sql = "select * from leak where type != 0 order by scan_time desc, id desc limit ?,?"
            self.cursor.execute(sql, ((page - 1) * item_size, item_size))
        elif domain_id != -1:
            sql = "select * from leak where domain_id = ?"
            self.cursor.execute(sql, (domain_id,))
        else:
            sql = "select * from leak order by scan_time desc"
            self.cursor.execute(sql)
        results = self.cursor.fetchall()

        results_list = []
        for result in results:
            results_list.append(
                {
                    'id': result[0],
                    'domain_id': result[1],
                    'domain': result[2],
                    'repository_name': result[3],
                    'repository_url': result[4],
                    'code': result[5].split("\n"),
                    'scan_time': result[6],
                    'type': result[7],
                    'update_time': result[8],
                    'file_name': result[4].rsplit("/")[-1],
                }
            )
        return results_list

    def update_scan_time(self, domain_id):
        sql = "update range set scan_time = ? where id = ?"
        self.cursor.execute(sql, (datetime.datetime.now().strftime("%Y-%m-%d"), domain_id))
        self.conn.commit()

    def update_range(self, id, domain):
        sql = "update range set domain = ? where id = ?"
        self.cursor.execute(sql, (domain, id))
        self.conn.commit()

    def update_rule(self, id, keyword, rule):
        sql = "update rule set keyword = ? , rule = ? where id = ?"
        self.cursor.execute(sql, (keyword, rule, id))
        self.conn.commit()

    def insert_leak(self, leak, domain_id, leak_type):
        sql = "insert into leak (domain_id, domain, repository_name, repository_url, code, scan_time, type, " \
              "update_time) values (?, ?, ?, ?, ?, ?, ?, ?)"
        self.cursor.execute(sql,
                            (domain_id, leak["domain"], leak["repository_name"], leak["repository_url"],
                             "\n".join(leak["code"]), datetime.datetime.now().strftime("%Y-%m-%d"),
                             leak_type, leak["update_time"]))
        self.conn.commit()

    def insert_range(self, domain_id, domain):
        sql = "insert into range (domain_id, domain, sign, scan_time) values (?, ?, ?, ?)"
        self.cursor.execute(sql, (domain_id, domain, "", datetime.datetime.now().strftime("%Y-%m-%d")))
        self.conn.commit()

    def insert_rule(self, keyword, pattern):
        sql = "insert into rule (keyword, pattern) values (?, ?)"
        self.cursor.execute(sql, (keyword, pattern))
        self.conn.commit()

    def delete_leak(self):
        sql = "delete from leak where type = 0"
        self.cursor.execute(sql)
        self.conn.commit()

    def delete(self, mode, id):
        sql = "delete from %s where id = ?".format(mode)
        self.cursor.execute(sql, (id, ))
        self.conn.commit()

    def count(self, mode, not_type=None):
        if not_type:
            self.cursor.execute('select count(*) from {} where type != ?'.format(mode), (not_type,))
        else:
            self.cursor.execute('select count(*) from {}'.format(mode))
        total = self.cursor.fetchone()
        return total[0]

    def update_type(self, leak_id, leak_type):
        sql = "update leak set type = ? where id = ?"
        self.cursor.execute(sql, (leak_type, leak_id))
        self.conn.commit()

    def clean(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    g = GitLeak()
    leak = g.select_rules()
    g.clean()

    print(leak)
