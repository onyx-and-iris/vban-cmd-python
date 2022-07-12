# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Before any major/minor/patch bump all unit tests will be run to verify they pass.

## [Unreleased]

-   [ ] Create a stable branch.

## [0.3.0] - 2022-04

### Added

-   strip_levels, bus_levels property objects added to base class. These now return the full level array.
-   filter out empty values from strip_levels/bus_levels
-   script decorator added to sendtext() in base class. Now supports passing a nested dict, similar to apply()
-   pre-commit.ps1 added for use with git hook. test badges added to readme.
-   genbadge added to development dependencies in setup.py
-   Lower tests added.

### Changed

-   mc getter implemented in strip class
-   bus modes meta function reworked.
-   sendtext() now for multi set operationis (used by apply() method)
-   tests now run according to a kind, for a single run version is random.
-   now using psuedo decorator functions cache_bool and cache_string to handle caching.
-   meta functions reworked.
-   strip bool props moved into factory function.

### Fixed

-   fixed size of recvfrom buffer for self.rt_packet_socket in base class
-   nose tests migrated to pytest as nose will not be supported in python 3.10+
-   sendtext() removed from readme. Still in interface but not advised to use since it doesn't update cache.

## [0.2.0] - 2022-03-29

### Added

-   profiles module
-   example profiles added to \_profiles/ directory.

### Changed

-   setup/teardown moved into login()/logout() functions in base class.
-   now using black formatter, code style badge added to readme.

### Fixed

-   bus/strip labels split at null terminator in ascii string.
-   all gainlayers added to isdirty() function in VBAN_VMRT_Packet_Data

## [0.1.0] - 2022-03-21

### Added

-   gain property added to strip class.
-   added worker2 thread for keeping the public packet constantly updated in the background.
-   self.running flag for notifying threads when to stop.
-   docstrings added to base class.
-   apply() added to base class and strip/bus classes. supports setting parameters through dict.
-   bus modes mixin added to bus class
-   isdirty() added to VBAN_VMRT_Packet_Data for precisely defining the dirty parameter.

### Changed

-   underscore removed from package name. https://peps.python.org/pep-0008/#package-and-module-names
-   readme updated to reflect changes.
-   boolean strip/bus properties now defined by meta functions.

### Fixed

-   fixed kind map ins, outs order. (causing error with basic version)

## [0.0.1] - 2022-02

### Added

-   Create the base class, setup entry point to interface.
-   worker thread added to keep interface registered to the rt packet service
-   Added definitions for rt packet data and the various packet headers, as dataclasses.
-   Property objects in data packet dataclass for returning byte tuples/parsing string params.
-   Adding kinds module for mapping each Voicemeeter version to a namedtuple.
-   Added meta module.
-   Strip/Bus modules added.
-   Modes dataclass for defining strip states through bit modes.
-   GainLayer added to strip module. gainlayer properties added as mixin.
-   Higher unit tests added.
-   show(), hide(), shutdown() and restart() added to base class.
-   Add initial version of readme.
-   add property objects sr, nbc and streamname to TextRequestHeader. Now settable by kwargs.
