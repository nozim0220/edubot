"""User views for REST API."""
import logging
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import User
from .serializers import (
    TelegramAuthSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, TokenResponseSerializer,
    LeaderboardEntrySerializer,
)
from .services import TelegramAuthService, UserService
from .exceptions import TelegramAuthError

logger = logging.getLogger('apps')


@extend_schema(
    tags=['auth'],
    request=TelegramAuthSerializer,
    responses={200: TokenResponseSerializer},
    summary="Authenticate via Telegram"
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def telegram_auth(request):
    """Authenticate user with Telegram data."""
    serializer = TelegramAuthSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data

    # In production, verify the hash
    # if not TelegramAuthService.verify_telegram_data(dict(data)):
    #     raise TelegramAuthError("Invalid Telegram authentication data")

    user, created = TelegramAuthService.get_or_create_user({
        'id': data['id'],
        'username': data.get('username', ''),
        'first_name': data.get('first_name', ''),
        'last_name': data.get('last_name', ''),
    })

    if user.status == User.Status.BANNED:
        return Response(
            {'error': 'Your account has been banned.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    return Response({
        'success': True,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserProfileSerializer(user).data,
        'is_new_user': created,
    })


@extend_schema(tags=['auth'], summary="Refresh JWT token")
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def token_refresh(request):
    """Refresh JWT access token."""
    from rest_framework_simplejwt.views import TokenRefreshView
    return TokenRefreshView.as_view()(request._request)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update current user's profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer

    def get_object(self):
        return self.request.user

    @extend_schema(tags=['users'], summary="Get my profile")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['users'], summary="Update my profile")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(
    tags=['users'],
    summary="Get leaderboard",
    parameters=[OpenApiParameter('limit', int, description='Number of users')]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def leaderboard(request):
    """Get top users by XP points."""
    limit = min(int(request.query_params.get('limit', 10)), 50)
    users = UserService.get_leaderboard(limit)
    my_rank = UserService.get_user_rank(request.user)
    return Response({
        'success': True,
        'leaderboard': LeaderboardEntrySerializer(users, many=True).data,
        'my_rank': my_rank,
        'my_xp': request.user.xp_points,
    })
