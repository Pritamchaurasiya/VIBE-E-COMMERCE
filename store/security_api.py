from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import BannedIP

class SecurityDashboardView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        banned_ips = BannedIP.objects.all().values()
        return Response({
            'banned_ips': list(banned_ips),
            'count': len(banned_ips)
        })

    def post(self, request):
        ip = request.data.get('ip')
        reason = request.data.get('reason', 'Manual ban')
        if ip:
            BannedIP.objects.create(ip_address=ip, reason=reason, banned_by=request.user)
            return Response({'success': True})
        return Response({'error': 'IP required'}, status=400)
