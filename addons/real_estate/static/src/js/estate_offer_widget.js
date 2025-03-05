/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import { _t } from "@web/core/l10n/translation";

/**
 * Keep a reference to the original method so we can call it if allowed.
 */
const originalOnDeleteRecord = ListRenderer.prototype.onDeleteRecord;

/**
 * Patch the ListRenderer's onDeleteRecord to block deletion for records
 * that are "accepted" in estate.property.offer.
 */
patch(ListRenderer.prototype, {
  async onDeleteRecord(record, ev) {
    if (record.model.config.resModel !== "estate.property" || !record.data) {
      return originalOnDeleteRecord.apply(this, arguments);
    }

    if (record.data.status !== "accepted") {
      return originalOnDeleteRecord.apply(this, arguments);
    }

    // @ts-ignore this is a prop in the ListRenderer class
    this.notificationService.add(_t("You cannot delete an accepted offer."), {
      type: "danger",
    });

    return;
  },
});
