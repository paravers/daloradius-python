"""
RADIUS Group Management Service

This module provides business logic for RADIUS group management,
including group attributes, validation, and batch operations.
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.radius import GroupCheckRepository, GroupReplyRepository
from ..schemas.radius import (
    RadgroupcheckCreate, RadgroupreplyCreate,
    GroupAttributesResponse, GroupStatisticsResponse
)
from ..models.radius import GroupCheck, GroupReply


class RadiusGroupService:
    """Service for RADIUS group management operations"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.check_repo = GroupCheckRepository(db_session)
        self.reply_repo = GroupReplyRepository(db_session)

    async def get_all_groups(self) -> List[str]:
        """Get list of all unique group names"""
        check_groups = await self.check_repo.get_groups_list()
        reply_groups = await self.reply_repo.get_groups_list()

        # Combine and deduplicate
        all_groups = sorted(list(set(check_groups + reply_groups)))
        return all_groups

    async def get_group_complete_attributes(self, groupname: str) -> GroupAttributesResponse:
        """Get all attributes for a group (check + reply)"""
        check_attributes = await self.check_repo.get_group_attributes(groupname)
        reply_attributes = await self.reply_repo.get_group_attributes(groupname)

        return GroupAttributesResponse(
            groupname=groupname,
            check_attributes=check_attributes,
            reply_attributes=reply_attributes,
            total_attributes=len(check_attributes) + len(reply_attributes)
        )

    async def create_group_attribute(
        self,
        groupname: str,
        attribute: str,
        operator: str,
        value: str,
        attribute_type: str = "check"
    ) -> Tuple[bool, Any]:
        """
        Create a group attribute (check or reply)
        Returns (success, attribute_object)
        """
        try:
            if attribute_type == "check":
                attr_data = RadgroupcheckCreate(
                    groupname=groupname,
                    attribute=attribute,
                    op=operator,
                    value=value
                )
                result = await self.check_repo.create(attr_data)
            elif attribute_type == "reply":
                attr_data = RadgroupreplyCreate(
                    groupname=groupname,
                    attribute=attribute,
                    op=operator,
                    value=value
                )
                result = await self.reply_repo.create(attr_data)
            else:
                return False, f"Invalid attribute type: {attribute_type}"

            return True, result

        except Exception as e:
            return False, str(e)

    async def update_group_attribute(
        self,
        attribute_id: int,
        attribute_type: str,
        groupname: str,
        attribute: str,
        operator: str,
        value: str
    ) -> Tuple[bool, Any]:
        """
        Update a group attribute
        Returns (success, attribute_object_or_error)
        """
        try:
            if attribute_type == "check":
                attr_data = RadgroupcheckCreate(
                    groupname=groupname,
                    attribute=attribute,
                    op=operator,
                    value=value
                )
                result = await self.check_repo.update(attribute_id, attr_data)
            elif attribute_type == "reply":
                attr_data = RadgroupreplyCreate(
                    groupname=groupname,
                    attribute=attribute,
                    op=operator,
                    value=value
                )
                result = await self.reply_repo.update(attribute_id, attr_data)
            else:
                return False, f"Invalid attribute type: {attribute_type}"

            return True, result

        except Exception as e:
            return False, str(e)

    async def delete_group_attribute(
        self,
        attribute_id: int,
        attribute_type: str
    ) -> Tuple[bool, str]:
        """
        Delete a group attribute
        Returns (success, message)
        """
        try:
            if attribute_type == "check":
                await self.check_repo.delete(attribute_id)
            elif attribute_type == "reply":
                await self.reply_repo.delete(attribute_id)
            else:
                return False, f"Invalid attribute type: {attribute_type}"

            return True, "Attribute deleted successfully"

        except Exception as e:
            return False, str(e)

    async def delete_group_all_attributes(self, groupname: str) -> Dict[str, Any]:
        """Delete all attributes for a group"""
        check_count = await self.check_repo.delete_group_attributes(groupname)
        reply_count = await self.reply_repo.delete_group_attributes(groupname)

        total_deleted = check_count + reply_count

        return {
            "groupname": groupname,
            "check_attributes_deleted": check_count,
            "reply_attributes_deleted": reply_count,
            "total_deleted": total_deleted,
            "message": f"Deleted {total_deleted} attributes for group '{groupname}'"
        }

    async def get_group_statistics(self) -> GroupStatisticsResponse:
        """Get comprehensive group statistics"""
        check_stats = await self.check_repo.get_group_statistics()
        reply_stats = await self.reply_repo.get_group_statistics()

        # Get unique groups
        all_groups = await self.get_all_groups()

        return GroupStatisticsResponse(
            total_groups=len(all_groups),
            total_check_attributes=check_stats['total_attributes'],
            total_reply_attributes=reply_stats['total_attributes'],
            groups_with_attributes=len(all_groups)
        )

    async def validate_group_attribute(
        self,
        attribute: str,
        attribute_type: str = "check"
    ) -> Tuple[bool, str]:
        """
        Validate a RADIUS attribute name
        Returns (is_valid, message)
        """
        if attribute_type == "check":
            # Common check attributes for authentication
            valid_check_attributes = [
                "Auth-Type", "User-Password", "Password", "Crypt-Password",
                "MD5-Password", "SHA-Password", "CHAP-Password", "LM-Password",
                "NT-Password", "SMB-Account-CTRL", "SMB-Account-CTRL-TEXT",
                "Group", "Huntgroup-Name", "Simultaneous-Use", "Called-Station-Id",
                "Calling-Station-Id", "NAS-Port-Type", "Login-LAT-Service",
                "Login-LAT-Node", "Login-LAT-Group", "Framed-AppleTalk-Link",
                "Framed-AppleTalk-Network", "Framed-AppleTalk-Zone"
            ]
            if attribute in valid_check_attributes:
                return True, "Valid check attribute"

        elif attribute_type == "reply":
            # Common reply attributes for authorization
            valid_reply_attributes = [
                "Service-Type", "Framed-Protocol", "Framed-IP-Address",
                "Framed-IP-Netmask", "Framed-Routing", "Filter-Id",
                "Framed-MTU", "Framed-Compression", "Login-IP-Host",
                "Login-Service", "Login-TCP-Port", "Reply-Message",
                "Callback-Number", "Callback-Id", "Framed-Route",
                "Framed-IPX-Network", "Class", "Session-Timeout",
                "Idle-Timeout", "Termination-Action", "Called-Station-Id",
                "Calling-Station-Id", "NAS-Identifier", "Port-Limit",
                "Login-LAT-Service", "Login-LAT-Node", "Login-LAT-Group",
                "Framed-AppleTalk-Link", "Framed-AppleTalk-Network",
                "Framed-AppleTalk-Zone", "Acct-Interim-Interval"
            ]
            if attribute in valid_reply_attributes:
                return True, "Valid reply attribute"

        # Allow custom attributes but warn
        return True, f"Custom attribute - please verify it's supported by your RADIUS server"

    async def batch_create_group_attributes(
        self,
        groupname: str,
        attributes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Batch create multiple group attributes

        attributes format: [
            {
                "attribute": "Session-Timeout",
                "operator": ":=",
                "value": "3600",
                "type": "reply"
            }
        ]
        """
        results = {
            "groupname": groupname,
            "total_requested": len(attributes),
            "created": 0,
            "failed": 0,
            "errors": []
        }

        for attr_data in attributes:
            try:
                attribute = attr_data.get("attribute")
                operator = attr_data.get("operator", ":=")
                value = attr_data.get("value")
                attr_type = attr_data.get("type", "check")

                # Validate required fields
                if not all([attribute, value]):
                    results["errors"].append(
                        f"Missing required fields for attribute: {attr_data}")
                    results["failed"] += 1
                    continue

                # Validate attribute
                is_valid, message = await self.validate_group_attribute(attribute, attr_type)
                if not is_valid:
                    results["errors"].append(
                        f"Invalid attribute '{attribute}': {message}")
                    results["failed"] += 1
                    continue

                # Create the attribute
                success, result = await self.create_group_attribute(
                    groupname, attribute, operator, value, attr_type
                )

                if success:
                    results["created"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(
                        f"Failed to create {attribute}: {result}")

            except Exception as e:
                results["failed"] += 1
                results["errors"].append(
                    f"Exception creating attribute {attr_data}: {str(e)}")

        results["success_rate"] = results["created"] / \
            results["total_requested"] if results["total_requested"] > 0 else 0

        return results

    async def clone_group_attributes(
        self,
        source_group: str,
        target_group: str
    ) -> Dict[str, Any]:
        """
        Clone all attributes from source group to target group
        """
        # Get source group attributes
        source_attrs = await self.get_group_complete_attributes(source_group)

        # Prepare attributes for batch creation
        attributes_to_create = []

        # Add check attributes
        for attr in source_attrs.check_attributes:
            attributes_to_create.append({
                "attribute": attr.attribute,
                "operator": attr.op,
                "value": attr.value,
                "type": "check"
            })

        # Add reply attributes
        for attr in source_attrs.reply_attributes:
            attributes_to_create.append({
                "attribute": attr.attribute,
                "operator": attr.op,
                "value": attr.value,
                "type": "reply"
            })

        # Batch create in target group
        result = await self.batch_create_group_attributes(target_group, attributes_to_create)

        result.update({
            "source_group": source_group,
            "target_group": target_group,
            "source_attributes_found": len(attributes_to_create)
        })

        return result
