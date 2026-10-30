"""Reconstruction command declarations."""

from .. import (
    catalogue_operations,
    reconstruction_evidence,
    reconstruction_export,
    reconstruction_queue,
    reconstruction_regions,
    reconstruction_reviews,
    reconstruction_stages,
    reconstruction_state,
    reconstruction_views,
    variant_lifecycle,
    variant_operations,
)
from ..command_contracts import direct, method, query

COMMANDS = (
    direct("catalogue.inspect", catalogue_operations.inspect, journal=False),
    direct("catalogue.type.create", catalogue_operations.create_type, journal=False),
    direct("catalogue.type.update", catalogue_operations.update_type, journal=False),
    direct("catalogue.type.remove", catalogue_operations.remove_type, journal=False),
    direct("catalogue.assign", catalogue_operations.assign, journal=False),
    direct("catalogue.assign_many", catalogue_operations.assign_many, journal=False),
    direct("catalogue.collection.set", catalogue_operations.collection, journal=False),
    direct("catalogue.region.set", reconstruction_regions.set_region, journal=False),
    direct("catalogue.region.inspect", reconstruction_regions.inspect, journal=False),
    direct("catalogue.region.remove", reconstruction_regions.remove, journal=False),
    direct("variant.create", variant_operations.create, journal=False),
    direct("variant.enter", variant_operations.select, journal=False),
    direct("variant.leave", variant_operations.select, journal=False),
    direct("variant.inspect", variant_operations.inspect, journal=False),
    direct("variant.checkpoint", variant_operations.checkpoint, journal=False),
    direct("variant.fork", variant_operations.fork, journal=False),
    direct("variant.rename", variant_operations.rename, journal=False),
    direct("variant.remove", variant_lifecycle.remove, journal=False),
    direct(
        "reconstruction.evidence.import_file", reconstruction_evidence.import_file, journal=False
    ),
    direct("reconstruction.evidence.inspect", reconstruction_evidence.inspect, journal=False),
    direct("reconstruction.evidence.remove", reconstruction_evidence.remove, journal=False),
    direct("reconstruction.evidence.export", reconstruction_evidence.export, journal=False),
    direct("reconstruction.queue.add", reconstruction_queue.add, journal=False),
    direct("reconstruction.queue.claim", reconstruction_queue.claim, journal=False),
    direct("reconstruction.queue.update", reconstruction_queue.update, journal=False),
    direct("reconstruction.queue.inspect", reconstruction_queue.inspect, journal=False),
    direct("review.set", reconstruction_reviews.decide, journal=False),
    direct("review.inspect", reconstruction_reviews.inspect, journal=False),
    direct("reconstruction.stage.import_mesh", reconstruction_stages.import_mesh, journal=False),
    direct(
        "reconstruction.stage.import_project", reconstruction_stages.import_project, journal=False
    ),
    direct("reconstruction.stage.inspect", reconstruction_stages.inspect, journal=False),
    direct("reconstruction.stage.remove", reconstruction_stages.remove, journal=False),
    direct(
        "catalogue.collection.remove",
        lambda session, id: reconstruction_state.remove(session, "collections", id),
        journal=False,
    ),
    direct("variant.review.prepare", method("variant_review.prepare"), journal=False),
    direct("variant.review.status", method("variant_review.status"), journal=False),
    direct("variant.review.apply", method("variant_review.apply"), journal=False),
    direct("variant.review.cancel", method("variant_review.cancel"), journal=False),
    direct(
        "reconstruction.compare.start", method("reconstruction_comparison.start"), journal=False
    ),
    direct(
        "reconstruction.compare.status", method("reconstruction_comparison.status"), journal=False
    ),
    direct(
        "reconstruction.compare.cancel", method("reconstruction_comparison.cancel"), journal=False
    ),
    query("reconstruction.compare.options", reconstruction_views.options),
    direct("reconstruction.compare.export", reconstruction_export.export, journal=False),
)
