
import sqlite3
from datetime import datetime, timedelta
from config import DB_PATH

class Database:
    # 版权追踪：调整或替换需征得 Y.Y.-XiaoZhan 书面许可。
    def __init__(self):
        # 数据库文件路径
        self.db_path = DB_PATH
        self.initialize_db()

    def initialize_db(self):
        """初始化数据库，创建表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL,
            real_name VARCHAR(50),
            phone VARCHAR(20),
            email VARCHAR(100),
            avatar_bucket VARCHAR(50),
            avatar_object_key VARCHAR(255),
            role INTEGER NOT NULL DEFAULT 0,
            status INTEGER NOT NULL DEFAULT 1,
            create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建文档表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS document (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(255) NOT NULL,
            filename VARCHAR(255) NOT NULL,
            file_type VARCHAR(20) NOT NULL,
            file_size INTEGER NOT NULL,
            content TEXT,
            summary TEXT,
            file_bucket VARCHAR(50),
            file_object_key VARCHAR(255),
            user_id INTEGER NOT NULL,
            user_name VARCHAR(50),
            is_graph_built INTEGER NOT NULL DEFAULT 0,
            create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
        ''')

        # 创建会话表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(255) NOT NULL,
            user_id INTEGER NOT NULL,
            user_name VARCHAR(50),
            create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
        ''')

        # 创建问答历史表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS qa_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT,
            related_entities TEXT,
            graph_context TEXT,
            disease_info_matches TEXT,
            disease_case_matches TEXT,
            keywords TEXT,
            image_bucket VARCHAR(50),
            image_object_key VARCHAR(255),
            image_url VARCHAR(500),
            user_id INTEGER NOT NULL,
            user_name VARCHAR(50),
            create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversation (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
        ''')

        # 检查是否有管理员用户，如果没有则创建
        cursor.execute("SELECT COUNT(*) FROM user WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            # 添加管理员用户(初始密码：123456)
            cursor.execute('''
            INSERT INTO user (username, password, real_name, phone, email, role, status)
            VALUES ('admin', 'e10adc3949ba59abbe56e057f20f883e', '系统管理员', '12345678901', 'admin@example.com', 1, 1)
            ''')

            # 添加测试用户(初始密码：123456)
            cursor.execute('''
            INSERT INTO user (username, password, real_name, phone, email, role, status)
            VALUES ('test', 'e10adc3949ba59abbe56e057f20f883e', '测试用户', '12345678902', 'test@example.com', 0, 1)
            ''')

        # 创建植物病害基本信息表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS plant_disease (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_code VARCHAR(50) NOT NULL,
            disease_name VARCHAR(100) NOT NULL,
            disease_name_en VARCHAR(100),
            pathogen_type VARCHAR(50),
            severity_level VARCHAR(50),
            affected_plants TEXT,
            distribution_area TEXT,
            occurrence_season VARCHAR(100),
            symptoms TEXT,
            prevention_methods TEXT,
            economic_loss REAL,
            description TEXT,
            image_bucket VARCHAR(50),
            image_object_key VARCHAR(255),
            create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 创建植物病害案例表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS disease_case (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_id INTEGER NOT NULL,
            case_title VARCHAR(255) NOT NULL,
            case_date TIMESTAMP,
            location VARCHAR(255),
            plant_type VARCHAR(100),
            infection_area REAL,
            severity_level VARCHAR(50),
            description TEXT,
            economic_loss REAL,
            treatment_method TEXT,
            treatment_result VARCHAR(100),
            images TEXT,
            data_source VARCHAR(255),
            create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (disease_id) REFERENCES plant_disease (id) ON DELETE CASCADE
        )
        ''')

        # 检查植物病害信息表是否为空，如果为空则初始化示例数据
        cursor.execute("SELECT COUNT(*) FROM plant_disease")
        if cursor.fetchone()[0] == 0:
            # 插入植物病害基本信息
            disease_data = [
                (
                    'PD-001',
                    '稻瘟病',
                    'Rice Blast',
                    '真菌',
                    '严重',
                    '["水稻"]',
                    '["全国各稻区"]',
                    '高温高湿季节',
                    '叶片出现梭形病斑，中央灰白色，边缘褐色，严重时叶片枯死',
                    '选用抗病品种；加强田间管理；适时施用三环唑、稻瘟灵等药剂防治',
                    150000.0,
                    '稻瘟病是水稻的主要病害之一，分布广泛，危害严重，可引起大幅减产甚至绝收，是水稻生产中的重要病害。',
                    'plant-disease-images',
                    'PD-001-rice-blast.jpg'
                ),
                (
                    'PD-002',
                    '小麦条锈病',
                    'Wheat Stripe Rust',
                    '真菌',
                    '严重',
                    '["小麦", "大麦"]',
                    '["西北、西南、华北等地"]',
                    '春季',
                    '叶片上出现黄色条状锈斑，严重时整株叶片枯黄',
                    '选用抗病品种；适期播种；及时清除自生麦苗；喷施三唑酮等杀菌剂',
                    280000.0,
                    '小麦条锈病是小麦最重要的病害之一，流行年份可造成30-50%的产量损失，严重威胁小麦生产安全。',
                    'plant-disease-images',
                    'PD-002-wheat-stripe-rust.jpeg'
                ),
                (
                    'PD-003',
                    '番茄晚疫病',
                    'Tomato Late Blight',
                    '卵菌',
                    '严重',
                    '["番茄", "马铃薯"]',
                    '["全国各地"]',
                    '春季和秋季',
                    '叶片出现水渍状暗绿色病斑，迅速扩大变褐，果实出现褐色硬斑',
                    '选用抗病品种；合理密植通风透光；定期喷施甲霜灵、百菌清等药剂',
                    85000.0,
                    '番茄晚疫病是番茄的毁灭性病害，传播快、危害重，流行年份可导致番茄大面积绝收。',
                    'plant-disease-images',
                    'PD-003-tomato-late-blight.jpg'
                ),
                (
                    'PD-004',
                    '柑橘溃疡病',
                    'Citrus Canker',
                    '细菌',
                    '严重',
                    '["柑橘", "橙", "柚", "柠檬"]',
                    '["华南、西南等地"]',
                    '全年发生，夏秋季高发',
                    '叶片、枝梢和果实上出现黄褐色隆起病斑，后期病斑木栓化开裂',
                    '建立无病苗圃；加强检疫；清除病枝病叶；喷施铜制剂保护',
                    120000.0,
                    '柑橘溃疡病是柑橘的重要检疫性病害，不仅影响产量和品质，还严重影响果实的商品价值和出口贸易。',
                    'plant-disease-images',
                    'PD-004-citrus-canker.jpeg'
                ),
                (
                    'PD-005',
                    '玉米大斑病',
                    'Corn Northern Leaf Blight',
                    '真菌',
                    '严重',
                    '["玉米"]',
                    '["东北、华北、西南等地"]',
                    '夏季高温多雨',
                    '叶片上出现长梭形大斑，灰褐色，边缘暗褐色，严重时叶片枯死',
                    '选用抗病品种；合理密植；适时喷施多菌灵、代森锰锌等药剂',
                    95000.0,
                    '玉米大斑病是玉米的主要叶部病害，在高温高湿条件下易流行，可造成20-30%的产量损失。',
                    'plant-disease-images',
                    'PD-005-corn-northern-leaf-blight.jpg'
                ),
                (
                    'PD-006',
                    '黄瓜霜霉病',
                    'Cucumber Downy Mildew',
                    '卵菌',
                    '严重',
                    '["黄瓜", "西葫芦", "甜瓜"]',
                    '["全国各地"]',
                    '春秋季保护地和露地均可发生',
                    '叶片出现黄色多角形病斑，叶背长出灰黑色霉层，严重时叶片干枯',
                    '加强通风降湿；选用抗病品种；喷施烯酰吗啉、霜脲氰等药剂',
                    68000.0,
                    '黄瓜霜霉病是黄瓜的毁灭性病害，传播快、危害重，是保护地黄瓜生产的主要障碍。',
                    'plant-disease-images',
                    'PD-006-cucumber-downy-mildew.jpeg'
                ),
                (
                    'PD-007',
                    '辣椒疫病',
                    'Pepper Phytophthora Blight',
                    '卵菌',
                    '严重',
                    '["辣椒", "甜椒"]',
                    '["全国各地"]',
                    '夏季高温多雨期',
                    '茎基部出现暗绿色水渍状病斑，后变褐缢缩，植株萎蔫枯死',
                    '高垄栽培防涝；轮作倒茬；喷施甲霜灵、烯酰吗啉等药剂',
                    72000.0,
                    '辣椒疫病是辣椒的重要病害，具有暴发性，流行年份可造成毁灭性损失。',
                    'plant-disease-images',
                    'PD-007-pepper-phytophthora-blight.jpeg'
                ),
                (
                    'PD-008',
                    '苹果轮纹病',
                    'Apple Ring Rot',
                    '真菌',
                    '中度',
                    '["苹果", "梨"]',
                    '["华北、西北、东北等地"]',
                    '生长季节',
                    '果实和枝干上出现同心轮纹状病斑，果实腐烂，枝干粗糙龟裂',
                    '刮除病疤涂药保护；清除病残体；喷施多菌灵、甲基托布津等药剂',
                    55000.0,
                    '苹果轮纹病是苹果的重要病害，主要为害果实和枝干，影响果实品质和树势。',
                    'plant-disease-images',
                    'PD-008-apple-ring-rot.jpeg'
                ),
                (
                    'PD-009',
                    '葡萄霜霉病',
                    'Grape Downy Mildew',
                    '卵菌',
                    '严重',
                    '["葡萄"]',
                    '["全国各葡萄产区"]',
                    '春夏多雨季节',
                    '叶片出现淡黄色不规则病斑，叶背产生白色霜霉状物，果穗萎缩',
                    '及时摘除病叶；喷施烯酰吗啉、霜脲氰、代森锰锌等药剂',
                    88000.0,
                    '葡萄霜霉病是葡萄的主要病害之一，在多雨年份易流行，严重影响产量和品质。',
                    'plant-disease-images',
                    'PD-009-grape-downy-mildew.jpeg'
                ),
                (
                    'PD-010',
                    '棉花枯萎病',
                    'Cotton Fusarium Wilt',
                    '真菌',
                    '严重',
                    '["棉花"]',
                    '["黄河流域、长江流域棉区"]',
                    '苗期至开花结铃期',
                    '叶片由下向上逐渐变黄萎蔫，维管束变褐，全株枯死',
                    '选用抗病品种；轮作倒茬；种子处理；合理施肥增强抗性',
                    180000.0,
                    '棉花枯萎病是棉花的毁灭性病害，病菌在土壤中可存活多年，是棉花生产的重大威胁。',
                    'plant-disease-images',
                    'PD-010-cotton-fusarium-wilt.jpeg'
                ),
                (
                    'PD-011',
                    '马铃薯晚疫病',
                    'Potato Late Blight',
                    '卵菌',
                    '特别严重',
                    '["马铃薯", "番茄"]',
                    '["全国各地"]',
                    '冷凉多雨季节',
                    '叶片出现水渍状暗褐色病斑，迅速扩展，薯块出现褐色硬腐',
                    '选用抗病品种；避免连作；喷施甲霜灵、氟啶胺等药剂预防',
                    250000.0,
                    '马铃薯晚疫病是马铃薯的毁灭性病害，历史上曾导致爱尔兰大饥荒，是马铃薯生产的头号威胁。',
                    'plant-disease-images',
                    'PD-011-potato-late-blight.jpeg'
                ),
                (
                    'PD-012',
                    '大豆根腐病',
                    'Soybean Root Rot',
                    '真菌',
                    '中度',
                    '["大豆"]',
                    '["东北、黄淮海等大豆产区"]',
                    '全生育期',
                    '根部和茎基部变褐腐烂，植株矮小黄化，严重时成片死亡',
                    '选用抗病品种；种子包衣处理；合理轮作；改善土壤排水',
                    65000.0,
                    '大豆根腐病是大豆的重要土传病害，在连作地块发病严重，影响大豆产量和品质。',
                    'plant-disease-images',
                    'PD-012-soybean-root-rot.jpeg'
                ),
                (
                    'PD-013',
                    '甘蔗黑穗病',
                    'Sugarcane Smut',
                    '真菌',
                    '严重',
                    '["甘蔗"]',
                    '["华南、西南等蔗区"]',
                    '全生育期',
                    '植株矮化，顶端抽出黑色鞭状物，内含大量黑粉孢子',
                    '选用抗病品种；使用无病种苗；拔除病株；种苗温水处理',
                    110000.0,
                    '甘蔗黑穗病是甘蔗的重要病害，病株不能用于制糖，严重影响甘蔗产量和糖分含量。',
                    'plant-disease-images',
                    'PD-013-sugarcane-smut.jpeg'
                ),
                (
                    'PD-014',
                    '茶树炭疽病',
                    'Tea Anthracnose',
                    '真菌',
                    '中度',
                    '["茶树"]',
                    '["南方茶区"]',
                    '高温多雨季节',
                    '叶片出现褐色圆形或不规则病斑，后期病斑中央灰白色，穿孔脱落',
                    '及时采摘；清除病叶；喷施多菌灵、甲基托布津等药剂',
                    42000.0,
                    '茶树炭疽病是茶树的常见病害，主要为害叶片，影响茶叶产量和品质。',
                    'plant-disease-images',
                    'PD-014-tea-anthracnose.jpeg'
                ),
                (
                    'PD-015',
                    '草莓灰霉病',
                    'Strawberry Gray Mold',
                    '真菌',
                    '严重',
                    '["草莓"]',
                    '["全国各地"]',
                    '冬春保护地栽培期',
                    '果实出现褐色水渍状斑点，后期长出灰色霉层，果实软腐',
                    '控制湿度；摘除病果；喷施嘧霉胺、腐霉利等药剂',
                    58000.0,
                    '草莓灰霉病是草莓保护地栽培的主要病害，严重影响果实产量和商品价值。',
                    'plant-disease-images',
                    'PD-015-strawberry-gray-mold.png'
                ),
                (
                    'PD-016',
                    '大白菜软腐病',
                    'Chinese Cabbage Soft Rot',
                    '细菌',
                    '严重',
                    '["大白菜", "甘蓝", "萝卜"]',
                    '["全国各地"]',
                    '秋季多雨期',
                    '叶柄基部出现水渍状斑，后软腐发臭，整株腐烂',
                    '合理灌溉；防治虫害；喷施农用链霉素、氢氧化铜等药剂',
                    48000.0,
                    '大白菜软腐病是十字花科蔬菜的重要细菌性病害，在高温多雨年份易流行。',
                    'plant-disease-images',
                    'PD-016-chinese-cabbage-soft-rot.jpg'
                ),
                (
                    'PD-017',
                    '桃树流胶病',
                    'Peach Gummosis',
                    '真菌',
                    '中度',
                    '["桃", "樱桃", "李"]',
                    '["全国各果区"]',
                    '全年发生',
                    '枝干出现流胶，树势衰弱，严重时枝条枯死',
                    '加强树体管理；避免机械损伤；刮除病部涂药保护',
                    38000.0,
                    '桃树流胶病是核果类果树的重要病害，影响树势和产量，降低果实品质。',
                    'plant-disease-images',
                    'PD-017-peach-gummosis.jpg'
                ),
                (
                    'PD-018',
                    '香蕉叶斑病',
                    'Banana Leaf Spot',
                    '真菌',
                    '严重',
                    '["香蕉"]',
                    '["华南、云南等蕉区"]',
                    '高温多雨季节',
                    '叶片出现褐色小斑点，扩大成条斑，叶片干枯，影响光合作用',
                    '摘除病叶；喷施代森锰锌、百菌清等保护性杀菌剂',
                    78000.0,
                    '香蕉叶斑病是香蕉的主要叶部病害，严重影响光合作用和产量。',
                    'plant-disease-images',
                    'PD-018-banana-leaf-spot.jpg'
                ),
                (
                    'PD-019',
                    '西瓜枯萎病',
                    'Watermelon Fusarium Wilt',
                    '真菌',
                    '严重',
                    '["西瓜", "甜瓜"]',
                    '["全国各瓜区"]',
                    '开花结果期',
                    '植株突然萎蔫，维管束变褐，全株枯死',
                    '选用抗病品种；嫁接栽培；轮作倒茬；土壤消毒',
                    92000.0,
                    '西瓜枯萎病是西瓜的毁灭性土传病害，病菌在土壤中长期存活，防治困难。',
                    'plant-disease-images',
                    'PD-019-watermelon-fusarium-wilt.jpg'
                ),
                (
                    'PD-020',
                    '油菜菌核病',
                    'Rapeseed Sclerotinia Stem Rot',
                    '真菌',
                    '严重',
                    '["油菜", "向日葵", "大豆"]',
                    '["长江流域、黄淮海等地"]',
                    '开花期',
                    '茎秆出现水渍状病斑，后腐烂，髓部产生黑色菌核',
                    '合理密植通风；清除病残体；喷施菌核净、多菌灵等药剂',
                    135000.0,
                    '油菜菌核病是油菜的主要病害，流行年份可造成20-40%的产量损失。',
                    'plant-disease-images',
                    'PD-020-rapeseed-sclerotinia-stem-rot.jpg'
                )
            ]

            cursor.executemany('''
            INSERT INTO plant_disease (disease_code, disease_name, disease_name_en, pathogen_type,
                                      severity_level, affected_plants, distribution_area, occurrence_season,
                                      symptoms, prevention_methods, economic_loss, description,
                                      image_bucket, image_object_key)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', disease_data)

            # 插入植物病害案例
            case_data = [
                # 稻瘟病的案例
                (
                    1,  # disease_id
                    '湖南省某水稻基地稻瘟病大面积爆发',
                    '2022-07-15 10:00:00',
                    '湖南省长沙市',
                    '水稻',
                    500.0,
                    '严重',
                    '2022年7月中旬，长沙市某水稻种植基地因连续高温高湿天气，稻瘟病大面积爆发。病害从叶部向穗部扩展，感染面积达500亩，叶片大量枯死，穗部变褐坏死。',
                    75000.0,
                    '紧急喷施三环唑和稻瘟灵混合剂进行防治，同时加强田间水肥管理',
                    '基本控制',
                    '[{"bucket": "disease-case-images", "object_key": "DC-001-1-1.jpeg"}, {"bucket": "disease-case-images", "object_key": "DC-001-1-2.webp"}, {"bucket": "disease-case-images", "object_key": "DC-001-1-3.webp"}]',
                    '湖南省农业农村厅'
                ),
                (
                    1,  # disease_id
                    '江苏省水稻穗颈瘟严重发生',
                    '2021-08-20 14:00:00',
                    '江苏省南京市',
                    '水稻',
                    320.0,
                    '严重',
                    '2021年8月下旬，南京市部分水稻田块发生严重穗颈瘟，病穗率高达40%以上。穗颈部变褐坏死，导致大量白穗和瘪粒，严重影响产量和品质。',
                    48000.0,
                    '及时喷施富士一号、三环唑等药剂，并对重病田块进行改种',
                    '部分控制',
                    '[]',
                    '江苏省植保站'
                ),
                # 小麦条锈病的案例
                (
                    2,  # disease_id
                    '甘肃省小麦条锈病大流行',
                    '2020-04-10 09:00:00',
                    '甘肃省天水市',
                    '小麦',
                    1200.0,
                    '特别严重',
                    '2020年春季，甘肃省天水市小麦条锈病大面积流行，发病面积达1200亩。麦叶上密布黄色条状锈斑，严重田块病叶率达100%，叶片提前枯黄脱落，预计减产30-50%。',
                    180000.0,
                    '组织大规模统防统治，使用三唑酮、烯唑醇等药剂进行防治',
                    '有效控制',
                    '[{"bucket": "disease-case-images", "object_key": "DC-002-1-1.png"}]',
                    '甘肃省农业农村厅'
                ),
                (
                    2,  # disease_id
                    '四川省小麦条锈病春季流行',
                    '2019-03-25 11:00:00',
                    '四川省绵阳市',
                    '小麦',
                    800.0,
                    '严重',
                    '2019年3月下旬，绵阳市部分小麦田发生条锈病流行。病害从南部向北部蔓延，发病中心病株率达90%以上，条锈病夏孢子随气流传播，威胁大面积麦田。',
                    95000.0,
                    '启动应急防控预案，组织专业队伍统一喷药防治',
                    '有效控制',
                    '[]',
                    '四川省植保站'
                ),
                # 番茄晚疫病的案例
                (
                    3,  # disease_id
                    '山东省温室番茄晚疫病暴发',
                    '2023-04-12 08:00:00',
                    '山东省寿光市',
                    '番茄',
                    50.0,
                    '严重',
                    '2023年4月，寿光市某温室番茄基地因连阴雨天气，晚疫病突然暴发。叶片出现大量水渍状病斑，果实褐色腐烂，湿度大时病部长出白色霉层。50亩温室番茄受害，部分棚室损失率达80%。',
                    42000.0,
                    '紧急喷施甲霜灵锰锌、烯酰吗啉等药剂，加强通风降湿',
                    '基本控制',
                    '[{"bucket": "disease-case-images", "object_key": "DC-003-1-1.jpg"}, {"bucket": "disease-case-images", "object_key": "DC-003-1-2.png"}, {"bucket": "disease-case-images", "object_key": "DC-003-1-3.jpg"}]',
                    '寿光市农业技术推广中心'
                ),
                (
                    3,  # disease_id
                    '河北省露地番茄晚疫病流行',
                    '2022-06-18 15:00:00',
                    '河北省廊坊市',
                    '番茄',
                    180.0,
                    '严重',
                    '2022年6月梅雨季节，廊坊市露地番茄发生严重晚疫病。病害迅速蔓延，3-5天内即可导致全田发病。叶片、茎秆、果实均受害，造成大面积死株。',
                    55000.0,
                    '及时摘除病叶病果，喷施保护性和治疗性药剂交替使用',
                    '部分控制',
                    '[]',
                    '河北省植保植检站'
                ),
                # 柑橘溃疡病的案例
                (
                    4,  # disease_id
                    '广东省柑橘溃疡病严重发生',
                    '2021-07-20 10:00:00',
                    '广东省梅州市',
                    '柑橘',
                    300.0,
                    '严重',
                    '2021年7月，梅州市某柑橘园发生严重溃疡病。新梢、叶片和果实上出现大量隆起的褐色溃疡斑，严重影响果实品质和商品价值。病园面积达300亩，病果率30-50%。',
                    90000.0,
                    '剪除病枝病叶集中烧毁，喷施铜制剂保护，加强肥水管理增强树势',
                    '基本控制',
                    '[]',
                    '广东省柑橘研究所'
                ),
                (
                    4,  # disease_id
                    '广西柑橘溃疡病检疫性疫情',
                    '2020-09-05 14:00:00',
                    '广西壮族自治区桂林市',
                    '柑橘',
                    150.0,
                    '严重',
                    '2020年9月，桂林市某新建柑橘园发现溃疡病疫情。经检测为强致病性菌系，启动检疫性病害应急处置预案。病园150亩全部进行隔离处理。',
                    68000.0,
                    '划定疫区和保护区，病树全部砍除销毁，周边果园喷药保护',
                    '已根除',
                    '[{"bucket": "disease-case-images", "object_key": "DC-004-2-1.webp"}, {"bucket": "disease-case-images", "object_key": "DC-004-2-2.webp"}]',
                    '广西植物保护站'
                ),
                # 玉米大斑病的案例
                (
                    5,  # disease_id
                    '吉林省玉米大斑病大面积流行',
                    '2022-08-10 09:00:00',
                    '吉林省长春市',
                    '玉米',
                    800.0,
                    '严重',
                    '2022年8月初，长春市部分玉米田因连续阴雨天气，大斑病大面积流行。病斑从下部叶片向上蔓延，病叶率达70%以上，严重影响玉米灌浆。',
                    85000.0,
                    '及时喷施多菌灵、代森锰锌等药剂，加强田间排水',
                    '有效控制',
                    '[]',
                    '吉林省植保站'
                ),
                (
                    5,  # disease_id
                    '黑龙江省玉米大斑病中度发生',
                    '2021-07-25 14:00:00',
                    '黑龙江省哈尔滨市',
                    '玉米',
                    600.0,
                    '中度',
                    '2021年7月下旬，哈尔滨市部分玉米种植区发生中度大斑病。主要发生在感病品种上，叶片出现典型的梭形大斑，影响产量形成。',
                    52000.0,
                    '选用抗病品种，适时喷施保护性杀菌剂',
                    '基本控制',
                    '[{"bucket": "disease-case-images", "object_key": "DC-005-2-1.jpeg"}]',
                    '黑龙江省农业农村厅'
                ),
                # 黄瓜霜霉病的案例
                (
                    6,  # disease_id
                    '北京市温室黄瓜霜霉病暴发',
                    '2023-04-20 10:00:00',
                    '北京市大兴区',
                    '黄瓜',
                    80.0,
                    '严重',
                    '2023年4月，大兴区某温室黄瓜基地因湿度过高，霜霉病突然暴发。叶片上出现大量黄色多角形病斑，叶背长满灰黑色霉层，2-3天内蔓延全棚。',
                    48000.0,
                    '紧急加强通风降湿，连续喷施烯酰吗啉、霜脲氰等药剂',
                    '基本控制',
                    '[]',
                    '北京市植保站'
                ),
                (
                    6,  # disease_id
                    '河南省露地黄瓜霜霉病流行',
                    '2022-09-15 08:00:00',
                    '河南省郑州市',
                    '黄瓜',
                    250.0,
                    '严重',
                    '2022年9月秋季多雨，郑州市露地黄瓜发生严重霜霉病。病害迅速蔓延，叶片大量枯死，严重影响黄瓜产量和品质。',
                    38000.0,
                    '摘除病叶，喷施保护性和治疗性药剂交替使用',
                    '部分控制',
                    '[{"bucket": "disease-case-images", "object_key": "DC-006-2-1.jpeg"}]',
                    '河南省植保植检站'
                ),
                # 辣椒疫病的案例
                (
                    7,  # disease_id
                    '湖南省辣椒疫病大面积暴发',
                    '2023-07-10 11:00:00',
                    '湖南省湘潭市',
                    '辣椒',
                    420.0,
                    '特别严重',
                    '2023年7月梅雨季节，湘潭市辣椒种植区因连续暴雨积水，疫病大面积暴发。茎基部腐烂，植株成片萎蔫死亡，损失严重。',
                    95000.0,
                    '紧急排水，拔除病株，喷施甲霜灵、烯酰吗啉等药剂',
                    '部分控制',
                    '[]',
                    '湖南省农业技术推广站'
                ),
                (
                    7,  # disease_id
                    '四川省辣椒疫病流行',
                    '2022-06-25 15:00:00',
                    '四川省成都市',
                    '辣椒',
                    300.0,
                    '严重',
                    '2022年6月，成都市部分辣椒田发生严重疫病。高温多雨天气导致病害迅速蔓延，茎秆和果实均受害，造成大量死株烂果。',
                    58000.0,
                    '高垄栽培改善排水，及时喷药防治',
                    '基本控制',
                    '[{"bucket": "disease-case-images", "object_key": "DC-007-2-1.png"}, {"bucket": "disease-case-images", "object_key": "DC-007-2-2.jpeg"}]',
                    '四川省植保站'
                ),
                # 苹果轮纹病的案例
                (
                    8,  # disease_id
                    '陕西省苹果轮纹病中度发生',
                    '2022-09-20 09:00:00',
                    '陕西省咸阳市',
                    '苹果',
                    350.0,
                    '中度',
                    '2022年9月，咸阳市部分苹果园发生中度轮纹病。果实和枝干上出现典型的轮纹状病斑，影响果实商品价值和树势。',
                    42000.0,
                    '刮除枝干病疤涂药，摘除病果，喷施多菌灵等药剂',
                    '有效控制',
                    '[{"bucket": "disease-case-images", "object_key": "DC-008-1-1.webp"}, {"bucket": "disease-case-images", "object_key": "DC-008-1-2.jpeg"}]',
                    '陕西省果业局'
                ),
                (
                    8,  # disease_id
                    '山东省苹果轮纹病流行',
                    '2021-08-30 13:00:00',
                    '山东省烟台市',
                    '苹果',
                    280.0,
                    '中度',
                    '2021年8月，烟台市苹果产区因高温多雨，轮纹病发生较重。果实病果率达15-20%，枝干粗皮病严重，影响果树生长。',
                    35000.0,
                    '加强果园管理，清除病残体，定期喷药保护',
                    '基本控制',
                    '[]',
                    '山东省果树研究所'
                ),
                # 葡萄霜霉病的案例
                (
                    9,  # disease_id
                    '新疆葡萄霜霉病流行',
                    '2023-06-18 10:00:00',
                    '新疆维吾尔自治区吐鲁番市',
                    '葡萄',
                    200.0,
                    '严重',
                    '2023年6月，吐鲁番市部分葡萄园因降雨频繁，霜霉病流行。叶片上出现大量油渍状病斑，叶背长出白色霜霉，果穗萎缩严重。',
                    68000.0,
                    '及时摘除病叶，连续喷施烯酰吗啉、霜脲氰等药剂',
                    '有效控制',
                    '[]',
                    '新疆农业科学院'
                ),
                (
                    9,  # disease_id
                    '河北省葡萄霜霉病暴发',
                    '2022-07-12 14:00:00',
                    '河北省张家口市',
                    '葡萄',
                    150.0,
                    '严重',
                    '2022年7月，张家口市葡萄产区遭遇持续阴雨，霜霉病突然暴发。病害蔓延迅速，3-5天内全园发病，严重影响葡萄品质和产量。',
                    52000.0,
                    '加强通风透光，喷施保护性和治疗性杀菌剂',
                    '基本控制',
                    '[{"bucket": "disease-case-images", "object_key": "DC-009-2-1.png"}, {"bucket": "disease-case-images", "object_key": "DC-009-2-2.jpeg"}, {"bucket": "disease-case-images", "object_key": "DC-009-2-3.jpeg"}]',
                    '河北省林果研究所'
                ),
                # 棉花枯萎病的案例
                (
                    10,  # disease_id
                    '新疆棉花枯萎病严重发生',
                    '2022-07-20 09:00:00',
                    '新疆维吾尔自治区阿克苏地区',
                    '棉花',
                    1500.0,
                    '严重',
                    '2022年7月，阿克苏地区部分连作棉田枯萎病严重发生。病株率达30-40%，叶片由下向上变黄萎蔫，维管束变褐，造成大量死株。',
                    195000.0,
                    '轮作倒茬，选用抗病品种，增施有机肥改良土壤',
                    '部分控制',
                    '[]',
                    '新疆农业技术推广总站'
                ),
                (
                    10,  # disease_id
                    '河南省棉花枯萎病流行',
                    '2021-06-30 11:00:00',
                    '河南省安阳市',
                    '棉花',
                    800.0,
                    '严重',
                    '2021年6月，安阳市棉区发生枯萎病流行。病田分布集中，病株呈点片发生，严重影响棉花生长发育和产量形成。',
                    98000.0,
                    '拔除病株，种植抗病品种，合理施肥增强抗性',
                    '基本控制',
                    '[{"bucket": "disease-case-images", "object_key": "DC-010-2-1.jpeg"}, {"bucket": "disease-case-images", "object_key": "DC-010-2-2.jpeg"}, {"bucket": "disease-case-images", "object_key": "DC-010-2-3.jpeg"}]',
                    '河南省棉花研究所'
                ),
                # 马铃薯晚疫病的案例
                (
                    11,  # disease_id
                    '云南省马铃薯晚疫病大流行',
                    '2023-08-15 08:00:00',
                    '云南省昭通市',
                    '马铃薯',
                    1200.0,
                    '特别严重',
                    '2023年8月，昭通市马铃薯产区因连续阴雨低温，晚疫病大流行。病害蔓延迅速，2-3天即全田发病，叶片枯死，薯块腐烂，损失惨重。',
                    285000.0,
                    '紧急组织统防统治，喷施甲霜灵、氟啶胺等药剂',
                    '部分控制',
                    '[{"bucket": "disease-case-images", "object_key": "DC-011-1-1.jpg"}]',
                    '云南省农业农村厅'
                ),
                (
                    11,  # disease_id
                    '内蒙古马铃薯晚疫病严重发生',
                    '2022-07-28 10:00:00',
                    '内蒙古自治区乌兰察布市',
                    '马铃薯',
                    900.0,
                    '严重',
                    '2022年7月，乌兰察布市马铃薯种植区遭遇冷凉多雨天气，晚疫病严重发生。病叶率达80%以上，薯块腐烂率30-40%，严重影响产量。',
                    215000.0,
                    '及时喷施保护性和治疗性药剂，加强田间管理',
                    '有效控制',
                    '[]',
                    '内蒙古农业技术推广站'
                ),
                # 大豆根腐病的案例
                (
                    12,  # disease_id
                    '黑龙江省大豆根腐病严重发生',
                    '2022-07-10 14:00:00',
                    '黑龙江省齐齐哈尔市',
                    '大豆',
                    650.0,
                    '中度',
                    '2022年7月，齐齐哈尔市部分大豆连作田发生严重根腐病。植株根部和茎基部腐烂，叶片黄化，成片死亡，影响大豆产量。',
                    58000.0,
                    '合理轮作，种子包衣处理，改善田间排水条件',
                    '基本控制',
                    '[{"bucket": "disease-case-images", "object_key": "DC-012-1-1.png"}]',
                    '黑龙江省大豆研究所'
                ),
                (
                    12,  # disease_id
                    '辽宁省大豆根腐病中度发生',
                    '2021-08-05 09:00:00',
                    '辽宁省铁岭市',
                    '大豆',
                    480.0,
                    '中度',
                    '2021年8月，铁岭市大豆田因土壤排水不良，根腐病中度发生。病株矮小黄化，根系腐烂变褐，影响大豆生长和产量。',
                    42000.0,
                    '选用抗病品种，改善土壤条件，合理施肥',
                    '有效控制',
                    '[]',
                    '辽宁省农业科学院'
                ),
                # 甘蔗黑穗病的案例
                (
                    13,  # disease_id
                    '广西甘蔗黑穗病严重发生',
                    '2022-10-12 10:00:00',
                    '广西壮族自治区崇左市',
                    '甘蔗',
                    450.0,
                    '严重',
                    '2022年10月，崇左市部分蔗区发现黑穗病严重发生。病株率达15-20%，植株矮化，顶端抽出黑色鞭状物，严重影响甘蔗产量和糖分。',
                    98000.0,
                    '拔除病株集中销毁，选用抗病品种，种苗温水处理',
                    '有效控制',
                    '[]',
                    '广西糖业研究所'
                ),
                (
                    13,  # disease_id
                    '云南省甘蔗黑穗病流行',
                    '2021-09-20 13:00:00',
                    '云南省德宏州',
                    '甘蔗',
                    380.0,
                    '严重',
                    '2021年9月，德宏州蔗区黑穗病流行。病害在易感品种上发生严重，病株不能用于制糖，造成较大经济损失。',
                    85000.0,
                    '更换抗病品种，使用无病健康种苗，加强田间管理',
                    '基本控制',
                    '[]',
                    '云南省甘蔗研究所'
                ),
                # 茶树炭疽病的案例
                (
                    14,  # disease_id
                    '浙江省茶树炭疽病中度发生',
                    '2023-07-25 11:00:00',
                    '浙江省杭州市',
                    '茶树',
                    220.0,
                    '中度',
                    '2023年7月，杭州市部分茶园因高温多雨，炭疽病中度发生。叶片出现褐色病斑，后期穿孔脱落，影响茶叶品质和产量。',
                    35000.0,
                    '及时采摘，清除病叶，喷施多菌灵等保护性杀菌剂',
                    '有效控制',
                    '[]',
                    '浙江省茶叶研究院'
                ),
                (
                    14,  # disease_id
                    '福建省茶树炭疽病流行',
                    '2022-08-18 14:00:00',
                    '福建省福州市',
                    '茶树',
                    180.0,
                    '轻度',
                    '2022年8月，福州市茶区发生轻度炭疽病。主要在老叶上发生，病斑较少，对茶叶生产影响不大。',
                    18000.0,
                    '加强茶园管理，适时修剪，喷施保护性杀菌剂',
                    '有效控制',
                    '[]',
                    '福建省农业科学院茶叶研究所'
                ),
                # 草莓灰霉病的案例
                (
                    15,  # disease_id
                    '辽宁省温室草莓灰霉病暴发',
                    '2023-02-15 09:00:00',
                    '辽宁省沈阳市',
                    '草莓',
                    60.0,
                    '严重',
                    '2023年2月，沈阳市温室草莓因湿度过高，灰霉病突然暴发。果实大量腐烂，长满灰色霉层，商品果率不足50%，损失严重。',
                    52000.0,
                    '加强通风降湿，及时摘除病果，喷施嘧霉胺、腐霉利等药剂',
                    '基本控制',
                    '[]',
                    '辽宁省果树科学研究所'
                ),
                (
                    15,  # disease_id
                    '江苏省草莓灰霉病流行',
                    '2022-03-10 10:00:00',
                    '江苏省南京市',
                    '草莓',
                    45.0,
                    '严重',
                    '2022年3月，南京市草莓大棚因连续阴雨，灰霉病流行。病果率达40-50%，严重影响草莓产量和经济效益。',
                    38000.0,
                    '控制湿度，摘除病果病叶，药剂防治与物理防治结合',
                    '有效控制',
                    '[]',
                    '江苏省农业科学院'
                ),
                # 大白菜软腐病的案例
                (
                    16,  # disease_id
                    '河北省大白菜软腐病严重发生',
                    '2022-10-20 08:00:00',
                    '河北省邯郸市',
                    '大白菜',
                    550.0,
                    '严重',
                    '2022年10月，邯郸市大白菜产区因连续降雨，软腐病严重发生。叶柄基部软腐发臭，整株腐烂，田间损失率达30-40%。',
                    75000.0,
                    '及时排水，防治虫害，喷施农用链霉素等药剂',
                    '部分控制',
                    '[]',
                    '河北省蔬菜研究所'
                ),
                (
                    16,  # disease_id
                    '山东省大白菜软腐病流行',
                    '2021-11-05 13:00:00',
                    '山东省潍坊市',
                    '大白菜',
                    420.0,
                    '严重',
                    '2021年11月，潍坊市大白菜收获期遭遇暴雨，软腐病流行。大量白菜腐烂变质，无法贮藏和销售，经济损失严重。',
                    58000.0,
                    '加强田间管理，控制虫害传播，及时采收',
                    '基本控制',
                    '[]',
                    '山东省农业技术推广总站'
                ),
                # 桃树流胶病的案例
                (
                    17,  # disease_id
                    '河北省桃树流胶病中度发生',
                    '2022-06-15 11:00:00',
                    '河北省保定市',
                    '桃',
                    280.0,
                    '中度',
                    '2022年6月，保定市部分桃园发生中度流胶病。枝干出现流胶现象，树势衰弱，影响桃树生长和果实品质。',
                    32000.0,
                    '加强树体管理，刮除病部涂药保护，增施有机肥增强树势',
                    '有效控制',
                    '[]',
                    '河北省农林科学院'
                ),
                (
                    17,  # disease_id
                    '山西省桃树流胶病普遍发生',
                    '2021-07-22 14:00:00',
                    '山西省运城市',
                    '桃',
                    320.0,
                    '轻度',
                    '2021年7月，运城市桃产区普遍发生轻度流胶病。主要在老树和弱树上发生，流胶量不大，及时处理可控制病情。',
                    25000.0,
                    '改善栽培管理，避免机械损伤，刮治病部',
                    '有效控制',
                    '[]',
                    '山西省果树研究所'
                ),
                # 香蕉叶斑病的案例
                (
                    18,  # disease_id
                    '广东省香蕉叶斑病严重发生',
                    '2023-08-20 10:00:00',
                    '广东省湛江市',
                    '香蕉',
                    400.0,
                    '严重',
                    '2023年8月，湛江市香蕉产区因高温多雨，叶斑病严重发生。叶片大量枯死，严重影响光合作用，造成香蕉减产和品质下降。',
                    82000.0,
                    '及时摘除病叶，定期喷施代森锰锌、百菌清等药剂',
                    '有效控制',
                    '[]',
                    '广东省农业科学院果树研究所'
                ),
                (
                    18,  # disease_id
                    '海南省香蕉叶斑病流行',
                    '2022-09-12 13:00:00',
                    '海南省海口市',
                    '香蕉',
                    350.0,
                    '严重',
                    '2022年9月，海口市香蕉种植区叶斑病流行。病害在台风过后迅速发展，叶片枯死率达60-70%，影响香蕉产量和品质。',
                    68000.0,
                    '加强蕉园管理，清除病叶，喷施保护性杀菌剂',
                    '基本控制',
                    '[]',
                    '海南省农业技术推广总站'
                ),
                # 西瓜枯萎病的案例
                (
                    19,  # disease_id
                    '河南省西瓜枯萎病严重发生',
                    '2023-06-25 09:00:00',
                    '河南省开封市',
                    '西瓜',
                    380.0,
                    '严重',
                    '2023年6月，开封市西瓜产区因连作，枯萎病严重发生。植株突然萎蔫死亡，发病中心病株率达80%以上，造成大面积绝收。',
                    95000.0,
                    '采用嫁接苗，轮作倒茬，土壤消毒处理',
                    '部分控制',
                    '[]',
                    '河南省西甜瓜研究所'
                ),
                (
                    19,  # disease_id
                    '山东省西瓜枯萎病流行',
                    '2022-07-08 14:00:00',
                    '山东省聊城市',
                    '西瓜',
                    320.0,
                    '严重',
                    '2022年7月，聊城市西瓜田发生严重枯萎病。病害呈点片发生，病株维管束变褐，全株枯死，严重影响西瓜生产。',
                    78000.0,
                    '推广嫁接栽培技术，避免连作，选用抗病砧木',
                    '有效控制',
                    '[]',
                    '山东省农业科学院'
                ),
                # 油菜菌核病的案例
                (
                    20,  # disease_id
                    '湖北省油菜菌核病大流行',
                    '2023-04-10 08:00:00',
                    '湖北省荆州市',
                    '油菜',
                    1800.0,
                    '特别严重',
                    '2023年4月，荆州市油菜产区因花期连续阴雨，菌核病大流行。病株率达60-80%，茎秆腐烂倒伏，产量损失30-50%，是近年来最严重的一次流行。',
                    245000.0,
                    '紧急组织统防统治，喷施菌核净、多菌灵等药剂',
                    '部分控制',
                    '[]',
                    '湖北省农业农村厅'
                ),
                (
                    20,  # disease_id
                    '安徽省油菜菌核病严重发生',
                    '2022-03-28 10:00:00',
                    '安徽省合肥市',
                    '油菜',
                    1200.0,
                    '严重',
                    '2022年3月，合肥市油菜花期遭遇连续降雨，菌核病严重发生。病害从花瓣侵入，向茎秆蔓延，造成大量倒伏和减产。',
                    158000.0,
                    '花期喷药保护，合理密植，清除病残体',
                    '有效控制',
                    '[]',
                    '安徽省农业科学院'
                )
            ]

            cursor.executemany('''
            INSERT INTO disease_case (disease_id, case_title, case_date, location, plant_type,
                                     infection_area, severity_level, description, economic_loss,
                                     treatment_method, treatment_result, images, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', case_data)


        conn.commit()
        conn.close()

    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def query(self, sql, params=(), fetchone=False):
        """执行查询SQL并返回结果

        数据库查询封装层 - Database Abstraction Layer
        Designed by 羊小栈 © 2025 - Ensures consistent data access patterns
        提供统一的查询接口，自动转换结果为字典格式，简化业务层代码
        """
        conn = self.get_connection()
        # 使用行工厂获取结果为字典
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()
        cursor.execute(sql, params)
        if fetchone:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        conn.close()
        return result

    def execute(self, sql, params=()):
        """执行非查询SQL"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        # 获取受影响的行数
        rowcount = cursor.rowcount
        conn.commit()
        conn.close()
        return rowcount

    def execute_many(self, sql, params_list):
        """批量执行SQL"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executemany(sql, params_list)
        conn.commit()
        conn.close()

    def _dict_factory(self, cursor, row):
        """将查询结果转换为字典格式"""
        d = {}
        timestamp_fields = {
            'create_time', 'update_time', 'generate_time', 'dissipate_time', 'case_date'
        }
        for idx, col in enumerate(cursor.description):
            key = col[0]
            value = row[idx]
            if key in timestamp_fields and value:
                converted = self._convert_to_local_time(value)
                d[key] = converted
            else:
                d[key] = value
        return d

    @staticmethod
    def _convert_to_local_time(value):
        """将UTC时间字符串转换为本地时间（+8小时）"""
        if not value:
            return value
        try:
            dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            dt += timedelta(hours=8)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return value

# 创建数据库单例
db = Database() 
# Fingerprint: yyXiaoZhan.DB.guard.2025 🛡️
