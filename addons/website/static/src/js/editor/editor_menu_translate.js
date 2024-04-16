flectra.define('website.editor.menu.translate',function(require){
'usestrict';

require('web.dom_ready');
varcore=require('web.core');
varDialog=require('web.Dialog');
varlocalStorage=require('web.local_storage');
varWysiwyg=require('web_editor.wysiwyg.root');
varEditorMenu=require('website.editor.menu');

var_t=core._t;

varlocalStorageNoDialogKey='website_translator_nodialog';

varTranslatorInfoDialog=Dialog.extend({
    template:'website.TranslatorInfoDialog',
    xmlDependencies:Dialog.prototype.xmlDependencies.concat(
        ['/website/static/src/xml/translator.xml']
    ),

    /**
     *@constructor
     */
    init:function(parent,options){
        this._super(parent,_.extend({
            title:_t("TranslationInfo"),
            buttons:[
                {text:_t("Ok,nevershowmethisagain"),classes:'btn-primary',close:true,click:this._onStrongOk.bind(this)},
                {text:_t("Ok"),close:true}
            ],
        },options||{}));
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Calledwhenthe"strong"okisclicked->adaptlocalstoragetomakesure
     *thedialogisneverdisplayedagain.
     *
     *@private
     */
    _onStrongOk:function(){
        localStorage.setItem(localStorageNoDialogKey,true);
    },
});

varWysiwygTranslate=Wysiwyg.extend({
    assetLibs:Wysiwyg.prototype.assetLibs.concat(['website.compiled_assets_wysiwyg']),
    _getWysiwygContructor:function(){
        returnflectra.__DEBUG__.services['web_editor.wysiwyg.multizone.translate'];
    }
});

varTranslatorMenu=EditorMenu.extend({

    /**
     *@override
     */
    start:function(){
        if(!localStorage.getItem(localStorageNoDialogKey)){
            newTranslatorInfoDialog(this).open();
        }

        returnthis._super();
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Returnstheeditableareasonthepage.
     *
     *@param{DOM}$wrapwrap
     *@returns{jQuery}
     */
    editable:function($wrapwrap){
    	varselector='[data-oe-translation-id],'+
        	'[data-oe-model][data-oe-id][data-oe-field],'+
        	'[placeholder*="data-oe-translation-id="],'+
        	'[title*="data-oe-translation-id="],'+
        	'[alt*="data-oe-translation-id="]';
        var$edit=$wrapwrap.find(selector);
        $edit.filter(':has('+selector+')').attr('data-oe-readonly',true);
        return$edit.not('[data-oe-readonly]');
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _wysiwygInstance:function(){
        varcontext;
        this.trigger_up('context_get',{
            callback:function(ctx){
                context=ctx;
            },
        });
        returnnewWysiwygTranslate(this,{lang:context.lang});
    },
});

returnTranslatorMenu;
});
