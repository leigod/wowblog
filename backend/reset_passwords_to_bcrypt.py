#!/usr/bin/env python3
"""
一次性运维脚本：将 wb_users 表的密码统一迁移为 bcrypt 格式。

背景
----
历史遗留两套密码格式：
  - 后台路径：bcrypt(md5(password + salt))  —— 列长 32 会截断 bcrypt，实际存的是被截断的哈希
  - 前端注册路径：裸 md5(password + salt)    —— 未包 bcrypt，亿级/秒可爆破，且无法登录

P0 修复后所有路径统一为纯 bcrypt。本脚本对**已存在的全部用户**做一次性迁移：
  1. ALTER TABLE wb_users MODIFY COLUMN password VARCHAR(72)  （旧列仅 32，存不下 60 字符的 bcrypt）
  2. UPDATE wb_users SET password = bcrypt('123456'), salt = NULL

迁移后所有用户密码统一为 123456，用户首次登录后应自行修改。

用法
----
    # 预演（只打印 SQL，不改库）
    python reset_passwords_to_bcrypt.py --dry-run

    # 真实执行（需交互输入 yes 确认）
    python reset_passwords_to_bcrypt.py

    # 跳过确认直接执行（CI / 脚本调用）
    python reset_passwords_to_bcrypt.py --yes

依赖：aiomysql、passlib[bcrypt]（均为项目已有依赖）。
"""
import argparse
import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

# 直接使用 bcrypt 库（passlib 1.7.4 与 bcrypt 4.x 后端初始化不兼容，hash/verify 会抛异常）
import bcrypt

try:
    import aiomysql
except ImportError:  # pragma: no cover
    print("[FATAL] 未安装 aiomysql，请在后端虚拟环境中运行：pip install aiomysql", file=sys.stderr)
    sys.exit(1)


DEFAULT_PASSWORD = "123456"
TABLE = "wb_users"

# ALTER 不显式指定 NULL/NOT NULL，沿用列当前的可空属性，避免现有 NULL 数据导致报错
ALTER_SQL = f"ALTER TABLE {TABLE} MODIFY COLUMN password VARCHAR(72);"
# salt 列在建表时被设为 NOT NULL，但 bcrypt 自带随机盐、salt 不再使用；
# 代码中新用户一律写入 salt=None，故必须放开为可空，否则注册/建号/迁移都会 IntegrityError
ALTER_SALT_SQL = f"ALTER TABLE {TABLE} MODIFY COLUMN salt VARCHAR(64) NULL;"
COUNT_SQL = f"SELECT COUNT(*) FROM {TABLE};"


async def run(dry_run: bool, assume_yes: bool) -> None:
    load_dotenv()

    host = os.getenv("DATABASE_HOST", "127.0.0.1")
    port = int(os.getenv("DATABASE_PORT", "8889"))
    db = os.getenv("DATABASE_NAME", "wowblog")
    user = os.getenv("DATABASE_USER", "root")
    password = os.getenv("DATABASE_PASSWORD")

    if not password:
        print("[FATAL] DATABASE_PASSWORD 未设置，请检查 .env", file=sys.stderr)
        sys.exit(1)

    # 直接用 bcrypt 库生成哈希（绕过 passlib 兼容问题）；bcrypt 上限 72 字节，截断处理
    hashed = bcrypt.hashpw(DEFAULT_PASSWORD.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")
    update_sql = f"UPDATE {TABLE} SET password = %s, salt = NULL;"

    print("=" * 60)
    print("密码迁移：MD5 → bcrypt（统一默认密码 123456）")
    print("=" * 60)
    print(f"目标库 : {user}@{host}:{port}/{db}")
    print(f"目标表 : {TABLE}")
    print(f"默认密码: {DEFAULT_PASSWORD}")
    print(f"bcrypt : {hashed}")
    print("-" * 60)
    print("将执行的 SQL：")
    print(f"  1) {ALTER_SQL}")
    print(f"  2) {ALTER_SALT_SQL}")
    print(f"  3) {update_sql % hashed!r}")
    print("-" * 60)

    if dry_run:
        print("[DRY-RUN] 未连接数据库，未做任何更改。去掉 --dry-run 实际执行。")
        return

    if not assume_yes:
        confirm = input("此操作将重置所有用户密码为 123456，不可撤销。输入 yes 继续: ").strip()
        if confirm.lower() != "yes":
            print("已取消。")
            return

    conn = await aiomysql.connect(
        host=host, port=port, user=user, password=password, db=db, charset="utf8mb4"
    )
    try:
        async with conn.cursor() as cur:
            await cur.execute(COUNT_SQL)
            total = (await cur.fetchone())[0]

            await cur.execute(ALTER_SQL)
            await cur.execute(ALTER_SALT_SQL)
            await cur.execute(update_sql, (hashed,))
            affected = cur.rowcount

        await conn.commit()
        print(f"[OK] 用户总数 {total}，密码已重置行数 {affected}。")
        print(f"[OK] 所有用户密码已统一为 {DEFAULT_PASSWORD}，请通知用户首次登录后修改。")
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="将用户密码一次性迁移为 bcrypt（默认 123456）")
    parser.add_argument("--dry-run", action="store_true", help="只打印 SQL，不连接数据库")
    parser.add_argument("--yes", action="store_true", help="跳过交互确认")
    args = parser.parse_args()
    asyncio.run(run(dry_run=args.dry_run, assume_yes=args.yes))


if __name__ == "__main__":
    main()
