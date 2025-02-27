from typing import Optional, Union

from libs.infinite_scroll_pagination import InfiniteScrollPagination
from extensions.ext_database import db
from models.model import App, EndUser
from models.web import PinnedConversation
from services.conversation_service import ConversationService


class WebConversationService:
    @classmethod
    def pagination_by_last_id(cls, app_model: App, end_user: Optional[EndUser],
                              last_id: Optional[str], limit: int, pinned: Optional[bool] = None) -> InfiniteScrollPagination:
        include_ids = None
        exclude_ids = None
        if pinned is not None:
            pinned_conversations = db.session.query(PinnedConversation).filter(
                PinnedConversation.app_id == app_model.id,
                PinnedConversation.created_by == end_user.id
            ).order_by(PinnedConversation.created_at.desc()).all()
            pinned_conversation_ids = [pc.conversation_id for pc in pinned_conversations]
            if pinned:
                include_ids = pinned_conversation_ids
            else:
                exclude_ids = pinned_conversation_ids

        return ConversationService.pagination_by_last_id(
            app_model=app_model,
            user=end_user,
            last_id=last_id,
            limit=limit,
            include_ids=include_ids,
            exclude_ids=exclude_ids
        )

    @classmethod
    def pin(cls, app_model: App, conversation_id: str, user: Optional[EndUser]):
        pinned_conversation = db.session.query(PinnedConversation).filter(
            PinnedConversation.app_id == app_model.id,
            PinnedConversation.conversation_id == conversation_id,
            PinnedConversation.created_by == user.id
        ).first()

        if pinned_conversation:
            return

        conversation = ConversationService.get_conversation(
            app_model=app_model,
            conversation_id=conversation_id,
            user=user
        )

        pinned_conversation = PinnedConversation(
            app_id=app_model.id,
            conversation_id=conversation.id,
            created_by=user.id
        )

        db.session.add(pinned_conversation)
        db.session.commit()

    @classmethod
    def unpin(cls, app_model: App, conversation_id: str, user: Optional[EndUser]):
        pinned_conversation = db.session.query(PinnedConversation).filter(
            PinnedConversation.app_id == app_model.id,
            PinnedConversation.conversation_id == conversation_id,
            PinnedConversation.created_by == user.id
        ).first()

        if not pinned_conversation:
            return

        db.session.delete(pinned_conversation)
        db.session.commit()
