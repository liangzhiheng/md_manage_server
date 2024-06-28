# 用户信息操作命令行
from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from user_manage.models import UserModel


class Command(BaseCommand):
    help = "自定义的用户管理命令行"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--init", action="store_true", help='初始化用户信息，仅保留初始管理员信息')
        parser.add_argument("--test", action="store_true", help="并行子命令测试")
    
    def handle(self, *args: Any, **options: Any) -> str | None:
        if options["init"]:
            self.stdout.write("初始化数据库")
        elif options["test"]:
            print(options["test"])
            self.stdout.write("测试")