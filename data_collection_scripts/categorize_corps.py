
import codecs
import re



sectors = ["edu", "gov", "finance", "media", "travel",
           "entertainment", "health", "food", "trans", "comm",
           "manufactoring", "energy", "email", "mobile", "gaming",
           "social", "video", "security", "hr", "cms", "portal",
           "forum", "ecommerce", "browser", "office", "information"]
           
sector_full = {"edu":"Education", "gov":"Government", "finance":"Finance",
               "media":"Media", "travel":"Travel & Hotel",
               "entertainment":"Entertainment", "health":"Healthcare",
               "food":"Food & Drink", "trans":"Transportation",
               "comm":"Telecomm.", "manufactoring":"Manufactoring",
               "energy":"Energy & Utilities", "email":"Email",
               "mobile":"Mobile", "gaming":"Gaming", "social":"Social Networks",
               "video":"Video & Photo", "security":"Security", "cms":"CMS",
               "portal":"Portal", "forum":"Forum", "ecommerce":"E-commerce",
               "browser":"Browser", "hr":"HR", "office":"Office",
               "information":"Information"}

strs_map = {}
patterns_map = {}
not_strs_map = {}


# Non-IT companies

edu_patterns = [".*大学$", ".*中学$", ".*学校$", ".*学院$", ".*大$"]

patterns_map["edu"] = edu_patterns

edu_strs = ['考试', "大学", "教育", "教师", "研究生院",
            "图书馆", "高校", "学校", "早教", "网校",
            "招生", "考", "学生", "博物馆", "英语",
            "edu.cn", "研究院", "学籍", "北大", "科技馆",
            "科学院", "技校", "新航道", "新东方", "口语100",
            "题库", "学而思"]

strs_map["edu"] = edu_strs

not_edu_strs = ["教育部", "教育局"]

not_strs_map["edu"] = not_edu_strs

gov_patterns = [".*局$", ".*厅$", ".*部$",
                ".*署$", ".*所$", ".*办$", ".*县$"]

patterns_map["gov"] = gov_patterns

gov_strs = ["政府", "委", "协会", "公安", "国家",
            "行政", "警", "法院", "全国", "红十字",
            "工信部", "司法", "gov", "GOV", "G0V",
            "公积金", "档案局", "举报", "检察院",
            "公共", "政务", "出入境", "部门",
            "治安", "测评中心", "中华人民共和国",
            "应急中心", "国土", "部门", "政协",
            "渔政", "组织", "厅", "社保", "社会保障",
            "治安", "总站", "公用", "人口", "地震",
            "国务院", "县", "省级", "总队", "军工",
            "办公室", "省长", "民政", "农业", "地税",
            "信访", "水务", "财税", "监察", "税务",
            "商务部", "禁毒", "工商", "信息化部"]

strs_map["gov"] = gov_strs

not_gov_strs = ["银行", "营业厅", "电网", "超级巡警"]

not_strs_map["gov"] = not_gov_strs

finance_strs = ["保险", "银行", "理财", "投资", 
                "期货", "证券", "证劵", "金融", "贷",
                "信托", "人寿", "支付", "钱",
                "股票", "ATM", "付", "险",
                "信用卡", "银联", "人保", "国泰君安",
                "信用社", "产权", "证卷", "操盘",
                "信用合作", "地产", "比特币", "基金",
                "大智慧", "网银", "众筹", "房产", "证监会",
                "银监会", "农信", "建行", "中信", "万科",
                "聚财", "和讯网"]

strs_map["finance"] = finance_strs

media_strs = ["电视台", "出版", "新闻", "刊",
              "日报", "传媒", "电台", "晚报",
              "卫视", "广播", "电视", "之声",
              "南方周末", "有线", "新华社", "读者",
              "广电"]

strs_map["media"] = media_strs

media_patterns = [".*报$"]

patterns_map["media"] = media_patterns

travel_strs = ["酒店", "宾馆", "旅店", "旅游", "旅馆",
               "旅行", "假期", "旅社", "旅", "锦江之星",
               "汉庭"]

strs_map["travel"] = travel_strs

not_travel_strs = ["旅游局"]

not_strs_map["travel"] = not_travel_strs

