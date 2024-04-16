flectra.define('website_links.website_links',function(require){
'usestrict';

varcore=require('web.core');
varpublicWidget=require('web.public.widget');

var_t=core._t;

varSelectBox=publicWidget.Widget.extend({
    events:{
        'change':'_onChange',
    },

    /**
     *@constructor
     *@param{Object}parent
     *@param{Object}obj
     *@param{String}placeholder
     */
    init:function(parent,obj,placeholder){
        this._super.apply(this,arguments);
        this.obj=obj;
        this.placeholder=placeholder;
    },
    /**
     *@override
     */
    willStart:function(){
        varself=this;
        vardefs=[this._super.apply(this,arguments)];
        defs.push(this._rpc({
            model:this.obj,
            method:'search_read',
            params:{
                fields:['id','name'],
            },
        }).then(function(result){
            self.objects=_.map(result,function(val){
                return{id:val.id,text:val.name};
            });
        }));
        returnPromise.all(defs);
    },
    /**
     *@override
     */
    start:function(){
        varself=this;
        this.$el.select2({
            placeholder:self.placeholder,
            allowClear:true,
            createSearchChoice:function(term){
                if(self._objectExists(term)){
                    returnnull;
                }
                return{id:term,text:_.str.sprintf("Create'%s'",term)};
            },
            createSearchChoicePosition:'bottom',
            multiple:false,
            data:self.objects,
            minimumInputLength:self.objects.length>100?3:0,
        });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{String}query
     */
    _objectExists:function(query){
        return_.find(this.objects,function(val){
            returnval.text.toLowerCase()===query.toLowerCase();
        })!==undefined;
    },
    /**
     *@private
     *@param{String}name
     */
    _createObject:function(name){
        varself=this;
        varargs={
            name:name
        };
        if(this.obj==="utm.campaign"){
            args.is_website=true;
        }
        returnthis._rpc({
            model:this.obj,
            method:'create',
            args:[args],
        }).then(function(record){
            self.$el.attr('value',record);
            self.objects.push({'id':record,'text':name});
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Object}ev
     */
    _onChange:function(ev){
        if(!ev.added||!_.isString(ev.added.id)){
            return;
        }
        this._createObject(ev.added.id);
    },
});

varRecentLinkBox=publicWidget.Widget.extend({
    template:'website_links.RecentLink',
    xmlDependencies:['/website_links/static/src/xml/recent_link.xml'],
    events:{
        'click.btn_shorten_url_clipboard':'_toggleCopyButton',
        'click.o_website_links_edit_code':'_editCode',
        'click.o_website_links_ok_edit':'_onLinksOkClick',
        'click.o_website_links_cancel_edit':'_onLinksCancelClick',
        'submit#o_website_links_edit_code_form':'_onSubmitCode',
    },

    /**
     *@constructor
     *@param{Object}parent
     *@param{Object}obj
     */
    init:function(parent,obj){
        this._super.apply(this,arguments);
        this.link_obj=obj;
        this.animating_copy=false;
    },
    /**
     *@override
     */
    start:function(){
        newClipboardJS(this.$('.btn_shorten_url_clipboard').get(0));
        returnthis._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _toggleCopyButton:function(){
        if(this.animating_copy){
            return;
        }

        varself=this;
        this.animating_copy=true;
        vartop=this.$('.o_website_links_short_url').position().top;
        this.$('.o_website_links_short_url').clone()
            .css('position','absolute')
            .css('left',15)
            .css('top',top-2)
            .css('z-index',2)
            .removeClass('o_website_links_short_url')
            .addClass('animated-link')
            .insertAfter(this.$('.o_website_links_short_url'))
            .animate({
                opacity:0,
                top:'-=20',
            },500,function(){
                self.$('.animated-link').remove();
                self.animating_copy=false;
            });
    },
    /**
     *@private
     *@param{String}message
     */
    _notification:function(message){
        this.$('.notification').append('<strong>'+message+'</strong>');
    },
    /**
     *@private
     */
    _editCode:function(){
        varinitCode=this.$('#o_website_links_code').html();
        this.$('#o_website_links_code').html('<formstyle="display:inline;"id="o_website_links_edit_code_form"><inputtype="hidden"id="init_code"value="'+initCode+'"/><inputtype="text"id="new_code"value="'+initCode+'"/></form>');
        this.$('.o_website_links_edit_code').hide();
        this.$('.copy-to-clipboard').hide();
        this.$('.o_website_links_edit_tools').show();
    },
    /**
     *@private
     */
    _cancelEdit:function(){
        this.$('.o_website_links_edit_code').show();
        this.$('.copy-to-clipboard').show();
        this.$('.o_website_links_edit_tools').hide();
        this.$('.o_website_links_code_error').hide();

        varoldCode=this.$('#o_website_links_edit_code_form#init_code').val();
        this.$('#o_website_links_code').html(oldCode);

        this.$('#code-error').remove();
        this.$('#o_website_links_codeform').remove();
    },
    /**
     *@private
     */
    _submitCode:function(){
        varself=this;

        varinitCode=this.$('#o_website_links_edit_code_form#init_code').val();
        varnewCode=this.$('#o_website_links_edit_code_form#new_code').val();

        if(newCode===''){
            self.$('.o_website_links_code_error').html(_t("Thecodecannotbeleftempty"));
            self.$('.o_website_links_code_error').show();
            return;
        }

        functionshowNewCode(newCode){
            self.$('.o_website_links_code_error').html('');
            self.$('.o_website_links_code_error').hide();

            self.$('#o_website_links_codeform').remove();

            //Shownewcode
            varhost=self.$('#o_website_links_host').html();
            self.$('#o_website_links_code').html(newCode);

            //Updatebuttoncopytoclipboard
            self.$('.btn_shorten_url_clipboard').attr('data-clipboard-text',host+newCode);

            //Showactionagain
            self.$('.o_website_links_edit_code').show();
            self.$('.copy-to-clipboard').show();
            self.$('.o_website_links_edit_tools').hide();
        }

        if(initCode===newCode){
            showNewCode(newCode);
        }else{
            this._rpc({
                route:'/website_links/add_code',
                params:{
                    init_code:initCode,
                    new_code:newCode,
                },
            }).then(function(result){
                showNewCode(result[0].code);
            },function(){
                self.$('.o_website_links_code_error').show();
                self.$('.o_website_links_code_error').html(_t("Thiscodeisalreadytaken"));
            });
        }
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Event}ev
     */
    _onLinksOkClick:function(ev){
        ev.preventDefault();
        this._submitCode();
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onLinksCancelClick:function(ev){
        ev.preventDefault();
        this._cancelEdit();
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onSubmitCode:function(ev){
        ev.preventDefault();
        this._submitCode();
    },
});

varRecentLinks=publicWidget.Widget.extend({

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    getRecentLinks:function(filter){
        varself=this;
        returnthis._rpc({
            route:'/website_links/recent_links',
            params:{
                filter:filter,
                limit:20,
            },
        }).then(function(result){
            _.each(result.reverse(),function(link){
                self._addLink(link);
            });
            self._updateNotification();
        },function(){
            varmessage=_t("Unabletogetrecentlinks");
            self.$el.append('<divclass="alertalert-danger">'+message+'</div>');
        });
    },
    /**
     *@private
     */
    _addLink:function(link){
        varnbLinks=this.getChildren().length;
        varrecentLinkBox=newRecentLinkBox(this,link);
        recentLinkBox.prependTo(this.$el);
        $('.link-tooltip').tooltip();

        if(nbLinks===0){
            this._updateNotification();
        }
    },
    /**
     *@private
     */
    removeLinks:function(){
        _.invoke(this.getChildren(),'destroy');
    },
    /**
     *@private
     */
    _updateNotification:function(){
        if(this.getChildren().length===0){
            varmessage=_t("Youdon'thaveanyrecentlinks.");
            $('.o_website_links_recent_links_notification').html('<divclass="alertalert-info">'+message+'</div>');
        }else{
            $('.o_website_links_recent_links_notification').empty();
        }
    },
});

publicWidget.registry.websiteLinks=publicWidget.Widget.extend({
    selector:'.o_website_links_create_tracked_url',
    events:{
        'click#filter-newest-links':'_onFilterNewestLinksClick',
        'click#filter-most-clicked-links':'_onFilterMostClickedLinksClick',
        'click#filter-recently-used-links':'_onFilterRecentlyUsedLinksClick',
        'click#generated_tracked_linka':'_onGeneratedTrackedLinkClick',
        'keyup#url':'_onUrlKeyUp',
        'click#btn_shorten_url':'_onShortenUrlButtonClick',
        'submit#o_website_links_link_tracker_form':'_onFormSubmit',
    },

    /**
     *@override
     */
    start:function(){
        vardefs=[this._super.apply(this,arguments)];

        //UTMSselectswidgets
        varcampaignSelect=newSelectBox(this,'utm.campaign',_t("e.g.PromotionofJune,WinterNewsletter,.."));
        defs.push(campaignSelect.attachTo($('#campaign-select')));

        varmediumSelect=newSelectBox(this,'utm.medium',_t("e.g.Newsletter,SocialNetwork,.."));
        defs.push(mediumSelect.attachTo($('#channel-select')));

        varsourceSelect=newSelectBox(this,'utm.source',_t("e.g.SearchEngine,Websitepage,.."));
        defs.push(sourceSelect.attachTo($('#source-select')));

        //RecentLinksWidgets
        this.recentLinks=newRecentLinks(this);
        defs.push(this.recentLinks.appendTo($('#o_website_links_recent_links')));
        this.recentLinks.getRecentLinks('newest');

        //ClipboardLibrary
        newClipboardJS($('#btn_shorten_url').get(0));

        this.url_copy_animating=false;

        $('[data-toggle="tooltip"]').tooltip();

        returnPromise.all(defs);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onFilterNewestLinksClick:function(){
        this.recentLinks.removeLinks();
        this.recentLinks.getRecentLinks('newest');
    },
    /**
     *@private
     */
    _onFilterMostClickedLinksClick:function(){
        this.recentLinks.removeLinks();
        this.recentLinks.getRecentLinks('most-clicked');
    },
    /**
     *@private
     */
    _onFilterRecentlyUsedLinksClick:function(){
        this.recentLinks.removeLinks();
        this.recentLinks.getRecentLinks('recently-used');
    },
    /**
     *@private
     */
    _onGeneratedTrackedLinkClick:function(){
        $('#generated_tracked_linka').text(_t("Copied")).removeClass('btn-primary').addClass('btn-success');
        setTimeout(function(){
            $('#generated_tracked_linka').text(_t("Copy")).removeClass('btn-success').addClass('btn-primary');
        },5000);
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onUrlKeyUp:function(ev){
        if(!$('#btn_shorten_url').hasClass('btn-copy')||ev.which===13){
            return;
        }

        $('#btn_shorten_url').removeClass('btn-successbtn-copy').addClass('btn-primary').html('Gettrackedlink');
        $('#generated_tracked_link').css('display','none');
        $('.o_website_links_utm_forms').show();
    },
    /**
     *@private
     */
    _onShortenUrlButtonClick:function(){
        if(!$('#btn_shorten_url').hasClass('btn-copy')||this.url_copy_animating){
            return;
        }

        varself=this;
        this.url_copy_animating=true;
        $('#generated_tracked_link').clone()
            .css('position','absolute')
            .css('left','78px')
            .css('bottom','8px')
            .css('z-index',2)
            .removeClass('#generated_tracked_link')
            .addClass('url-animated-link')
            .appendTo($('#generated_tracked_link'))
            .animate({
                opacity:0,
                bottom:'+=20',
            },500,function(){
                $('.url-animated-link').remove();
                self.url_copy_animating=false;
            });
    },
    /**
     *AddtheRecentLinkBoxwidgetandsendtheformwhentheusergeneratethelink
     *
     *@private
     *@param{Event}ev
     */
    _onFormSubmit:function(ev){
        varself=this;
        ev.preventDefault();

        if($('#btn_shorten_url').hasClass('btn-copy')){
            return;
        }

        ev.stopPropagation();

        //GetURLandUTMs
        varcampaignID=$('#campaign-select').attr('value');
        varmediumID=$('#channel-select').attr('value');
        varsourceID=$('#source-select').attr('value');

        varparams={};
        params.url=$('#url').val();
        if(campaignID!==''){
            params.campaign_id=parseInt(campaignID);
        }
        if(mediumID!==''){
            params.medium_id=parseInt(mediumID);
        }
        if(sourceID!==''){
            params.source_id=parseInt(sourceID);
        }

        $('#btn_shorten_url').text(_t("Generatinglink..."));

        this._rpc({
            route:'/website_links/new',
            params:params,
        }).then(function(result){
            if('error'inresult){
                //Handleerrors
                if(result.error==='empty_url'){
                    $('.notification').html('<divclass="alertalert-danger">TheURLisempty.</div>');
                }elseif(result.error==='url_not_found'){
                    $('.notification').html('<divclass="alertalert-danger">URLnotfound(404)</div>');
                }else{
                    $('.notification').html('<divclass="alertalert-danger">Anerroroccurwhiletryingtogenerateyourlink.Tryagainlater.</div>');
                }
            }else{
                //Linkgenerated,cleantheformandshowthelink
                varlink=result[0];

                $('#btn_shorten_url').removeClass('btn-primary').addClass('btn-successbtn-copy').html('Copy');
                $('#btn_shorten_url').attr('data-clipboard-text',link.short_url);

                $('.notification').html('');
                $('#generated_tracked_link').html(link.short_url);
                $('#generated_tracked_link').css('display','inline');

                self.recentLinks._addLink(link);

                //CleanURLandUTMselects
                $('#campaign-select').select2('val','');
                $('#channel-select').select2('val','');
                $('#source-select').select2('val','');

                $('.o_website_links_utm_forms').hide();
            }
        });
    },
});

return{
    SelectBox:SelectBox,
    RecentLinkBox:RecentLinkBox,
    RecentLinks:RecentLinks,
};
});
