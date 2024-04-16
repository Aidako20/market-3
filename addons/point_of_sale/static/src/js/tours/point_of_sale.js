flectra.define('point_of_sale.tour',function(require){
"usestrict";

varcore=require('web.core');
vartour=require('web_tour.tour');

var_t=core._t;

tour.register('point_of_sale_tour',{
    url:"/web",
    rainbowMan:false,
    sequence:45,
},[tour.stepUtils.showAppsMenuItem(),{
    trigger:'.o_app[data-menu-xmlid="point_of_sale.menu_point_root"]',
    content:_t("Readytolaunchyour<b>pointofsale</b>?"),
    width:215,
    position:'right',
    edition:'community'
},{
    trigger:'.o_app[data-menu-xmlid="point_of_sale.menu_point_root"]',
    content:_t("Readytolaunchyour<b>pointofsale</b>?"),
    width:215,
    position:'bottom',
    edition:'enterprise'
},{
    trigger:".o_pos_kanbanbutton.oe_kanban_action_button",
    content:_t("<p>Readytohavealookatthe<b>POSInterface</b>?Let'sstartourfirstsession.</p>"),
    position:"bottom"
}]);

});
