flectra.define('point_of_sale.DebugManager.Backend',function(require){
    'usestrict';

    const{_t}=require('web.core');
    constDebugManager=require('web.DebugManager.Backend');

    DebugManager.include({
        /**
         *RunstheJS(desktop)tests
         */
        perform_pos_js_tests(){
            this.do_action({
                name:_t('JSTests'),
                target:'new',
                type:'ir.actions.act_url',
                url:'/pos/ui/tests?mod=*',
            });
        },
    });
});
