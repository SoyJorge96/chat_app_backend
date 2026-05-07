# """Helpers puros para evaluar permisos por rol."""

# from app.api.v1.modules.users.utils.actions_permissions import Actions


# def has_permission(user_house: HouseUserModel, action: str) -> bool:
#     """Indica si la membresía del usuario puede ejecutar la acción dada."""
#     role = getattr(user_house, "role", None)
#     role_permissions = getattr(role, "role_permissions", []) if role is not None else []
#     permission_codes = {
#         role_permission.permission.code
#         for role_permission in role_permissions
#         if getattr(role_permission, "permission", None) is not None
#     }

#     return Actions.ALL in permission_codes or action in permission_codes
