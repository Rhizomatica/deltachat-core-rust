import calendar
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

from ._utils import AttrDict
from .const import ChatVisibility, ViewType
from .contact import Contact
from .message import Message

if TYPE_CHECKING:
    from datetime import datetime

    from .account import Account
    from .rpc import Rpc


@dataclass
class Chat:
    """Chat object which manages members and through which you can send and retrieve messages."""

    account: "Account"
    id: int

    @property
    def _rpc(self) -> "Rpc":
        return self.account._rpc

    async def delete(self) -> None:
        """Delete this chat and all its messages.

        Note:

        - does not delete messages on server
        - the chat or contact is not blocked, new message will arrive
        """
        await self._rpc.delete_chat(self.account.id, self.id)

    async def block(self) -> None:
        """Block this chat."""
        await self._rpc.block_chat(self.account.id, self.id)

    async def accept(self) -> None:
        """Accept this contact request chat."""
        await self._rpc.accept_chat(self.account.id, self.id)

    async def leave(self) -> None:
        """Leave this chat."""
        await self._rpc.leave_group(self.account.id, self.id)

    async def mute(self, duration: Optional[int] = None) -> None:
        """Mute this chat, if a duration is not provided the chat is muted forever.

        :param duration: mute duration from now in seconds. Must be greater than zero.
        """
        if duration is not None:
            assert duration > 0, "Invalid duration"
            dur: Union[str, dict] = {"Until": duration}
        else:
            dur = "Forever"
        await self._rpc.set_chat_mute_duration(self.account.id, self.id, dur)

    async def unmute(self) -> None:
        """Unmute this chat."""
        await self._rpc.set_chat_mute_duration(self.account.id, self.id, "NotMuted")

    async def pin(self) -> None:
        """Pin this chat."""
        await self._rpc.set_chat_visibility(self.account.id, self.id, ChatVisibility.PINNED)

    async def unpin(self) -> None:
        """Unpin this chat."""
        await self._rpc.set_chat_visibility(self.account.id, self.id, ChatVisibility.NORMAL)

    async def archive(self) -> None:
        """Archive this chat."""
        await self._rpc.set_chat_visibility(self.account.id, self.id, ChatVisibility.ARCHIVED)

    async def unarchive(self) -> None:
        """Unarchive this chat."""
        await self._rpc.set_chat_visibility(self.account.id, self.id, ChatVisibility.NORMAL)

    async def set_name(self, name: str) -> None:
        """Set name of this chat."""
        await self._rpc.set_chat_name(self.account.id, self.id, name)

    async def set_ephemeral_timer(self, timer: int) -> None:
        """Set ephemeral timer of this chat."""
        await self._rpc.set_chat_ephemeral_timer(self.account.id, self.id, timer)

    async def get_encryption_info(self) -> str:
        """Return encryption info for this chat."""
        return await self._rpc.get_chat_encryption_info(self.account.id, self.id)

    async def get_qr_code(self) -> Tuple[str, str]:
        """Get Join-Group QR code text and SVG data."""
        return await self._rpc.get_chat_securejoin_qr_code_svg(self.account.id, self.id)

    async def get_basic_snapshot(self) -> AttrDict:
        """Get a chat snapshot with basic info about this chat."""
        info = await self._rpc.get_basic_chat_info(self.account.id, self.id)
        return AttrDict(chat=self, **info)

    async def get_full_snapshot(self) -> AttrDict:
        """Get a full snapshot of this chat."""
        info = await self._rpc.get_full_chat_by_id(self.account.id, self.id)
        return AttrDict(chat=self, **info)

    async def can_send(self) -> bool:
        """Return true if messages can be sent to the chat."""
        return await self._rpc.can_send(self.account.id, self.id)

    async def send_message(
        self,
        text: Optional[str] = None,
        html: Optional[str] = None,
        viewtype: Optional[ViewType] = None,
        file: Optional[str] = None,
        location: Optional[Tuple[float, float]] = None,
        override_sender_name: Optional[str] = None,
        quoted_msg: Optional[Union[int, Message]] = None,
    ) -> Message:
        """Send a message and return the resulting Message instance."""
        if isinstance(quoted_msg, Message):
            quoted_msg = quoted_msg.id

        draft = {
            "text": text,
            "html": html,
            "viewtype": viewtype,
            "file": file,
            "location": location,
            "overrideSenderName": override_sender_name,
            "quotedMessageId": quoted_msg,
        }
        msg_id = await self._rpc.send_msg(self.account.id, self.id, draft)
        return Message(self.account, msg_id)

    async def send_text(self, text: str) -> Message:
        """Send a text message and return the resulting Message instance."""
        msg_id = await self._rpc.misc_send_text_message(self.account.id, self.id, text)
        return Message(self.account, msg_id)

    async def send_videochat_invitation(self) -> Message:
        """Send a videochat invitation and return the resulting Message instance."""
        msg_id = await self._rpc.send_videochat_invitation(self.account.id, self.id)
        return Message(self.account, msg_id)

    async def send_sticker(self, path: str) -> Message:
        """Send an sticker and return the resulting Message instance."""
        msg_id = await self._rpc.send_sticker(self.account.id, self.id, path)
        return Message(self.account, msg_id)

    async def forward_messages(self, messages: List[Message]) -> None:
        """Forward a list of messages to this chat."""
        msg_ids = [msg.id for msg in messages]
        await self._rpc.forward_messages(self.account.id, msg_ids, self.id)

    async def set_draft(
        self,
        text: Optional[str] = None,
        file: Optional[str] = None,
        quoted_msg: Optional[int] = None,
    ) -> None:
        """Set draft message."""
        if isinstance(quoted_msg, Message):
            quoted_msg = quoted_msg.id
        await self._rpc.misc_set_draft(self.account.id, self.id, text, file, quoted_msg)

    async def remove_draft(self) -> None:
        """Remove draft message."""
        await self._rpc.remove_draft(self.account.id, self.id)

    async def get_draft(self) -> Optional[AttrDict]:
        """Get draft message."""
        snapshot = await self._rpc.get_draft(self.account.id, self.id)
        if not snapshot:
            return None
        snapshot = AttrDict(snapshot)
        snapshot["chat"] = Chat(self.account, snapshot.chat_id)
        snapshot["sender"] = Contact(self.account, snapshot.from_id)
        snapshot["message"] = Message(self.account, snapshot.id)
        return snapshot

    async def get_messages(self, info_only: bool = False, add_daymarker: bool = False) -> List[Message]:
        """get the list of messages in this chat."""
        msgs = await self._rpc.get_message_ids(self.account.id, self.id, info_only, add_daymarker)
        return [Message(self.account, msg_id) for msg_id in msgs]

    async def get_fresh_message_count(self) -> int:
        """Get number of fresh messages in this chat"""
        return await self._rpc.get_fresh_msg_cnt(self.account.id, self.id)

    async def mark_noticed(self) -> None:
        """Mark all messages in this chat as noticed."""
        await self._rpc.marknoticed_chat(self.account.id, self.id)

    async def add_contact(self, *contact: Union[int, str, Contact]) -> None:
        """Add contacts to this group."""
        for cnt in contact:
            if isinstance(cnt, str):
                contact_id = (await self.account.create_contact(cnt)).id
            elif not isinstance(cnt, int):
                contact_id = cnt.id
            else:
                contact_id = cnt
            await self._rpc.add_contact_to_chat(self.account.id, self.id, contact_id)

    async def remove_contact(self, *contact: Union[int, str, Contact]) -> None:
        """Remove members from this group."""
        for cnt in contact:
            if isinstance(cnt, str):
                contact_id = (await self.account.create_contact(cnt)).id
            elif not isinstance(cnt, int):
                contact_id = cnt.id
            else:
                contact_id = cnt
            await self._rpc.remove_contact_from_chat(self.account.id, self.id, contact_id)

    async def get_contacts(self) -> List[Contact]:
        """Get the contacts belonging to this chat.

        For single/direct chats self-address is not included.
        """
        contacts = await self._rpc.get_chat_contacts(self.account.id, self.id)
        return [Contact(self.account, contact_id) for contact_id in contacts]

    async def set_image(self, path: str) -> None:
        """Set profile image of this chat.

        :param path: Full path of the image to use as the group image.
        """
        await self._rpc.set_chat_profile_image(self.account.id, self.id, path)

    async def remove_image(self) -> None:
        """Remove profile image of this chat."""
        await self._rpc.set_chat_profile_image(self.account.id, self.id, None)

    async def get_locations(
        self,
        contact: Optional[Contact] = None,
        timestamp_from: Optional["datetime"] = None,
        timestamp_to: Optional["datetime"] = None,
    ) -> List[AttrDict]:
        """Get list of location snapshots for the given contact in the given timespan."""
        time_from = calendar.timegm(timestamp_from.utctimetuple()) if timestamp_from else 0
        time_to = calendar.timegm(timestamp_to.utctimetuple()) if timestamp_to else 0
        contact_id = contact.id if contact else 0

        result = await self._rpc.get_locations(self.account.id, self.id, contact_id, time_from, time_to)
        locations = []
        contacts: Dict[int, Contact] = {}
        for loc in result:
            location = AttrDict(loc)
            location["chat"] = self
            location["contact"] = contacts.setdefault(location.contact_id, Contact(self.account, location.contact_id))
            location["message"] = Message(self.account, location.msg_id)
            locations.append(location)
        return locations
