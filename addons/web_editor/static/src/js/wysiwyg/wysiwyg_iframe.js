flectra.define('web_editor.wysiwyg.iframe',function(require){
'usestrict';

varWysiwyg=require('web_editor.wysiwyg');
varajax=require('web.ajax');
varcore=require('web.core');
varconfig=require('web.config');

varqweb=core.qweb;
varpromiseCommon;
varpromiseWysiwyg;


/**
 *Addoption(inIframe)toloadWysiwyginaniframe.
 **/
Wysiwyg.include({
    /**
     *AddoptionstoloadWysiwyginaniframe.
     *
     *@override
     *@param{boolean}options.inIframe
     **/
    init:function(parent,options){
        this._super.apply(this,arguments);
        if(this.options.inIframe){
            this._onUpdateIframeId='onLoad_'+this.id;
        }
        this.__extraAssetsForIframe=[];
    },
    /**
     *Loadassetstoinjectintoiframe.
     *
     *@override
     **/
    willStart:function(){
        if(!this.options.inIframe){
            returnthis._super();
        }

        vardefAsset;
        if(this.options.iframeCssAssets){
            defAsset=ajax.loadAsset(this.options.iframeCssAssets);
        }else{
            defAsset=Promise.resolve({
                cssLibs:[],
                cssContents:[]
            });
        }

        promiseWysiwyg=promiseWysiwyg||ajax.loadAsset('web_editor.wysiwyg_iframe_editor_assets');
        this.defAsset=Promise.all([promiseWysiwyg,defAsset]);

        this.$target=this.$el;
        returnthis.defAsset
            .then(this._loadIframe.bind(this))
            .then(this._super.bind(this));
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Createiframe,injectcssandcreatealinkwiththecontent,
     *theninjectthetargetinside.
     *
     *@private
     *@returns{Promise}
     */
    _loadIframe:function(){
        varself=this;
        this.$iframe=$('<iframeclass="wysiwyg_iframe">').css({
            'min-height':'55vh',
            width:'100%'
        });
        varavoidDoubleLoad=0;//thisbugonlyappearsonsomeconfigurations.

        //resolvepromiseonload
        vardef=newPromise(function(resolve){
            window.top[self._onUpdateIframeId]=function(Editor,_avoidDoubleLoad){
                if(_avoidDoubleLoad!==avoidDoubleLoad){
                    console.warn('Wysiwygiframedoubleloaddetected');
                    return;
                }
                deletewindow.top[self._onUpdateIframeId];
                var$iframeTarget=self.$iframe.contents().find('#iframe_target');
                $iframeTarget.attr("isMobile",config.device.isMobile);
                $iframeTarget.find('.o_editable').html(self.$target.val());
                self.options.toolbarHandler=$('#web_editor-top-edit',self.$iframe[0].contentWindow.document);
                $(qweb.render('web_editor.FieldTextHtml.fullscreen'))
                    .appendTo(self.options.toolbarHandler)
                    .on('click','.o_fullscreen',function(){
                        $("body").toggleClass("o_field_widgetTextHtml_fullscreen");
                        varfull=$("body").hasClass("o_field_widgetTextHtml_fullscreen");
                        self.$iframe.parents().toggleClass('o_form_fullscreen_ancestor',full);
                        $(window).trigger("resize");//inducearesize()callandletotherbackendelementsknow(thenavbarextraitemsmanagementreliesonthis)
                    });
                self.Editor=Editor;
                resolve();
            };
        });
        this.$iframe.data('loadDef',def);//forunittest

        //injectcontentiniframe

        this.$iframe.on('load',functiononLoad(ev){
            var_avoidDoubleLoad=++avoidDoubleLoad;
            self.defAsset.then(function(assets){
                if(_avoidDoubleLoad!==avoidDoubleLoad){
                    console.warn('Wysiwygimmediateiframedoubleloaddetected');
                    return;
                }

                variframeContent=qweb.render('wysiwyg.iframeContent',{
                    assets:assets.concat(self.__extraAssetsForIframe),
                    updateIframeId:self._onUpdateIframeId,
                    avoidDoubleLoad:_avoidDoubleLoad
                });
                self.$iframe[0].contentWindow.document
                    .open("text/html","replace")
                    .write(iframeContent);
            });
        });

        this.$iframe.insertAfter(this.$target);

        returndef;
    },
});

});
