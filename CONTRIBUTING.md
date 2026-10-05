# Contributing

Keep guidance grounded in actual results. Include OS/kernel/loader versions and where a failure happened, but remove serial numbers, partition IDs, account paths, key material, and recovery/enrollment passwords from public reports. Review diagnostic output before posting it.

Distinguish a reference-machine result from a new hardware test. Bootloader and signing changes need artifact inspection and a documented physical verification plan. A unit test or VM cannot prove physical display initialization or long-term stability.

Run `python3 -m unittest discover -s tests -v`. Do not make tests modify the host firmware, installed boot files, package manager, or root signing state. Update recovery instructions when a change introduces a new failure mode. Do not add one-command installers that guess partitions or overwrite trust databases.

Use upstream/distribution sources for binaries. This repository distributes documentation, reference templates, and artwork, not EFI executables or private keys.
