

from typing import Dict, List, Any
import hashlib
import json
from datetime import datetime, timezone
from clients.file_client import file_client

# 用户模型
class User:
    def __init__(self, db_user: Dict):
        self.id = db_user.get('id')
        self.username = db_user.get('username')
        self.password = db_user.get('password')
        self.real_name = db_user.get('real_name')
        self.phone = db_user.get('phone')
        self.email = db_user.get('email')
        self.avatar_bucket = db_user.get('avatar_bucket')
        self.avatar_object_key = db_user.get('avatar_object_key')
        self.role = db_user.get('role', 0)
        self.status = db_user.get('status', 1)
        self.create_time = db_user.get('create_time')
        self.update_time = db_user.get('update_time')
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'realName': self.real_name,
            'phone': self.phone,
            'email': self.email,
            'avatarBucket': self.avatar_bucket,
            'avatarObjectKey': self.avatar_object_key,
            'role': self.role,
            'status': self.status,
            'createTime': self.create_time,
            'updateTime': self.update_time
        }

# 用户信息VO
class UserInfo:
    def __init__(self, user: User):
        self.id = user.id
        self.username = user.username
        self.real_name = user.real_name
        self.phone = user.phone
        self.email = user.email
        self.avatar_bucket = user.avatar_bucket
        self.avatar_object_key = user.avatar_object_key
        # 构建头像URL
        self.avatar_url = None
        if user.avatar_bucket and user.avatar_object_key:
            self.avatar_url = file_client.get_file_url(user.avatar_bucket, user.avatar_object_key)
        self.role = user.role
        self.status = user.status
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'username': self.username,
            'realName': self.real_name,
            'phone': self.phone,
            'email': self.email,
            'avatarBucket': self.avatar_bucket,
            'avatarObjectKey': self.avatar_object_key,
            'avatarUrl': self.avatar_url,
            'role': self.role,
            'status': self.status
        }

# 用户登录VO
class UserLoginVO:
    def __init__(self, user: User, token: str):
        self.user_info = UserInfo(user)
        self.token = token
    
    def to_dict(self) -> Dict:
        return {
            'userInfo': self.user_info.to_dict(),
            'token': self.token
        }

# 文档模型
class Document:
    def __init__(self, db_document: Dict):
        self.id = db_document.get('id')
        self.title = db_document.get('title')
        self.filename = db_document.get('filename')
        self.file_type = db_document.get('file_type')
        self.file_size = db_document.get('file_size')
        self.content = db_document.get('content')
        self.summary = db_document.get('summary')
        self.file_bucket = db_document.get('file_bucket')
        self.file_object_key = db_document.get('file_object_key')
        self.user_id = db_document.get('user_id')
        self.user_name = db_document.get('user_name')
        self.is_graph_built = db_document.get('is_graph_built', 0)
        self.create_time = db_document.get('create_time')
        self.update_time = db_document.get('update_time')

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'filename': self.filename,
            'fileType': self.file_type,
            'fileSize': self.file_size,
            'content': self.content,
            'summary': self.summary,
            'fileBucket': self.file_bucket,
            'fileObjectKey': self.file_object_key,
            'userId': self.user_id,
            'userName': self.user_name,
            'isGraphBuilt': self.is_graph_built,
            'createTime': self.create_time,
            'updateTime': self.update_time
        }

# 文档信息VO
class DocumentInfo:
    def __init__(self, document: Document):
        self.id = document.id
        self.title = document.title
        self.filename = document.filename
        self.file_type = document.file_type
        self.file_size = document.file_size
        self.content = document.content
        self.summary = document.summary
        self.file_bucket = document.file_bucket
        self.file_object_key = document.file_object_key
        self.user_id = document.user_id
        self.user_name = document.user_name
        self.is_graph_built = document.is_graph_built
        self.create_time = document.create_time
        self.update_time = document.update_time
        # 构建文件URL
        self.file_url = None
        if document.file_bucket and document.file_object_key:
            self.file_url = file_client.get_file_url(document.file_bucket, document.file_object_key)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'filename': self.filename,
            'fileType': self.file_type,
            'fileSize': self.file_size,
            'content': self.content,
            'summary': self.summary,
            'fileBucket': self.file_bucket,
            'fileObjectKey': self.file_object_key,
            'fileUrl': self.file_url,
            'userId': self.user_id,
            'userName': self.user_name,
            'isGraphBuilt': self.is_graph_built,
            'createTime': self.create_time,
            'updateTime': self.update_time
        }

# 分页数据
class PageVO:
    def __init__(self, records: List[Any], total: int, size: int, current: int):
        self.records = records
        self.total = total
        self.size = size
        self.current = current
        self.pages = (total + size - 1) // size if size else 0
    
    def to_dict(self) -> Dict:
        return {
            'records': self.records,
            'total': self.total,
            'size': self.size,
            'current': self.current,
            'pages': self.pages
        }

# 教务政策信息VO
class AcademicPolicyInfo:
    def __init__(self, policy: Dict):
        self.id = policy.get('id')
        self.policy_name = policy.get('policy_name')
        self.policy_type = policy.get('policy_type')
        self.content = policy.get('content')
        self.summary = policy.get('summary')
        self.effective_date = policy.get('effective_date')
        self.status = policy.get('status')
        self.create_time = policy.get('create_time')
        self.update_time = policy.get('update_time')

# 课程信息VO
class CourseInfo:
    def __init__(self, course: Dict):
        self.id = course.get('id')
        self.course_code = course.get('course_code')
        self.course_name = course.get('course_name')
        self.credits = course.get('credits')
        self.hours = course.get('hours')
        self.description = course.get('description')
        self.prerequisites = course.get('prerequisites')
        self.department = course.get('department')
        self.create_time = course.get('create_time')
        self.update_time = course.get('update_time')


# 密码加密
def encrypt_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()