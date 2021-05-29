from django.contrib.postgres.search import TrigramSimilarity
from django.conf import settings
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework import permissions
from rest_framework.response import Response

from .serializers import (
    BuildingSerializer,
    BuildingDraftSerializer,
    PublicBuildingDraftCreateSerializer,
    PublicBuildingCreateSerializer,
    PublicBuildingDraftCreateSerializer,
    BuildingListSerializer,
    BuildingSearchSerializer,
    SearchQuerySerializer,
    StatisticSerializer,
)
from .models import Building, BuildingDraft, Statistic


class BuildingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows buildings to be viewed or edited.
    """

    lookup_field = "general_id"

    def get_queryset(self):
        return Building.approved.all().order_by("general_id")

    def get_serializer_class(self):
        if self.action == "list":
            return BuildingListSerializer
        elif self.action == "public_create":
            return PublicBuildingCreateSerializer
        elif self.action == "search":
            return SearchQuerySerializer
        return BuildingSerializer

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.AllowAny],
    )
    def public_create(self, request):
        """
        Special action to allow the public to create a building, while
        keeping the default create action available for staff only
        """
        serializer = PublicBuildingCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="query",
                type=SearchQuerySerializer,
                location=OpenApiParameter.QUERY,
                description="The address of the building",
            )
        ],
        responses=BuildingSearchSerializer,
    )
    @action(
        detail=False,
        permission_classes=[permissions.AllowAny],
    )
    def search(self, request):
        """
        Search a building by its address
        """

        # DRF recommends using request.query_params instead of request.GET
        serializer = SearchQuerySerializer(data=request.query_params)

        if serializer.is_valid():
            query = serializer.data["query"]
            buildings = (
                Building.approved.annotate(similarity=TrigramSimilarity("address", query))
                .filter(similarity__gt=settings.TRIGRAM_SIMILARITY_THRESHOLD)
                .order_by("-similarity")
            )
        else:
            buildings = None

        result_serializer = BuildingSearchSerializer(buildings, many=True)
        return Response(result_serializer.data)


class BuildingDraftViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows building drafts to be viewed or updated.
    """

    lookup_field = "general_id"

    def get_queryset(self):
        return BuildingDraft.objects.all().order_by("general_id")

    def get_serializer_class(self):
        if self.action == "list":
            return BuildingListSerializer
        elif self.action == "public_create":
            return PublicBuildingDraftCreateSerializer
        return BuildingDraftSerializer

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.AllowAny],
    )
    def public_create(self, request):
        """
        Special action to allow the public to create a building draft, while
        keeping the default create action available for staff only
        """
        serializer = PublicBuildingDraftCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((permissions.AllowAny,))
def statistics(self):
    stats = Statistic.objects.first()
    serializer = StatisticSerializer(stats, many=False)

    return Response(serializer.data)
