flectra.define('website.editor.link',function(require){
'usestrict';

varweWidgets=require('wysiwyg.widgets');
varwUtils=require('website.utils');

weWidgets.LinkDialog.include({
    xmlDependencies:(weWidgets.LinkDialog.prototype.xmlDependencies||[]).concat(
        ['/website/static/src/xml/website.editor.xml']
    ),
    events:_.extend({},weWidgets.LinkDialog.prototype.events||{},{
        'changeselect[name="link_anchor"]':'_onAnchorChange',
        'inputinput[name="url"]':'_onURLInput',
    }),
    custom_events:_.extend({},weWidgets.LinkDialog.prototype.custom_events||{},{
        website_url_chosen:'_onAutocompleteClose',
    }),
    LINK_DEBOUNCE:1000,

    /**
     *@constructor
     */
    init:function(){
        this._super.apply(this,arguments);
        this._adaptPageAnchor=_.debounce(this._adaptPageAnchor,this.LINK_DEBOUNCE);
    },
    /**
     *AllowstheURLinputtoproposeexistingwebsitepages.
     *
     *@override
     */
    start:function(){
        vardef=this._super.apply(this,arguments);
        wUtils.autocompleteWithPages(this,this.$('input[name="url"]'));
        this.opened(this._adaptPageAnchor.bind(this));
        returndef;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _adaptPageAnchor:function(){
        varurlInputValue=this.$('input[name="url"]').val();
        var$pageAnchor=this.$('.o_link_dialog_page_anchor');
        if(!$pageAnchor.length){
            return;
        }
        varisFromWebsite=urlInputValue[0]==='/';
        var$selectMenu=this.$('select[name="link_anchor"]');
        var$anchorsLoading=this.$('.o_anchors_loading');

        if($selectMenu.data("anchor-for")!==urlInputValue){//avoiduselessquery
            $anchorsLoading.removeClass('d-none');
            $pageAnchor.toggleClass('d-none',!isFromWebsite);
            $selectMenu.empty();
            consturlWithoutHash=urlInputValue.split("#")[0];
            wUtils.loadAnchors(urlWithoutHash).then(function(anchors){
                _.each(anchors,function(anchor){
                    $selectMenu.append($('<option>',{text:anchor}));
                });
                always();
            }).guardedCatch(always);
        }else{
            always();
        }

        functionalways(){
            $anchorsLoading.addClass('d-none');
            constanchor=`#${urlInputValue.split('#')[1]}`;
            letanchorIndex=-1;
            if(anchor){
                constoptionEls=$selectMenu[0].querySelectorAll('option');
                anchorIndex=Array.from(optionEls).findIndex(el=>el.textContent===anchor);
            }
            $selectMenu.prop("selectedIndex",anchorIndex);
        }
        $selectMenu.data("anchor-for",urlInputValue);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onAutocompleteClose:function(){
        this._onURLInput();
    },
    /**
     *@private
     */
    _onAnchorChange:function(){
        varanchorValue=this.$('[name="link_anchor"]').val();
        var$urlInput=this.$('[name="url"]');
        varurlInputValue=$urlInput.val();
        if(urlInputValue.indexOf('#')>-1){
            urlInputValue=urlInputValue.substr(0,urlInputValue.indexOf('#'));
        }
        $urlInput.val(urlInputValue+anchorValue);
    },
    /**
     *@override
     */
    _onURLInput:function(){
        this._super.apply(this,arguments);
        this._adaptPageAnchor();
    },
});
});
