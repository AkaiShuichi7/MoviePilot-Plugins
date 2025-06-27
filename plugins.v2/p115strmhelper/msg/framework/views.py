# --- START OF FILE qbittorrenthelper/framework/views.py ---

from typing import Dict, Any

from app.log import logger

from .callbacks import Action, encode_action
from .registry import view_registry
from .schemas import TSession


class BaseViewRenderer:
    """
    渲染器基类，定义了渲染视图的核心流程。
    """

    def render(self, session: TSession) -> Dict[str, Any]:
        """
        根据 session 中的 current_view 渲染对应的视图。
        """
        view_name = session.business.current_view
        view_def = view_registry.get_by_name(view_name)

        if view_def:
            try:
                # 通过 view_def.renderer_name 获取方法名，然后用 getattr 调用
                renderer_method = getattr(self, view_def.renderer_name)
                return renderer_method(session)
            except AttributeError:
                logger.error(f"渲染器中未实现方法 '{view_def.renderer_name}' 来渲染视图 '{view_name}'。")
                return self.render_default(session, f"渲染器未实现 '{view_name}' 视图。")
        else:
            logger.warning(f"未找到视图 '{view_name}' 的渲染器。")
            return self.render_default(session, f"无法渲染未知的视图 '{view_name}'。")

    def render_default(self, session, error_text: str = None) -> Dict[str, Any]:
        """
        默认的渲染方法，在找不到特定视图渲染器时调用。
        """
        text = error_text or f"无法渲染视图 '{session.business.current_view}'。"
        return {
            "title": "未知视图",
            "text": text,
            "buttons": [[self._build_common_close_button(session)]]
        }

    @staticmethod
    def _build_button(session: TSession, text: str, action: Action, url: str = None) -> Dict[str, Any]:
        """
        构建一个按钮字典。
        """
        button = {"text": text}
        if url:
            button["url"] = url
        elif action:
            button["callback_data"] = encode_action(session=session, action=action)
        return button

    def _build_common_go_back_button(self, session: TSession, view: str = None) -> Dict[str, Any]:
        """
        构建通用的返回按钮。
        """
        button = {}
        # 如果不是在已关闭的视图，才显示返回按钮
        if session.business.current_view != 'close':
            view = view or session.business.current_view
            button = self._build_button(session, "◀️ 返回", Action(command='go_back', view=view))
        return button

    def _build_common_close_button(self, session: TSession) -> Dict[str, Any]:
        """
        构建通用的关闭按钮。
        """
        button = {}
        # 总是显示关闭按钮，除非在已关闭的视图
        if session.business.current_view != 'close':
            button = self._build_button(session, "❌ 关闭", Action(command='go_to', view='close'))
        return button

    def _build_common_refresh_button(self, session: TSession) -> Dict[str, Any]:
        """
        构建通用的刷新按钮。
        """
        button = {}
        if session.business.current_view != 'close':
            # 如果当前视图不是已关闭的视图，才显示刷新按钮
            button = self._build_button(session, "🔄 刷新", Action(command='go_to', view=session.business.current_view))
        return button

    def _build_common_page_next_button(self, session: TSession) -> Dict[str, Any]:
        """
        构建通用的下一页按钮。
        """
        button = {}
        if session.business.page < session.business.total_pages - 1:
            # 如果还有下一页，才显示下一页按钮
            button = self._build_button(session, "➡️ 下一页", Action(command='go_to', view=session.business.current_view))
        return button

    def _build_common_page_prev_button(self, session: TSession) -> Dict[str, Any]:
        """
        构建通用的上一页按钮。
        :param session:
        :return:
        """
        button = {}
        if session.business.page > 0:
            # 如果还有上一页，才显示上一页按钮
            button = self._build_button(session, "⬅️ 上一页", Action(command='go_to', view=session.business.current_view))
        return button
