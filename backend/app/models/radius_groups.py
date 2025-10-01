"""Deprecated: legacy duplicate RADIUS group & pool models.

All models previously defined here were consolidated:
  * GroupCheck, GroupReply, RadPostAuth -> backend.app.models.radius
  * NasReload, RadIpPool -> backend.app.models.nas

This stub remains temporarily to avoid breaking imports during
the refactor window. New code must not import from this module.

Safe to remove once all imports to `radius_groups` are eliminated.
"""

__all__: list[str] = []
