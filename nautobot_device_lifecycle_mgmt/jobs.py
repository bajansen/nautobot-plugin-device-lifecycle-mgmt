"""Jobs for the Lifecycle Management plugin."""
from datetime import datetime

from nautobot.dcim.models import Device, InventoryItem
from nautobot.extras.jobs import Job

from nautobot_device_lifecycle_mgmt import choices
from .models import (
    DeviceSoftwareValidationResult,
    InventoryItemSoftwareValidationResult,
)
from .software import DeviceSoftware, InventoryItemSoftware


name = "Device/Software Lifecycle Reporting"  # pylint: disable=invalid-name


class SoftwareValidation(Job):
    """Checks if devices and inventory items run validated software version."""

    name = "Software Validation"
    description = "Validates software version on devices and inventory items."
    read_only = False

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class for the job."""

        commit_default = True

    def test_device_software_validity(self) -> None:
        """Check if software assigned to each device is valid. If no software is assigned return warning message."""
        devices = Device.objects.all()
        job_run_time = datetime.now()

        for device in devices:
            device_software = DeviceSoftware(device)

            validate_obj, _ = DeviceSoftwareValidationResult.objects.get_or_create(device=device)
            validate_obj.is_validated = device_software.validate_software()
            validate_obj.sw_missing = device_software.software is None
            validate_obj.software = device_software.software
            validate_obj.last_run = job_run_time
            validate_obj.run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
            validate_obj.validated_save()
        self.log_success(message=f"Performed validation on: {devices.count()} devices.")

    def test_inventory_item_software_validity(self):
        """Check if software assigned to each inventory item is valid. If no software is assigned return warning message."""
        inventory_items = InventoryItem.objects.all()
        job_run_time = datetime.now()

        for inventoryitem in inventory_items:
            inventoryitem_software = InventoryItemSoftware(inventoryitem)

            validate_obj, _ = InventoryItemSoftwareValidationResult.objects.get_or_create(inventory_item=inventoryitem)
            validate_obj.is_validated = inventoryitem_software.validate_software()
            validate_obj.sw_missing = inventoryitem_software.software is None
            validate_obj.software = inventoryitem_software.software
            validate_obj.last_run = job_run_time
            validate_obj.run_type = choices.ReportRunTypeChoices.REPORT_FULL_RUN
            validate_obj.validated_save()

        self.log_success(message=f"Performed validation on: {inventory_items.count()} inventory items.")


jobs = [SoftwareValidation]
