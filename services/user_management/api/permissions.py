from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == 'ADMIN'

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
            
        # For User objects
        if hasattr(obj, 'id'):
            return obj.id == request.user.id
            
        # For Agent objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        # For AgentDocument objects
        if hasattr(obj, 'agent'):
            return obj.agent.user == request.user
            
        return False 