"""
crud/articles 单元测试

建立 CRUD 层 mock 测试模式：用 mock_db_session（AsyncMock）替代真 DB，
验证查询构建逻辑与参数校验分支。后续可按此模式扩展覆盖更多 CRUD。
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.crud import articles as crud_articles


class TestArticlesCrud:
    """测试文章 CRUD 关键路径与校验"""

    @pytest.mark.asyncio
    async def test_get_articles_count_by_status(self, mock_db_session):
        """按状态分组统计：execute 返回 fetchall 结果"""
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("published", 5), ("draft", 2)]
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await crud_articles.get_articles_count_by_status(mock_db_session)

        assert result == [("published", 5), ("draft", 2)]
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_articles_count_invalid_status_raises(self, mock_db_session):
        """非法 status 应抛 ValueError"""
        req = MagicMock()
        req.status = "invalid_status"

        with pytest.raises(ValueError, match="Invalid status"):
            await crud_articles.get_articles_count(mock_db_session, req)

    @pytest.mark.asyncio
    async def test_get_articles_invalid_status_raises(self, mock_db_session):
        """get_articles 同样校验非法 status"""
        req = MagicMock()
        req.status = "invalid_status"

        with pytest.raises(ValueError, match="Invalid status"):
            await crud_articles.get_articles(mock_db_session, reqdata=req)

    @pytest.mark.asyncio
    async def test_get_articles_count_no_filter(self, mock_db_session):
        """reqdata=None 时不过滤，直接 execute + scalar_one_or_none"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 42
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        count = await crud_articles.get_articles_count(mock_db_session, None)

        assert count == 42
