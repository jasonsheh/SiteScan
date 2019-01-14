#!/usr/bin/python
# __author__ = 'JasonSheh'
# __email__ = 'qq3039344@gmail.com'
# -*- coding:utf-8 -*-


import datetime
from sqlalchemy import create_engine, func
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from setting import user_path, item_size

Base = declarative_base()


class Range(Base):
    __tablename__ = "range"

    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer)
    domain = Column(String(255))
    sign = Column(String(255))
    scan_time = Column(Text)

    def format(self):
        return {
            "id": self.id,
            "domain_id": self.domain_id,
            "domain": self.domain,
            "sign": self.sign,
            "scan_time": self.scan_time
        }


class Leak(Base):
    """
    type default -1 未知/unknown
    type 0 忽略/无危害
    type 1 确认/相关
    type 2 确认/不相关
    type 3 确认/程序判断
    """
    __tablename__ = "leak"

    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer)
    domain = Column(String(255))
    repository_name = Column(String(255))
    repository_url = Column(String(255))
    code = Column(Text)
    scan_time = Column(Text)
    update_time = Column(Text)
    type = Column(Integer)
    confidence = Column(Integer)

    def format(self):
        return {
            "id": self.id,
            "domain_id": self.domain_id,
            "domain": self.domain,
            "repository_name": self.repository_name,
            "repository_url": self.repository_url,
            "code": self.code,
            "scan_time": self.scan_time,
            "update_time": self.update_time,
            "type": self.type,
            "confidence": self.confidence,
        }


class Rule(Base):
    __tablename__ = "rule"

    id = Column(Integer, primary_key=True)
    keyword = Column(String(255))
    pattern = Column(String(255))

    def format(self):
        return {
            "id": self.id,
            "keyword": self.keyword,
            "pattern": self.pattern,
        }


class GitLeak:
    def __init__(self):
        # 增加setting文件中，数据库类型的选择
        self.engine = create_engine(
            "sqlite:///{user_path}/db/GitLeak.db?check_same_thread=False".format(user_path=user_path))
        # self.conn = sqlite3.connect(user_path + '/db/GitLeak.db', check_same_thread=False)
        self.session = sessionmaker(bind=self.engine)()

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
        i = 0
        for src_info in src_list:
            i += 1
            self.session.add(Range(domain_id=i, domain=src_info[2][2:], sign="",
                                   scan_time=datetime.datetime.now().strftime("%Y-%m-%d")))
        self.session.commit()
        print("init range successfully")

    def create_database(self):
        Base.metadata.create_all(self.engine)

    def select_range(self, page=0, count=0):
        results = []
        if count != 0:
            results = self.session.query(Range).order_by(Range.scan_time).limit(count).all()
        if page != 0:
            results = self.session.query(Range).order_by(Range.scan_time.desc()).limit(item_size).offset(
                (page - 1) * item_size).all()
        if page == 0 and count == 0:
            results = self.session.query(Range).order_by(Range.scan_time.desc()).all()

        results_list = []
        for result in results:
            results_list.append(result.format())
        return results_list

    def select_rules(self, page=0):
        if page != 0:
            results = self.session.query(Rule).limit(item_size).offset((page - 1) * item_size).all()
        else:
            results = self.session.query(Rule).all()

        results_list = []
        # result Rule
        for result in results:
            results_list.append(result.format())
        return results_list

    def select_leak(self, page=0, repository_name="", domain=""):
        if page != 0:
            results = self.session.query(Leak).filter(Leak.type != 0).order_by(Leak.scan_time.desc()).order_by(Leak.id.desc()).limit(
                item_size).offset((page - 1) * item_size).all()
        elif repository_name != "":
            results = self.session.query(Leak).filter_by(repository_name=repository_name).all()
        elif domain != "":
            results = self.session.query(Leak).filter_by(domain=domain).all()
        else:
            results = self.session.query(Leak).order_by(Leak.scan_time.desc()).all()

        results_list = []
        for result in results:
            r = result.format()
            r["code"] = r["code"].split("\n")
            r["file_name"] = r["repository_name"].rsplit("/")[-1]

            results_list.append(r)
        return results_list

    def update_scan_time(self, domain_id):
        _range = self.session.query(Range).filter_by(id=domain_id)
        _range.scan_time = datetime.datetime.now().strftime("%Y-%m-%d")
        self.session.commit()

    def update_range(self, id, domain):
        _range = self.session.query(Range).filter_by(id=id)
        _range.domain = domain
        self.session.commit()

    def update_rule(self, id, keyword, pattern):
        rule = self.session.query(Rule).filter_by(id=id)
        rule.keyword = keyword
        rule.pattern = pattern
        self.session.commit()

    def insert_leak(self, leak, domain_id):
        leak = Leak(domain_id=domain_id, domain=leak["domain"], repository_name=leak["repository_name"],
                    repository_url=leak["repository_url"], code="\n".join(leak["code"]), type=leak["type"],
                    scan_time=datetime.datetime.now().strftime("%Y-%m-%d"), update_time=leak["update_time"],
                    confidence=leak["confidence"])
        self.session.add(leak)
        self.session.commit()

    def insert_range(self, domain_id, domain):
        _range = Range(domain_id=domain_id, domain=domain, sign="",
                       scan_time=datetime.datetime.now().strftime("%Y-%m-%d"))
        self.session.add(_range)
        self.session.commit()

    def insert_rule(self, keyword, pattern):
        rule = Rule(keyword=keyword, pattern=pattern)
        self.session.add(rule)
        self.session.commit()

    def delete_leak(self):
        self.session.query(Leak).filter_by(type=0).delete()

    def delete(self, mode, id):
        del_mode = {
            "leak": Leak,
            "range": Range,
            "rule": Rule
        }
        self.session.query(del_mode[mode]).filter_by(id=id).delete()

    def count(self, mode, not_type=None):
        count_mode = {
            "leak": Leak,
            "range": Range,
            "rule": Rule
        }
        if not_type:
            total = self.session.query(func.count(Leak.id)).filter(Leak.type != not_type).scalar()
        else:
            total = self.session.query(func.count(count_mode[mode].id)).scalar()
        return total

    def update_type(self, leak_id, leak_type):
        self.session.query(Leak).filter_by(id=leak_id).update({"type": leak_type})

    def clean(self):
        self.session.close()


if __name__ == '__main__':
    GitLeak().create_database()
