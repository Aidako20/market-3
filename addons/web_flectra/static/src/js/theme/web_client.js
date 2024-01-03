/** @flectra-module **/

import { WebClient } from "@web/webclient/webclient";
import { SideBar } from "@web_flectra/js/sidebar";
const { HomeMenu } = '@web_flectra/js/theme/home_menu';
const { onMounted } = owl;
import { mount } from "@flectra/owl";
import { useBus, useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";

patch(WebClient.prototype , {
    
    setup() {
        var self = this;
        super.setup(...arguments);
        this.rpc = useService("rpc");
        this.previous_url = false;
        const originalEvent = this.menuService.setCurrentMenu;
        this.menuService.setCurrentMenu = (menu) => {
            originalEvent.apply(this.menuService, [menu]);
            self.resetSidebarMenu(menu.actionID)
        }
        
        useBus(this.env.bus,"home_menu_toggled", (toggle) => {
            this.toggleHomeMenu(toggle)
        });
        useBus(this.env.bus, "home_menu_selected", (menu) => {
            console.log('on selected')
            this.homeMenuSelected(menu)
        });
        onMounted(() => {

            this.env.bus.addEventListener("reset_side_menu", (actionID) => {
                this.resetSidebarMenu(actionID);
            });
            this.resetSidebarMenu();
        });
    },

    async resetSidebarMenu(actionID=false) {
        if(!$('.oe_application_menu_placeholder').length) { return; }
        const current = this.router.current;
        if(actionID && actionID != current.hash.action){
            setTimeout(() => {
                this.resetSidebarMenu(actionID);
                return;
            }, 500);
            return;
        }
        var app = {
            'menuID': current.hash.menu_id,
            'actionID': current.hash.action
        }
        if(this.sideBar){
            await this.sideBar.reset_menu();
            await this.sideBar.open_menu(app.menuID);
            await this.sideBar.set_menu(app);
        } else {
            this.sideBar = await mount(SideBar, $('.oe_application_menu_placeholder')[0], {
                env: this.env,
                props: {
                    menu: app
                }
            });
        }

        $('#menu_launcher').removeClass('d-none');
    },

    toggleHomeMenu(toggle) {
        //this.previous_url = $.bbq.getState();
        this.env.bus.trigger('set_prev_url', this.router.current.hash);
        this.actionService.doAction('apps_menu', {});
    },

    async homeMenuSelected(menu) {
        await this.menuService.selectMenu(menu.detail);
    },

    _loadDefaultApp() {
        this.actionService.doAction('apps_menu', {});
    },
});
WebClient.components = { ...WebClient.components, HomeMenu };