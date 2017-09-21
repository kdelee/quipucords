#
# Copyright (c) 2017 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 3 (GPLv3). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv3
# along with this software; if not, see
# https://www.gnu.org/licenses/gpl-3.0.txt.
#
"""Describes the views associatd with the API models"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from api.serializers import CredentialSerializer, HostCredentialSerializer, \
    NetworkProfileSerializer
from api.models import Credential, HostCredential, NetworkProfile

PASSWORD_KEY = 'password'
SUDO_PASSWORD_KEY = 'sudo_password'
PASSWORD_MASK = '********'


def mask_credential(cred):
    """Masks the sensitive values in a credential from being returned on read.

    :param cred: a dictionary of values that may be masked
    :returns: the masked dictionary if it contains sensitive data
    """
    if cred[PASSWORD_KEY]:
        cred[PASSWORD_KEY] = PASSWORD_MASK
    if cred[SUDO_PASSWORD_KEY]:
        cred[SUDO_PASSWORD_KEY] = PASSWORD_MASK
    return cred


# pylint: disable=too-many-ancestors
class CredentialViewSet(ModelViewSet):
    """A view set for the Credential model"""
    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer


class HostCredentialViewSet(ModelViewSet):
    """A view set for the HostCredential model"""
    queryset = HostCredential.objects.all()
    serializer_class = HostCredentialSerializer

    def list(self, request):  # pylint: disable=unused-argument
        serializer = HostCredentialSerializer(self.queryset, many=True)
        for cred in serializer.data:
            cred = mask_credential(cred)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        cred = mask_credential(serializer.data)
        return Response(cred, status=status.HTTP_201_CREATED,
                        headers=headers)

    def retrieve(self, request, pk=None):  # pylint: disable=unused-argument
        host_cred = get_object_or_404(self.queryset, pk=pk)
        serializer = HostCredentialSerializer(host_cred)
        cred = mask_credential(serializer.data)
        return Response(cred)

    # pylint: disable=unused-argument
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        cred = mask_credential(serializer.data)
        return Response(cred)


class NetworkProfileViewSet(ModelViewSet):
    """A view set for NetworkProfiles"""

    queryset = NetworkProfile.objects.all()
    serializer_class = NetworkProfileSerializer

    def list(self, request):  # pylint: disable=unused-argument
        serializer = NetworkProfileSerializer(self.queryset, many=True)
        return Response(serializer.data)

    # pylint: disable=unused-argument
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def retrieve(self, request, pk=None):  # pylint: disable=unused-argument
        network_profile = get_object_or_404(self.queryset, pk=pk)
        serializer = NetworkProfileSerializer(network_profile)
        return Response(serializer.data)

    # pylint: disable=unused-argument
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
