/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { useInputField } from "@web/views/fields/input_field_hook";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

export class ClipboardUrlField extends Component {
  static template = "kzm_gitlab_integration.ClipboardUrlField";
  static props = {
    ...standardFieldProps,
    placeholder: { type: String, optional: true },
    text: { type: String, optional: true },
    websitePath: { type: Boolean, optional: true },
  };

  setup() {
    useInputField({ getValue: () => this.value });
    this.notificationService = useService("notification");
  }

  get value() {
    return this.props.record.data[this.props.name] || "";
  }

  get formattedHref() {
    let value = this.props.record.data[this.props.name];
    if (value && !this.props.websitePath) {
      // If not a website path, add http:// prefix if missing.
      const regex = /^((ftp|http)s?:\/)?\//i;
      value = !regex.test(value) ? `http://${value}` : value;
    }
    return value;
  }

  onClick(ev) {
    // Prevent default link navigation.
    ev.preventDefault();
    const url = this.formattedHref;
    if (!url) return;
    if (navigator.clipboard) {
      navigator.clipboard
        .writeText(url)
        .then(() => {
          this.notificationService.add(_t("Url copied to clipboard"), {
            type: "success",
          });
        })
        .catch((err) => {
          this.notificationService.add(_t("Url copied to clipboard"), {
            type: "danger",
          });
        });
    } else {
      // Fallback for older browsers:
      const textarea = document.createElement("textarea");
      textarea.value = url;
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand("copy");
        this.notificationService.add(
          _t("You cannot delete an accepted offer."),
          {
            type: "success",
          }
        );
      } catch (err) {
        this.notificationService.add(_t("Failed to copy url to clipboard"), {
          type: "danger",
        });
      }
      document.body.removeChild(textarea);
    }
  }
}

export const clipboardUrlField = {
  component: ClipboardUrlField,
  displayName: _t("Clipboard URL"),
  supportedOptions: [
    {
      label: _t("Is a website path"),
      name: "website_path",
      type: "boolean",
      help: _t(
        "If True, the url will be used as it is, without any prefix added to it."
      ),
    },
  ],
  supportedTypes: ["char"],
  extractProps: ({ attrs, options }) => ({
    text: attrs.text,
    websitePath: options.website_path,
    placeholder: attrs.placeholder,
  }),
};

registry.category("fields").add("clipboard_url", clipboardUrlField);
