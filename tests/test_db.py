"""数据库 CRUD 测试 — 使用临时数据库文件"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 在导入 database 前切换 DB 到临时路径
import ljmodel.database as db
db.DB_PATH = os.path.join(tempfile.gettempdir(), ".logic_judge_test.db")

# 重新建表
if os.path.exists(db.DB_PATH):
    os.remove(db.DB_PATH)
db.init_db()

SAMPLE_TEXT = "测试文本: 因为所有人都应该享有自由，所以政府不应限制言论自由。"


def test_save():
    """测试保存分析记录"""
    rid = db.save_analysis(SAMPLE_TEXT, 75, ["formal_logic", "simple_logic"],
                           {"synthesis": {"逻辑质量评分": "75/100"}})
    assert rid > 0, f"保存失败, id={rid}"
    print(f"[OK] test_save: id={rid}")


def test_list():
    """测试列出记录"""
    rows = db.list_analyses()
    assert len(rows) >= 1
    assert rows[0]["text"] == SAMPLE_TEXT
    assert rows[0]["score"] == 75
    print(f"[OK] test_list: {len(rows)} records")


def test_get():
    """测试获取单条详情"""
    rid = db.save_analysis("获取测试", 60, ["bias_detection"], {"synthesis": {}})
    row = db.get_analysis(rid)
    assert row is not None
    assert row["text"] == "获取测试"
    assert row["score"] == 60
    assert "bias_detection" in row["modules"]
    print(f"[OK] test_get: id={rid}")


def test_search():
    """测试关键词搜索"""
    db.save_analysis("人工智能的发展带来了许多伦理问题", 70, [], {})
    db.save_analysis("机器学习是人工智能的一个分支", 65, [], {})
    results = db.search_analyses("人工智能")
    assert len(results) >= 2
    assert all("人工智能" in r["text"] for r in results)
    print(f"[OK] test_search: found {len(results)} records")


def test_delete():
    """测试删除记录"""
    rid = db.save_analysis("待删除文本", 50, [], {})
    assert db.get_analysis(rid) is not None
    ok = db.delete_analysis(rid)
    assert ok
    assert db.get_analysis(rid) is None
    print(f"[OK] test_delete: id={rid}")


def test_get_nonexistent():
    """测试获取不存在的记录"""
    row = db.get_analysis(999999)
    assert row is None
    print("[OK] test_get_nonexistent")


def test_delete_nonexistent():
    """测试删除不存在的记录"""
    ok = db.delete_analysis(999999)
    assert not ok
    print("[OK] test_delete_nonexistent")


def test_clear():
    """测试清空"""
    db.save_analysis("清空前", 10, [], {})
    n = db.clear_history()
    assert n >= 1
    rows = db.list_analyses()
    assert len(rows) == 0
    print(f"[OK] test_clear: deleted {n}")


if __name__ == "__main__":
    test_save()
    test_list()
    test_get()
    test_search()
    test_delete()
    test_get_nonexistent()
    test_delete_nonexistent()
    test_clear()

    # 清理测试 DB（忽略文件锁错误）
    try:
        if os.path.exists(db.DB_PATH):
            os.remove(db.DB_PATH)
    except PermissionError:
        pass
    print("\n所有数据库测试通过!")
