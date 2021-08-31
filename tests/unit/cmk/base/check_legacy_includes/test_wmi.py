#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest

from cmk.base.check_legacy_includes.wmi import parse_wmi_table, scale_counter, WMITableLegacy


def test_parse_wmi_table() -> None:
    assert parse_wmi_table([
        ["[system_perf]"],
        [
            "AlignmentFixupsPersec", "Caption", "ContextSwitchesPersec", "Description",
            "ExceptionDispatchesPersec", "FileControlBytesPersec", "FileControlOperationsPersec",
            "FileDataOperationsPersec", "FileReadBytesPersec", "FileReadOperationsPersec",
            "FileWriteBytesPersec", "FileWriteOperationsPersec", "FloatingEmulationsPersec",
            "Frequency_Object", "Frequency_PerfTime", "Frequency_Sys100NS", "Name",
            "PercentRegistryQuotaInUse", "PercentRegistryQuotaInUse_Base", "Processes",
            "ProcessorQueueLength", "SystemCallsPersec", "SystemUpTime", "Threads",
            "Timestamp_Object", "Timestamp_PerfTime", "Timestamp_Sys100NS", "WMIStatus"
        ],
        [
            "0", "", "1401782", "", "4545", "43595392", "735572", "304946", "1995552734", "282564",
            "376169774", "22382", "0", "10000000", "10000000", "10000000", "", "142602226",
            "4294967295", "126", "0", "33560181", "132748875394984061", "1151",
            "132748883397166638", "8004422024", "132748631397160000", "OK"
        ],
        ["[computer_system]"],
        [
            "AdminPasswordStatus", "AutomaticManagedPagefile", "AutomaticResetBootOption",
            "AutomaticResetCapability", "BootOptionOnLimit", "BootOptionOnWatchDog",
            "BootROMSupported", "BootStatus", "BootupState", "Caption", "ChassisBootupState",
            "ChassisSKUNumber", "CreationClassName", "CurrentTimeZone", "DaylightInEffect",
            "Description", "DNSHostName", "Domain", "DomainRole", "EnableDaylightSavingsTime",
            "FrontPanelResetStatus", "HypervisorPresent", "InfraredSupported", "InitialLoadInfo",
            "InstallDate", "KeyboardPasswordStatus", "LastLoadInfo", "Manufacturer", "Model",
            "Name", "NameFormat", "NetworkServerModeEnabled", "NumberOfLogicalProcessors",
            "NumberOfProcessors", "OEMLogoBitmap", "OEMStringArray", "PartOfDomain",
            "PauseAfterReset", "PCSystemType", "PCSystemTypeEx", "PowerManagementCapabilities",
            "PowerManagementSupported", "PowerOnPasswordStatus", "PowerState", "PowerSupplyState",
            "PrimaryOwnerContact", "PrimaryOwnerName", "ResetCapability", "ResetCount",
            "ResetLimit", "Roles", "Status", "SupportContactDescription", "SystemFamily",
            "SystemSKUNumber", "SystemStartupDelay", "SystemStartupOptions", "SystemStartupSetting",
            "SystemType", "ThermalState", "TotalPhysicalMemory", "UserName", "WakeUpType",
            "Workgroup", "WMIStatus"
        ],
        [
            "3", "1", "1", "1", "", "", "1", "", "Normal boot", "MSEDGEWIN10", "3", "",
            "Win32_ComputerSystem", "65116", "1", "AT/AT COMPATIBLE", "MSEDGEWIN10", "WORKGROUP",
            "0", "1", "3", "1", "0", "", "", "3", "", "innotek GmbH", "VirtualBox", "MSEDGEWIN10",
            "", "1", "2", "1", "", "<array>", "0", "-1", "2", "2", "", "", "3", "0", "3", "", "",
            "1", "65535", "65535", "<array>", "OK", "", "Virtual Machine", "", "", "", "",
            "x64-based PC", "3", "4294496256", "MSEDGEWIN10\\IEUser", "6", "WORKGROUP", "OK"
        ],
    ]) == {
        "system_perf": WMITableLegacy(
            "system_perf",
            [
                "alignmentfixupspersec", "caption", "contextswitchespersec", "description",
                "exceptiondispatchespersec", "filecontrolbytespersec",
                "filecontroloperationspersec", "filedataoperationspersec", "filereadbytespersec",
                "filereadoperationspersec", "filewritebytespersec", "filewriteoperationspersec",
                "floatingemulationspersec", "frequency_object", "frequency_perftime",
                "frequency_sys100ns", "name", "percentregistryquotainuse",
                "percentregistryquotainuse_base", "processes", "processorqueuelength",
                "systemcallspersec", "systemuptime", "threads", "timestamp_object",
                "timestamp_perftime", "timestamp_sys100ns", "wmistatus"
            ],
            "name",
            None,
            None,
            [
                [
                    "0", "", "1401782", "", "4545", "43595392", "735572", "304946", "1995552734",
                    "282564", "376169774", "22382", "0", "10000000", "10000000", "10000000", "",
                    "142602226", "4294967295", "126", "0", "33560181", "132748875394984061", "1151",
                    "132748883397166638", "8004422024", "132748631397160000", "OK"
                ],
            ],
        ),
        "computer_system": WMITableLegacy(
            "computer_system",
            [
                "adminpasswordstatus", "automaticmanagedpagefile", "automaticresetbootoption",
                "automaticresetcapability", "bootoptiononlimit", "bootoptiononwatchdog",
                "bootromsupported", "bootstatus", "bootupstate", "caption", "chassisbootupstate",
                "chassisskunumber", "creationclassname", "currenttimezone", "daylightineffect",
                "description", "dnshostname", "domain", "domainrole", "enabledaylightsavingstime",
                "frontpanelresetstatus", "hypervisorpresent", "infraredsupported",
                "initialloadinfo", "installdate", "keyboardpasswordstatus", "lastloadinfo",
                "manufacturer", "model", "name", "nameformat", "networkservermodeenabled",
                "numberoflogicalprocessors", "numberofprocessors", "oemlogobitmap",
                "oemstringarray", "partofdomain", "pauseafterreset", "pcsystemtype",
                "pcsystemtypeex", "powermanagementcapabilities", "powermanagementsupported",
                "poweronpasswordstatus", "powerstate", "powersupplystate", "primaryownercontact",
                "primaryownername", "resetcapability", "resetcount", "resetlimit", "roles",
                "status", "supportcontactdescription", "systemfamily", "systemskunumber",
                "systemstartupdelay", "systemstartupoptions", "systemstartupsetting", "systemtype",
                "thermalstate", "totalphysicalmemory", "username", "wakeuptype", "workgroup",
                "wmistatus"
            ],
            "name",
            None,
            None,
            [
                [
                    "3", "1", "1", "1", "", "", "1", "", "Normal boot", "MSEDGEWIN10", "3", "",
                    "Win32_ComputerSystem", "65116", "1", "AT/AT COMPATIBLE", "MSEDGEWIN10",
                    "WORKGROUP", "0", "1", "3", "1", "0", "", "", "3", "", "innotek GmbH",
                    "VirtualBox", "MSEDGEWIN10", "", "1", "2", "1", "", "<array>", "0", "-1", "2",
                    "2", "", "", "3", "0", "3", "", "", "1", "65535", "65535", "<array>", "OK", "",
                    "Virtual Machine", "", "", "", "", "x64-based PC", "3", "4294496256",
                    "MSEDGEWIN10\\IEUser", "6", "WORKGROUP", "OK"
                ],
            ],
        ),
    }


def scale_counter_reference(measure, factor, base):
    # old, inefficient implementation
    # takes ages for the arguments: 18446744073664412644, 1, 15143722
    while (base * factor) < measure:
        base += 1 << 32
    return float(measure) / base


@pytest.mark.parametrize('measure, factor, base', [
    (1, 1, 1),
    (2, 1, 1),
    (3, 2, 1),
    ((1 << 32) - 1, 1, 1),
    (1 + (1 << 32), 1, 1),
    (1844674407, 1, 15143722),
    (1844674407, 2, 15143722),
    (1844674407, 13, 15143727),
    (1844674407366441, 1, 15143722),
])
def test_scale_counter(measure, factor, base):
    assert 1e-15 > abs(
        scale_counter(measure, factor, base) - scale_counter_reference(measure, factor, base))
