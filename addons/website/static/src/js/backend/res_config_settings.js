flectra.define('website.settings',function(require){

constBaseSettingController=require('base.settings').Controller;
constcore=require('web.core');
constDialog=require('web.Dialog');
constFieldBoolean=require('web.basic_fields').FieldBoolean;
constfieldRegistry=require('web.field_registry');
constFormController=require('web.FormController');

constQWeb=core.qweb;
const_t=core._t;

BaseSettingController.include({

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Bypassesthediscardconfirmationdialogwhengoingtoawebsitebecause
     *thetargetwebsitewillbetheoneselectedandwhenselectingatheme
     *becausethethemewillbeinstalledontheselectedwebsite.
     *
     *Withoutthisoverride,itisimpossibletogotoawebsiteotherthanthe
     *firstbecausediscardingwillrevertitbacktothedefaultvalue.
     *
     *Withoutthisoverride,itisimpossibletoeditrobots.txtwebsiteotherthanthe
     *firstbecausediscardingwillrevertitbacktothedefaultvalue.
     *
     *Withoutthisoverride,itisimpossibletosubmitsitemaptogoogleotherthanforthe
     *firstwebsitebecausediscardingwillrevertitbacktothedefaultvalue.
     *
     *Withoutthisoverride,itisimpossibletoinstallathemeonawebsite
     *otherthanthefirstbecausediscardingwillrevertitbacktothe
     *defaultvalue.
     *
     *@override
     */
    _onButtonClicked:function(ev){
        if(ev.data.attrs.name==='website_go_to'
                ||ev.data.attrs.name==='action_open_robots'
                ||ev.data.attrs.name==='action_ping_sitemap'
                ||ev.data.attrs.name==='install_theme_on_current_website'){
            FormController.prototype._onButtonClicked.apply(this,arguments);
        }else{
            this._super.apply(this,arguments);
        }
    },
});

constWebsiteCookiesbarField=FieldBoolean.extend({
    xmlDependencies:['/website/static/src/xml/website.res_config_settings.xml'],

    _onChange:function(){
        constchecked=this.$input[0].checked;
        if(!checked){
            returnthis._setValue(checked);
        }

        constcancelCallback=()=>this.$input[0].checked=!checked;
        Dialog.confirm(this,null,{
            title:_t("Pleaseconfirm"),
            $content:QWeb.render('website.res_config_settings.cookies_modal_main'),
            buttons:[{
                text:_t('Donotactivate'),
                classes:'btn-primary',
                close:true,
                click:cancelCallback,
            },
            {
                text:_t('Activateanyway'),
                close:true,
                click:()=>this._setValue(checked),
            }],
            cancel_callback:cancelCallback,
        });
    },
});

fieldRegistry.add('website_cookiesbar_field',WebsiteCookiesbarField);
});
