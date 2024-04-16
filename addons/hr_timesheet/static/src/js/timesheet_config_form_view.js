flectra.define('hr_timesheet.res.config.form',function(require){
    "usestrict";

    constcore=require('web.core');
    constconfig=require('web.config');
    constviewRegistry=require('web.view_registry');
    constBaseSetting=require('base.settings');
    
    const_t=core._t;

    constTimesheetConfigQRCodeMixin={
        async_renderView(){
            constself=this;
            awaitthis._super(...arguments);
            constgoogle_url="https://play.google.com/store/apps/details?id=com.flectra.FlectraTimesheets";
            constapple_url="https://apps.apple.com/be/app/awesome-timesheet/id1078657549";
            constaction_desktop={
                name:_t('DownloadourApp'),
                type:'ir.actions.client',
                tag:'timesheet_qr_code_modal',
                target:'new',
            };
            this.$el.find('img.o_config_app_store').on('click',function(event){
                event.preventDefault();
                if(!config.device.isMobile){
                    self.do_action(_.extend(action_desktop,{params:{'url':apple_url}}));
                }else{
                    self.do_action({type:'ir.actions.act_url',url:apple_url});
                }
            });
            this.$el.find('img.o_config_play_store').on('click',function(event){
                event.preventDefault();
                if(!config.device.isMobile){
                    self.do_action(_.extend(action_desktop,{params:{'url':google_url}}));
                }else{
                    self.do_action({type:'ir.actions.act_url',url:google_url});
                }
            });
        },
    };


    varTimesheetConfigFormRenderer=BaseSetting.Renderer.extend(TimesheetConfigQRCodeMixin);
    constBaseSettingView=viewRegistry.get('base_settings');
    varTimesheetConfigFormView=BaseSettingView.extend({
        config:_.extend({},BaseSettingView.prototype.config,{
            Renderer:TimesheetConfigFormRenderer,
        }),
    });

    viewRegistry.add('hr_timesheet_config_form',TimesheetConfigFormView);

    return{TimesheetConfigQRCodeMixin,TimesheetConfigFormRenderer,TimesheetConfigFormView};

});
