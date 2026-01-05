# 音乐知识图谱模块 - 基于实际数据库结构设计
#
# 支持的节点类型：
# - User: 用户
# - Artist: 歌手
# - Song: 歌曲
# - Category: 音乐分类
#
# 支持的关系类型：
# - PERFORMED_BY: 歌曲由歌手演唱
# - BELONGS_TO: 歌曲属于分类
# - LIKED: 用户点赞歌曲
# - PLAYED: 用户播放歌曲
# - SIMILAR_TO: 歌曲相似关系（基于风格、专辑等） 