entertainment_strs = ["影院", "剧院", "彩票", "彩",
                      "影城", "网吧", "投注网", "大连万达集团股份有限公司",
                      "KTV"]

strs_map["entertainment"] = entertainment_strs

not_entertainment_strs = ["彩云", "彩程"]

not_strs_map["entertainment"] = not_entertainment_strs

health_strs = ['药', '医', "健康", "同仁堂", "病",
               "卫生", "大夫", "血液", "体检", "健身",
               "妇炎洁", "血站"]
               
strs_map["health"] = health_strs

not_health_strs = ["卫生部", "卫生局", "管理局", "药监局"]

not_strs_map["health"] = not_health_strs

food_strs = ["食品", '餐', "美食", "食", "亨氏中国",
             "吉野家", "加多宝", "肯德基", "金龙鱼",
             "奶粉", "七喜", "俏江南", "麦当劳", "农夫山泉"]

strs_map["food"] = food_strs

not_food_strs = ["粮食局"]

not_strs_map["food"] = not_food_strs

trans_strs = ["交通", "物流", "快递", "航空",
              "民航", "铁路", "机场", "地铁",
              "GPS", "租车", "火车站", "公交",
              "船舶", "中铁", "口岸", "邮递",
              "速递", "拼车", "铁道", "高铁",
              "公路", "运输", "邮政"
              "车辆", "长途", "驾校", "申通",
              "海航", "导航", "东航", "海关",
              "速运", "圆通", "客运", "打车",
              "汽运", "国航"]

strs_map["trans"] = trans_strs

not_trans_strs = ["交通局", "运输部", "铁路部", "管理局",
                  "网站导航", "航空局", "网址导航", "运输局",
                  "民航总局", "铁路局", "空管局", "民航局"]
                  
not_strs_map["trans"] = not_trans_strs

comm_strs = ["电话", "通讯", "联通", "电信", "通信",
             "铁通", "宽带", "移动", "邮政", "路由",
             "号码", "邮电", "网络支撑", "华为", "vpn"]

strs_map["comm"] = comm_strs

not_comm_strs = ["威联通科技", "上海电信云存储",
                 "移动互联网创新大会"]

not_strs_map["comm"] = not_comm_strs

manufactoring_strs = ["一汽", "本田", "大众", "马自达", "奔驰",
                      "比亚迪", "海信", "海尔", "东风汽车"]

strs_map["manufactoring"] = manufactoring_strs

not_manufactoring_strs = ["大众网", "大众点评"]

not_strs_map["manufactoring"] = not_manufactoring_strs

# Energy and utilities
energy_strs = ["煤", "油", "核", "电力", "电气", "燃气",
               "电厂", "石化", "电网", "天然气", "发电",
               "供水", "水电", "水利", "电网"]

strs_map["energy"] = energy_strs

not_energy_strs = ["核新同花顺", "广电", "核心"]

not_strs_map["energy"] = not_energy_strs

# IT Companies

# "软件", "存储"

email_strs = ["邮箱", "邮件", "Mail"]

strs_map["email"] = email_strs

mobile_strs = ["三星", "诺基亚", "金立", "小米", "魅族科技",
               "天语手机"]

strs_map["mobile"] = mobile_strs

gaming_strs = ['玩', '游戏', "手游", "联众世界", "盛大网络",
               "第九城市", "上海征途信息技术有限公司", "久游网",
               "完美世界", "巨人网络", "完美时空", "福建网龙",
               "搜狐畅游", "游侠网", "剑圣网络", "傲世堂",
               "盛大在线", "人人豆", "奇客星空", "边锋网络",
               "蓝港在线"]

strs_map["gaming"] = gaming_strs

social_strs = ["人人", "豆瓣", "知乎", '微博',
               "开心网", "世纪佳缘", "百合网", "珍爱网",
               "博客", "SNS", "大众点评"]

strs_map["social"] = social_strs

not_social_strs = ["人人聚财", "人人乐", "人人豆"]

not_strs_map["social"] = not_social_strs

video_strs = ["奇艺", "优酷", "土豆网", "56", "视频",
              "酷6网", "迅雷", "乐视", "PPlive", "pplive",
              "哔哩哔哩弹幕网", "bilibili", "图虫网"]

