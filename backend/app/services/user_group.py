"""
User Group Association Service

This module provides business logic for user group management,
including validation, association management, and group operations.
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.user import UserRepository, UserGroupRepository
from ..schemas.user import (
    UserGroupCreate, UserGroupResponse,
    UserGroupStatisticsResponse, BatchUserGroupResult
)
from ..models.user import UserGroup


class UserGroupService:
    """Service for user group association management operations"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.user_repo = UserRepository(db_session)
        self.group_repo = UserGroupRepository(db_session)

    async def get_user_groups_detailed(self, username: str) -> Dict[str, Any]:
        """Get detailed information about user's groups"""
        # Check if user exists
        user = await self.user_repo.get_by_username(username)
        if not user:
            return {"error": f"User '{username}' not found", "groups": []}

        # Get groups with details
        groups_with_details = await self.group_repo.get_user_groups_with_details(username)

        # Calculate some statistics
        total_groups = len(groups_with_details)
        highest_priority = max([g["priority"]
                               for g in groups_with_details], default=0)
        lowest_priority = min([g["priority"]
                              for g in groups_with_details], default=0)

        return {
            "username": username,
            "total_groups": total_groups,
            "highest_priority": highest_priority,
            "lowest_priority": lowest_priority,
            "groups": groups_with_details,
            "user_info": {
                "id": user.id,
                "created_at": user.created_at,
                "is_active": user.is_active if hasattr(user, 'is_active') else True
            }
        }

    async def get_group_users_detailed(self, groupname: str) -> Dict[str, Any]:
        """Get detailed information about group's users"""
        users = await self.group_repo.get_group_users(groupname)

        # Get additional user details
        detailed_users = []
        for user_group in users:
            user = await self.user_repo.get_by_username(user_group.username)
            user_detail = {
                "username": user_group.username,
                "priority": user_group.priority,
                "joined_at": user_group.created_at,
                "association_id": user_group.id
            }

            if user:
                user_detail.update({
                    "user_id": user.id,
                    "user_created_at": user.created_at,
                    "is_active": user.is_active if hasattr(user, 'is_active') else True
                })

            detailed_users.append(user_detail)

        # Sort by priority
        detailed_users.sort(key=lambda x: x["priority"])

        return {
            "groupname": groupname,
            "total_users": len(detailed_users),
            "users": detailed_users
        }

    async def validate_user_group_association(
        self,
        username: str,
        groupname: str
    ) -> Tuple[bool, str]:
        """
        Validate if a user-group association is valid
        Returns (is_valid, message)
        """
        # Check if user exists
        user = await self.user_repo.get_by_username(username)
        if not user:
            return False, f"User '{username}' does not exist"

        # Check if user is already in the group
        existing_groups = await self.group_repo.get_user_groups(username)
        if any(ug.groupname == groupname for ug in existing_groups):
            return False, f"User '{username}' is already in group '{groupname}'"

        # Validate group name
        if not groupname or len(groupname.strip()) == 0:
            return False, "Group name cannot be empty"

        if len(groupname) > 64:
            return False, "Group name cannot exceed 64 characters"

        # Check for invalid characters in group name
        invalid_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
        if any(char in groupname for char in invalid_chars):
            return False, "Group name contains invalid characters"

        return True, "Valid association"

    async def add_user_to_group_with_validation(
        self,
        username: str,
        groupname: str,
        priority: int = 1
    ) -> Tuple[bool, Any]:
        """
        Add user to group with comprehensive validation
        Returns (success, result_or_error_message)
        """
        # Validate the association
        is_valid, message = await self.validate_user_group_association(username, groupname)
        if not is_valid:
            return False, message

        # Validate priority
        if priority < 0 or priority > 9999:
            return False, "Priority must be between 0 and 9999"

        try:
            association = await self.group_repo.add_user_to_group(username, groupname, priority)
            return True, association
        except Exception as e:
            return False, f"Failed to add user to group: {str(e)}"

    async def remove_user_from_group_with_validation(
        self,
        username: str,
        groupname: str
    ) -> Tuple[bool, str]:
        """
        Remove user from group with validation
        Returns (success, message)
        """
        # Check if user exists
        user = await self.user_repo.get_by_username(username)
        if not user:
            return False, f"User '{username}' does not exist"

        # Check if user is in the group
        user_groups = await self.group_repo.get_user_groups(username)
        if not any(ug.groupname == groupname for ug in user_groups):
            return False, f"User '{username}' is not in group '{groupname}'"

        try:
            success = await self.group_repo.remove_user_from_group(username, groupname)
            if success:
                return True, f"User '{username}' removed from group '{groupname}' successfully"
            else:
                return False, "Failed to remove user from group"
        except Exception as e:
            return False, f"Failed to remove user from group: {str(e)}"

    async def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive user group statistics"""
        basic_stats = await self.group_repo.get_user_group_statistics()

        # Get additional statistics
        all_groups = await self.group_repo.get_all_groups()
        groups_with_counts = await self.group_repo.get_groups_with_user_count()

        # Calculate average users per group
        if basic_stats["total_groups"] > 0:
            avg_users_per_group = basic_stats["total_associations"] / \
                basic_stats["total_groups"]
        else:
            avg_users_per_group = 0

        # Find groups with no users
        groups_with_users = {g["groupname"] for g in groups_with_counts}
        empty_groups = [g for g in all_groups if g not in groups_with_users]

        # Get users with most groups
        # This would require a more complex query, for now we'll skip it

        return {
            **basic_stats,
            "average_users_per_group": round(avg_users_per_group, 2),
            "empty_groups": empty_groups,
            "empty_groups_count": len(empty_groups),
            "groups_with_users": len(groups_with_users)
        }

    async def batch_manage_user_groups(
        self,
        operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform batch operations on user groups

        operations format: [
            {
                "action": "add" | "remove" | "update_priority",
                "username": "user1",
                "groupname": "group1",
                "priority": 1  # for add/update_priority actions
            }
        ]
        """
        results = {
            "total_operations": len(operations),
            "successful": 0,
            "failed": 0,
            "errors": [],
            "operations_log": []
        }

        for i, operation in enumerate(operations):
            op_result = {
                "index": i,
                "operation": operation,
                "success": False,
                "message": ""
            }

            try:
                action = operation.get("action")
                username = operation.get("username")
                groupname = operation.get("groupname")
                priority = operation.get("priority", 1)

                if not all([action, username, groupname]):
                    op_result["message"] = "Missing required fields: action, username, groupname"
                    results["failed"] += 1
                    results["errors"].append(op_result["message"])
                    results["operations_log"].append(op_result)
                    continue

                if action == "add":
                    success, result = await self.add_user_to_group_with_validation(
                        username, groupname, priority
                    )
                    op_result["success"] = success
                    op_result["message"] = str(
                        result) if not success else "Added successfully"

                elif action == "remove":
                    success, message = await self.remove_user_from_group_with_validation(
                        username, groupname
                    )
                    op_result["success"] = success
                    op_result["message"] = message

                elif action == "update_priority":
                    updated = await self.group_repo.update_user_group_priority(
                        username, groupname, priority
                    )
                    op_result["success"] = updated is not None
                    op_result["message"] = "Priority updated" if updated else "Association not found"

                else:
                    op_result["message"] = f"Unknown action: {action}"
                    results["failed"] += 1
                    results["errors"].append(op_result["message"])
                    results["operations_log"].append(op_result)
                    continue

                if op_result["success"]:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(op_result["message"])

            except Exception as e:
                op_result["success"] = False
                op_result["message"] = f"Exception: {str(e)}"
                results["failed"] += 1
                results["errors"].append(op_result["message"])

            results["operations_log"].append(op_result)

        results["success_rate"] = (
            results["successful"] / results["total_operations"]
            if results["total_operations"] > 0 else 0
        )

        return results

    async def suggest_groups_for_user(self, username: str, limit: int = 5) -> List[str]:
        """
        Suggest groups for a user based on patterns
        This is a simple implementation - could be enhanced with ML
        """
        # Get user's current groups
        user_groups = await self.group_repo.get_user_groups(username)
        current_group_names = {ug.groupname for ug in user_groups}

        # Get all groups with their user counts
        all_groups = await self.group_repo.get_groups_with_user_count()

        # Filter out groups user is already in
        available_groups = [
            g for g in all_groups
            if g["groupname"] not in current_group_names
        ]

        # Sort by user count (popular groups first) and take top suggestions
        available_groups.sort(key=lambda x: x["user_count"], reverse=True)

        return [g["groupname"] for g in available_groups[:limit]]

    async def get_group_hierarchy_info(self, groupname: str) -> Dict[str, Any]:
        """
        Get hierarchy information for a group
        This could be enhanced to support actual group hierarchies
        """
        users = await self.group_repo.get_group_users(groupname)

        # Group users by priority
        priority_groups = {}
        for user_group in users:
            priority = user_group.priority
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(user_group.username)

        # Sort priorities
        sorted_priorities = sorted(priority_groups.keys())

        hierarchy = []
        for priority in sorted_priorities:
            hierarchy.append({
                "priority_level": priority,
                "users": priority_groups[priority],
                "user_count": len(priority_groups[priority])
            })

        return {
            "groupname": groupname,
            "total_users": len(users),
            "priority_levels": len(priority_groups),
            "hierarchy": hierarchy
        }
