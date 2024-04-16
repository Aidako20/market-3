flectra.define('website.translateMenu',function(require){
'usestrict';

varutils=require('web.utils');
varTranslatorMenu=require('website.editor.menu.translate');
varwebsiteNavbarData=require('website.navbar');

varTranslatePageMenu=websiteNavbarData.WebsiteNavbarActionWidget.extend({
    assetLibs:['web_editor.compiled_assets_wysiwyg','website.compiled_assets_wysiwyg'],

    actions:_.extend({},websiteNavbarData.WebsiteNavbar.prototype.actions||{},{
        edit_master:'_goToMasterPage',
        translate:'_startTranslateMode',
    }),

    /**
     *@override
     */
    start:function(){
        varcontext;
        this.trigger_up('context_get',{
            extra:true,
            callback:function(ctx){
                context=ctx;
            },
        });
        this._mustEditTranslations=context.edit_translations;
        if(this._mustEditTranslations){
            varurl=window.location.href.replace(/([?&])&*edit_translations[^&#]*&?/,'\$1');
            window.history.replaceState({},null,url);

            this._startTranslateMode();
        }
        returnthis._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Actions
    //--------------------------------------------------------------------------

    /**
     *Redirectstheusertothesamepagebutintheoriginallanguageandin
     *editmode.
     *
     *@private
     *@returns{Promise}
     */
    _goToMasterPage:function(){
        varcurrent=document.createElement('a');
        current.href=window.location.toString();
        current.search+=(current.search?'&':'?')+'enable_editor=1';
        //weareintranslatemode,thepathnamestartswith'/<url_code/'
        current.pathname=current.pathname.substr(Math.max(0,current.pathname.indexOf('/',1)));

        varlink=document.createElement('a');
        link.href='/website/lang/default';
        link.search+=(link.search?'&':'?')+'r='+encodeURIComponent(current.pathname+current.search+current.hash);

        window.location=link.href;
        returnnewPromise(function(){});
    },
    /**
     *Redirectstheusertothesamepageintranslationmode(orstartthe
     *translatoristranslationmodeisalreadyenabled).
     *
     *@private
     *@returns{Promise}
     */
    _startTranslateMode:function(){
        if(!this._mustEditTranslations){
            window.location.search+='&edit_translations';
            returnnewPromise(function(){});
        }

        vartranslator=newTranslatorMenu(this);

        //Wedon'twanttheBSdropdowntoclose
        //whenclickinginaelementtotranslate
        $('.dropdown-menu').on('click','.o_editable',function(ev){
            ev.stopPropagation();
        });

        returntranslator.prependTo(document.body);
    },
});

websiteNavbarData.websiteNavbarRegistry.add(TranslatePageMenu,'.o_menu_systray:has([data-action="translate"])');
});
