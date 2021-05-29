from enum import Enum

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from import_export import resources


class SectorChoice(Enum):
    s1 = _("Sector 1")
    s2 = _("Sector 2")
    s3 = _("Sector 3")
    s4 = _("Sector 4")
    s5 = _("Sector 5")
    s6 = _("Sector 6")


class SeismicCategoryChoice(Enum):
    NA = _("N/A")
    U1 = _("U1")
    U2 = _("U2")
    U3 = _("U3")
    U4 = _("U4")
    RS1 = _("RS I")
    RS2 = _("RS II")
    RS3 = _("RS III")
    RS4 = _("RS IV")

    @classmethod
    def choices(cls):
        return [(i.name, i.value) for i in cls]


class ApprovedStatus(models.Manager):
    """Manager for filtering by accepted status"""

    def get_queryset(self):
        return super().get_queryset().filter(status=Building.ACCEPTED)


class PendingStatus(models.Manager):
    """Manager for filtering by pending status"""

    def get_queryset(self):
        return super().get_queryset().filter(status=Building.PENDING)


class RejectedStatus(models.Manager):
    """Manager for filtering by rejected status"""

    def get_queryset(self):
        return super().get_queryset().filter(status=Building.REJECTED)


class DraftsForNewBuildings(models.Manager):
    """Manager for filtering Drafts not assigned to a Building yet"""

    def get_queryset(self):
        return super().get_queryset().filter(building__isnull=True)


class BuildingData(models.Model):
    """
    Abstract model which defines the data fields for a building
    """

    PENDING = 0
    ACCEPTED = 1
    REJECTED = -1

    BUILDING_STATUS_CHOICES = [
        (PENDING, _("Pending")),
        (ACCEPTED, _("Accepted")),
        (REJECTED, _("Rejected")),
    ]

    general_id = models.AutoField(_("general id"), primary_key=True)
    risk_category = models.CharField(
        _("risk category"),
        max_length=3,
        choices=SeismicCategoryChoice.choices(),
        default=SeismicCategoryChoice.NA,
        db_index=True,
    )
    registration_number = models.IntegerField(_("registration number"), null=True)
    examination_year = models.IntegerField(_("examination year"), null=True)
    certified_expert = models.CharField(_("certified expert"), max_length=100, null=True)
    observations = models.CharField(_("observations"), max_length=1000, null=True)

    lat = models.FloatField(_("latitude"), null=True)
    lng = models.FloatField(_("longitude"), null=True)

    county = models.CharField(_("county"), max_length=60)
    address = models.CharField(_("address"), max_length=250, null=True)
    street_number = models.CharField(_("street number"), max_length=100)
    locality = models.CharField(_("locality"), max_length=20)

    year_built = models.IntegerField(_("year built"), null=True)
    height_regime = models.CharField(_("height regime"), max_length=50, null=True)
    apartment_count = models.IntegerField(_("apartment count"), null=True)
    surface = models.FloatField(_("surface"), null=True)

    cadastre_number = models.IntegerField(_("cadastre number"), null=True)
    land_registry_number = models.CharField(_("land registry number"), max_length=50, null=True)

    status = models.SmallIntegerField(
        _("status"),
        default=PENDING,
        choices=BUILDING_STATUS_CHOICES,
        db_index=True,
    )
    created_on = models.DateTimeField(_("created on"), default=timezone.now, blank=True)

    objects = models.Manager()
    approved = ApprovedStatus()
    pending = PendingStatus()
    rejected = RejectedStatus()

    class Meta:
        abstract = True


class Building(BuildingData):
    """
    Current data about a building
    """

    administration_update = models.DateField(_("administration update"), null=True, blank=True)
    admin_update = models.DateField(_("admin update"), null=True, blank=True)

    class Meta:
        verbose_name = _("building")
        verbose_name_plural = _("buildings")

    def __str__(self):
        return self.address


class BuildingDraft(BuildingData):
    """
    New data suggested for a building
    """

    building = models.ForeignKey(Building, null=True, on_delete=models.CASCADE)

    for_new_buildings = DraftsForNewBuildings()

    class Meta:
        verbose_name = _("building draft")
        verbose_name_plural = _("building drafts")

    def __str__(self):
        return self.address


class Statistic(models.Model):
    people_under_risk = models.IntegerField(_("people under risk"), null=True)
    consolidated_buildings = models.IntegerField(_("consolidated buildings"), null=True)

    class Meta:
        verbose_name = _("statistic")
        verbose_name_plural = _("statistics")

    def __str__(self):
        return "Statistics"


class BuildingResource(resources.ModelResource):
    class Meta:
        DATE_FORMAT = {"format": "%d.%m.%Y"}

        model = Building
        exclude = ("id",)
        import_id_fields = ("general_id",)

        widgets = {
            "administration_update": DATE_FORMAT,
            "admin_update": DATE_FORMAT,
        }

        verbose_name = _("building resource")
        verbose_name_plural = _("building resources")


class CsvFile(models.Model):
    NOT_TRIED = 0
    SUCCESS = 1
    FAILURE = -1

    DATA_FILE_STATUS_CHOICES = [
        (NOT_TRIED, _("Not tried")),
        (SUCCESS, _("Imported successfully")),
        (FAILURE, _("Import failed")),
    ]

    name = models.CharField(_("name"), max_length=255)
    file = models.FileField(_("file"))
    status = models.SmallIntegerField(_("status"), default=0, editable=False, choices=DATA_FILE_STATUS_CHOICES)

    class Meta:
        verbose_name = _("CSV file")
        verbose_name_plural = _("CSV files")

    def __str__(self):
        return self.name