strs_map["video"] = video_strs

not_video_strs = ["银川迅雷"]

not_strs_map["video"] = not_video_strs

security_strs = ["安全", "金山毒霸", "奇虎360", "江民", "wooyun",
                 "乌云", "防御", "卡巴斯基", "绿盟", "山石",
                 "数字认证", "赛门铁克", "超级巡警", "天融信",
                 "NOD32"]

strs_map["security"] = security_strs


hr_strs = ["人才", "招聘", "人力", "英才", "猎聘网", "job"]

strs_map["hr"] = hr_strs

not_hr_strs = ["人力资源部", "人力资源局"]

not_strs_map["hr"] = not_hr_strs

cms_strs = ['cms', "CMS"]

strs_map["cms"] = cms_strs

portal_strs = ["新浪", "搜狐", "网易", "凤凰网", "TOM在线", "腾讯",
               "人民网", "中华网", "百度", "搜狗", "2345",
               "广东雨林木风计算机科技有限公司", "TOM"]

strs_map["portal"] = portal_strs


forum_strs = ["猫扑", "论坛", "天涯", "社区", "Discuz!"]

strs_map["forum"] = forum_strs

ecommerce_strs = ["阿里巴巴", "淘宝网", "中粮我买网", "当当网",
                  "兰亭集势", "凡客诚品", "拉手网", "美团", 
                  "团宝", "糯米网", "红孩子", "ShopEx", "大麦网",
                  "票务", "商城", "商场", "购", "衣", "服饰",
                "百货", "鸿星尔克", "森马", "超市", "人人乐",
                  "天天果园", "上海远丰信息科技有限公司",
                  "广东东方思维科技有限公司","致远协创"]

strs_map["ecommerce"] = ecommerce_strs

browser_strs = ["浏览器", "UC Mobile", "傲游"]

strs_map["browser"] = browser_strs



office_strs = ["彩程","办公", "用友", "大汉网络", "金蝶", "雨林木风","金山软件","农友",
               "南软科技"]

strs_map["office"] = office_strs


information_strs = ["搜房网","58同城", "赛迪网", "易车", "机锋网", "IT168"]

strs_map["information"] = office_strs

def is_sector(sector, corp):
    
    if sector in not_strs_map:
        for string in not_strs_map[sector]:
            if string in corp:
                return False
    
    if sector in patterns_map:
        for pat in patterns_map[sector]:
            res = re.search(pat, corp)
            if res is not None:
                return True
                
    for string in strs_map[sector]:
        if string in corp:
            return True
    return False

#corp_list_files = ["../data/corp_list.txt", "../data/corp_list_unreg.txt"]


file_map = {}

for sector in sectors:
    file_map[sector] = codecs.open("../data/corp_category_round_1/corp_" + sector + ".txt", 'w', 'utf-8')

f_unsolved_corps = codecs.open("../data/corp_category_round_1/corp_uncategorized.txt", 'w', 'utf-8')

f_corp_list_sort = codecs.open("../data/corp_list_sort.txt", 'r', 'utf-8')

f_human = codecs.open("../data/corp_category_round_1/human_labeled.txt", 'r', 'utf-8')

human_label = {}

uncat_vul_count = 0
uncat_count = 0

for line in f_human:
    strs = line.strip().split(",")
    if len(strs) == 3:
        human_label[strs[0]] = strs[2] 

    
for line in f_corp_list_sort:
    
    strs = line.strip().split(",")    
    
    corp_name = line.split(',')[0].strip()
    
    vul_count = int(strs[len(strs) - 1])
    
    sector_found = False    
    
    for sector in sectors:
            
        if is_sector(sector, corp_name):
            file_map[sector].write(line)
            sector_found = True
            break
    
        
    if not sector_found:
        
        if corp_name in human_label and human_label[corp_name] in sectors:
            #print("Human label: " +  corp_name )
            file_map[human_label[corp_name]].write(line)
        else:
            f_unsolved_corps.write(line)
            uncat_vul_count += vul_count
            uncat_count += 1
        
print("uncat_vul_count: " + str(uncat_vul_count)) 
print("uncat_corp_count: " + str(uncat_count))

f_unsolved_corps.close()

for sector in sectors:
    file_map[sector].close()
