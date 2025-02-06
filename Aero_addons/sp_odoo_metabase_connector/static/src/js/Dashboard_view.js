/** @odoo-module */

import { registry } from "@web/core/registry";
const { jsonRpc } = require("web.ajax");


const { Component,onWillStart,useState} = owl;

export class DashboardView extends Component {
    setup() {
         this.state = useState({
            iframeSrc : ""
        });
        let id = this.props.action.params._id;
        if (id){
            onWillStart(async () => {
              let iframe = await jsonRpc('/check/menu/dashboard', 'call', {'menu_id': id });
              if(iframe)
              {
                this.state.iframeSrc = iframe
              }
            });
        }

    }
}
DashboardView.template = "sp_odoo_metabase_connector.dashboard_template";

registry.category('actions').add('sp_odoo_metabase_connector.attached_dashboard_view', DashboardView);
