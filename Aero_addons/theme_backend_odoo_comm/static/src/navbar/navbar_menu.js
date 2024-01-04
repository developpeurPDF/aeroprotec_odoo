/** @odoo-module **/

import { patch } from 'web.utils';
import { NavBar } from "@web/webclient/navbar/navbar";
import {useBus, useService} from "@web/core/utils/hooks";
import {WebClient} from "@web/webclient/webclient";

const {Component, useState, onPatched, onWillPatch} = owl;

patch(WebClient.prototype, "theme_backend_odoo_comm.DefaultAppsMenu", {
    setup() {
        this._super();
        useBus(this.env.bus, "homepage-state-changed", ({detail: state}) => {
            document.body.classList.toggle("o_apps_menu_opened", state);
        });
    },
});

export class HomeMenuApps extends Component {
    setup() {
        super.setup();
        this.state = useState({open: false});
        this.menuService = useService("menu");
        useBus(this.env.bus, "ACTION_MANAGER:UI-UPDATED", () => {
            this._openAppsPage(false, false);
        });
    }

    _openAppsPage(open_state) {
        this.state.open = open_state;
        this.env.bus.trigger("homepage-state-changed", open_state);
    }

}

patch(NavBar.prototype, 'theme_backend_odoo_comm/static/src/navbar/navbar_menu.js', {
   
    getWebIconData(menu) {
        var result = "";
        if (menu.webIconData) {
            const prefix = menu.webIconData.startsWith("P")
                ? "data:image/svg+xml;base64,"
                : "data:image/png;base64,";
            result = menu.webIconData.startsWith("data:image")
                ? menu.webIconData
                : prefix + menu.webIconData.replace(/\s/g, "");
        }
        return result;
    }
            
});
HomeMenuApps.template = "theme_backend_odoo_comm.HomeMenuApps";
Object.assign(NavBar.components, {HomeMenuApps});