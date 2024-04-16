flectra.define('website_forum.website_forum',function(require){
'usestrict';

constdom=require('web.dom');
varcore=require('web.core');
varweDefaultOptions=require('web_editor.wysiwyg.default_options');
varwysiwygLoader=require('web_editor.loader');
varpublicWidget=require('web.public.widget');
varsession=require('web.session');
varqweb=core.qweb;

var_t=core._t;

publicWidget.registry.websiteForum=publicWidget.Widget.extend({
    selector:'.website_forum',
    xmlDependencies:['/website_forum/static/src/xml/website_forum_share_templates.xml'],
    events:{
        'click.karma_required':'_onKarmaRequiredClick',
        'mouseenter.o_js_forum_tag_follow':'_onTagFollowBoxMouseEnter',
        'mouseleave.o_js_forum_tag_follow':'_onTagFollowBoxMouseLeave',
        'mouseenter.o_forum_user_info':'_onUserInfoMouseEnter',
        'mouseleave.o_forum_user_info':'_onUserInfoMouseLeave',
        'mouseleave.o_forum_user_bio_expand':'_onUserBioExpandMouseLeave',
        'click.flag:not(.karma_required)':'_onFlagAlertClick',
        'click.vote_up:not(.karma_required),.vote_down:not(.karma_required)':'_onVotePostClick',
        'click.o_js_validation_queuea[href*="/validate"]':'_onValidationQueueClick',
        'click.o_wforum_validate_toggler:not(.karma_required)':'_onAcceptAnswerClick',
        'click.o_wforum_favourite_toggle':'_onFavoriteQuestionClick',
        'click.comment_delete':'_onDeleteCommentClick',
        'click.js_close_intro':'_onCloseIntroClick',
        'submit.js_wforum_submit_form:has(:not(.karma_required).o_wforum_submit_post)':'_onSubmitForm',
    },

    /**
     *@override
     */
    start:function(){
        varself=this;

        this.lastsearch=[];

        //float-leftclassmessesupthepostlayoutOPW769721
        $('span[data-oe-model="forum.post"][data-oe-field="content"]').find('img.float-left').removeClass('float-left');

        //welcomemessageactionbutton
        varforumLogin=_.string.sprintf('%s/web?redirect=%s',
            window.location.origin,
            encodeURIComponent(window.location.href)
        );
        $('.forum_register_url').attr('href',forumLogin);

        //Initializeforum'stooltips
        this.$('[data-toggle="tooltip"]').tooltip({delay:0});
        this.$('[data-toggle="popover"]').popover({offset:8});

        $('input.js_select2').select2({
            tags:true,
            tokenSeparators:[',','','_'],
            maximumInputLength:35,
            minimumInputLength:2,
            maximumSelectionSize:5,
            lastsearch:[],
            createSearchChoice:function(term){
                if(_.filter(self.lastsearch,function(s){
                    returns.text.localeCompare(term)===0;
                }).length===0){
                    //checkKarma
                    if(parseInt($('#karma').val())>=parseInt($('#karma_edit_retag').val())){
                        return{
                            id:'_'+$.trim(term),
                            text:$.trim(term)+'*',
                            isNew:true,
                        };
                    }
                }
            },
            formatResult:function(term){
                if(term.isNew){
                    return'<spanclass="badgebadge-primary">New</span>'+_.escape(term.text);
                }else{
                    return_.escape(term.text);
                }
            },
            ajax:{
                url:'/forum/get_tags',
                dataType:'json',
                data:function(term){
                    return{
                        query:term,
                        limit:50,
                        forum_id:$('#wrapwrap').data('forum_id'),
                    };
                },
                results:function(data){
                    varret=[];
                    _.each(data,function(x){
                        ret.push({
                            id:x.id,
                            text:x.name,
                            isNew:false,
                        });
                    });
                    self.lastsearch=ret;
                    return{results:ret};
                }
            },
            //Takedefaulttagsfromtheinputvalue
            initSelection:function(element,callback){
                vardata=[];
                _.each(element.data('init-value'),function(x){
                    data.push({id:x.id,text:x.name,isNew:false});
                });
                element.val('');
                callback(data);
            },
        });

        _.each($('textarea.o_wysiwyg_loader'),function(textarea){
            var$textarea=$(textarea);
            vareditorKarma=$textarea.data('karma')||0;//defaultvalueforbackwardcompatibility
            var$form=$textarea.closest('form');
            varhasFullEdit=parseInt($("#karma").val())>=editorKarma;
            //Warning:Donotactivateanyoptionthataddsinlinestyle.
            //Becausethestyleisdeletedaftersave.
            vartoolbar=[
                ['style',['style']],
                ['font',['bold','italic','underline','clear']],
                ['para',['ul','ol','paragraph']],
                ['table',['table']],
            ];
            if(hasFullEdit){
                toolbar.push(['insert',['link','picture']]);
            }
            toolbar.push(['history',['undo','redo']]);

            varoptions={
                height:350,
                minHeight:80,
                toolbar:toolbar,
                styleWithSpan:false,
                styleTags:_.without(weDefaultOptions.styleTags,'h1','h2','h3'),
                recordInfo:{
                    context:self._getContext(),
                    res_model:'forum.post',
                    res_id:+window.location.pathname.split('-').pop(),
                },
                disableFullMediaDialog:true,
                disableResizeImage:true,
            };
            if(!hasFullEdit){
                options.plugins={
                    LinkPlugin:false,
                    MediaPlugin:false,
                };
            }
            wysiwygLoader.load(self,$textarea[0],options).then(wysiwyg=>{
                //float-leftclassmessesupthepostlayoutOPW769721
                $form.find('.note-editable').find('img.float-left').removeClass('float-left');
                //o_we_selected_imagehasnotalwaysbeenremovedwhen
                //savingapostsoweneedthelinebelowtoremoveitifitispresent.
                $form.find('.note-editable').find('img.o_we_selected_image').removeClass('o_we_selected_image');
                $form.on('click','button,.a-submit',()=>{
                    $form.find('.note-editable').find('img.o_we_selected_image').removeClass('o_we_selected_image');
                    wysiwyg.save();
                });
            });
        });

        _.each(this.$('.o_wforum_bio_popover'),authorBox=>{
            $(authorBox).popover({
                trigger:'hover',
                offset:10,
                animation:false,
                html:true,
            }).popover('hide').data('bs.popover').tip.classList.add('o_wforum_bio_popover_container');
        });

        this.$('#post_reply').on('shown.bs.collapse',function(e){
            constreplyEl=document.querySelector('#post_reply');
            constscrollingElement=dom.closestScrollable(replyEl.parentNode);
            dom.scrollTo(replyEl,{
                forcedOffset:$(scrollingElement).innerHeight()-$(replyEl).innerHeight(),
            });
        });

        returnthis._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *
     *@override
     *@param{Event}ev
     */
    _onSubmitForm:function(ev){
        letvalidForm=true;

        let$form=$(ev.currentTarget);
        let$title=$form.find('input[name=post_name]');
        let$textarea=$form.find('textarea[name=content]');
        //It'snotreallyinthetextareathattheuserwriteatfirst
        constfillableTextAreaEl=ev.currentTarget
            .querySelector(".o_wysiwyg_wrapper.note-editable.panel-body");
        constisTextAreaFilled=fillableTextAreaEl&&
            (fillableTextAreaEl.innerText.trim()||fillableTextAreaEl.querySelector("img"));

        if($title.length&&$title[0].required){
            if($title.val()){
                $title.removeClass('is-invalid');
            }else{
                $title.addClass('is-invalid');
                validForm=false;
            }
        }

        //Becausethetextareaishidden,weaddtheredorgreenbordertoitscontainer
        if($textarea[0]&&$textarea[0].required){
            let$textareaContainer=$form.find('.o_wysiwyg_wrapper.note-editor.panel.panel-default');
            if(!isTextAreaFilled){
                $textareaContainer.addClass('borderborder-dangerrounded-top');
                validForm=false;
            }else{
                $textareaContainer.removeClass('borderborder-dangerrounded-top');
            }
        }

        if(validForm){
            //Storessocialsharedatatodisplaymodalonnextpage.
            if($form.has('.oe_social_share_call').length){
                sessionStorage.setItem('social_share',JSON.stringify({
                    targetType:$(ev.currentTarget).find('.o_wforum_submit_post').data('social-target-type'),
                }));
            }
        }else{
            ev.preventDefault();
            setTimeout(function(){
                var$buttons=$(ev.currentTarget).find('button[type="submit"],a.a-submit');
                _.each($buttons,function(btn){
                    let$btn=$(btn);
                    $btn.find('i').remove();
                    $btn.prop('disabled',false);
                });
            },0);
        }
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onKarmaRequiredClick:function(ev){
        var$karma=$(ev.currentTarget);
        varkarma=$karma.data('karma');
        varforum_id=$('#wrapwrap').data('forum_id');
        if(!karma){
            return;
        }
        ev.preventDefault();
        varmsg=karma+''+_t("karmaisrequiredtoperformthisaction.");
        vartitle=_t("KarmaError");
        if(forum_id){
            msg+='<aclass="alert-link"href="/forum/'+forum_id+'/faq">'+_t("Readtheguidelinestoknowhowtogainkarma.")+'</a>';
        }
        if(session.is_website_user){
            msg=_t("Sorryyoumustbeloggedintoperformthisaction");
            title=_t("AccessDenied");
        }
        this.call('crash_manager','show_warning',{
            message:msg,
            title:title,
        },{
            sticky:false,
        });
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onTagFollowBoxMouseEnter:function(ev){
        $(ev.currentTarget).find('.o_forum_tag_follow_box').stop().fadeIn().css('display','block');
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onTagFollowBoxMouseLeave:function(ev){
        $(ev.currentTarget).find('.o_forum_tag_follow_box').stop().fadeOut().css('display','none');
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onUserInfoMouseEnter:function(ev){
        $(ev.currentTarget).parent().find('.o_forum_user_bio_expand').delay(500).toggle('fast');
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onUserInfoMouseLeave:function(ev){
        $(ev.currentTarget).parent().find('.o_forum_user_bio_expand').clearQueue();
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onUserBioExpandMouseLeave:function(ev){
        $(ev.currentTarget).fadeOut('fast');
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onFlagAlertClick:function(ev){
        varself=this;
        ev.preventDefault();
        var$link=$(ev.currentTarget);
        this._rpc({
            route:$link.data('href')||($link.attr('href')!=='#'&&$link.attr('href'))||$link.closest('form').attr('action'),
        }).then(function(data){
            if(data.error){
                varmessage;
                if(data.error==='anonymous_user'){
                    message=_t("Sorryyoumustbeloggedtoflagapost");
                }elseif(data.error==='post_already_flagged'){
                    message=_t("Thispostisalreadyflagged");
                }elseif(data.error==='post_non_flaggable'){
                    message=_t("Thispostcannotbeflagged");
                }
                self.call('crash_manager','show_warning',{
                    message:message,
                    title:_t("AccessDenied"),
                },{
                    sticky:false,
                });
            }elseif(data.success){
                varelem=$link;
                if(data.success==='post_flagged_moderator'){
                    elem.data('href')&&elem.html('Flagged');
                    varc=parseInt($('#count_flagged_posts').html(),10);
                    c++;
                    $('#count_flagged_posts').html(c);
                }elseif(data.success==='post_flagged_non_moderator'){
                    elem.data('href')&&elem.html('Flagged');
                    varforumAnswer=elem.closest('.forum_answer');
                    forumAnswer.fadeIn(1000);
                    forumAnswer.slideUp(1000);
                }
            }
        });
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onVotePostClick:function(ev){
        varself=this;
        ev.preventDefault();
        var$btn=$(ev.currentTarget);
        this._rpc({
            route:$btn.data('href'),
        }).then(function(data){
            if(data.error){
                varmessage;
                if(data.error==='own_post'){
                    message=_t('Sorry,youcannotvoteforyourownposts');
                }elseif(data.error==='anonymous_user'){
                    message=_t('Sorryyoumustbeloggedtovote');
                }
                self.call('crash_manager','show_warning',{
                    message:message,
                    title:_t("AccessDenied"),
                },{
                    sticky:false,
                });
            }else{
                var$container=$btn.closest('.vote');
                var$items=$container.children();
                var$voteUp=$items.filter('.vote_up');
                var$voteDown=$items.filter('.vote_down');
                var$voteCount=$items.filter('.vote_count');
                varuserVote=parseInt(data['user_vote']);

                $voteUp.prop('disabled',userVote===1);
                $voteDown.prop('disabled',userVote===-1);

                $items.removeClass('text-successtext-dangertext-mutedo_forum_vote_animate');
                void$container[0].offsetWidth;//Forcearefresh

                if(userVote===1){
                    $voteUp.addClass('text-success');
                    $voteCount.addClass('text-success');
                    $voteDown.removeClass('karma_required');
                }
                if(userVote===-1){
                    $voteDown.addClass('text-danger');
                    $voteCount.addClass('text-danger');
                    $voteUp.removeClass('karma_required');
                }
                if(userVote===0){
                    if(!$voteDown.data('can-downvote')){
                        $voteDown.addClass('karma_required');
                    }
                    if(!$voteUp.data('can-upvote')){
                        $voteUp.addClass('karma_required');
                    }
                }
                $voteCount.html(data['vote_count']).addClass('o_forum_vote_animate');
            }
        });
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onValidationQueueClick:function(ev){
        ev.preventDefault();
        var$link=$(ev.currentTarget);
        $link.parents('.post_to_validate').hide();
        $.get($link.attr('href')).then(()=>{
            varleft=$('.o_js_validation_queue:visible').length;
            vartype=$('h2.o_page_headera.active').data('type');
            $('#count_post').text(left);
            $('#moderation_toolsa[href*="/'+type+'_"]').find('strong').text(left);
            if(!left){
                this.$('.o_caught_up_alert').removeClass('d-none');
            }
        },function(){
            $link.parents('.o_js_validation_queue>div').addClass('bg-dangertext-white').css('background-color','#FAA');
            $link.parents('.post_to_validate').show();
        });
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onAcceptAnswerClick:function(ev){
        ev.preventDefault();
        var$link=$(ev.currentTarget);
        vartarget=$link.data('target');

        this._rpc({
            route:$link.data('href'),
        }).then(data=>{
            if(data.error){
                if(data.error==='anonymous_user'){
                    varmessage=_t("Sorry,anonymoususerscannotchoosecorrectanswer.");
                }
                this.call('crash_manager','show_warning',{
                    message:message,
                    title:_t("AccessDenied"),
                },{
                    sticky:false,
                });
            }else{
                _.each(this.$('.forum_answer'),answer=>{
                    var$answer=$(answer);
                    varisCorrect=$answer.is(target)?data:false;
                    var$toggler=$answer.find('.o_wforum_validate_toggler');
                    varnewHelper=isCorrect?$toggler.data('helper-decline'):$toggler.data('helper-accept');

                    $answer.toggleClass('o_wforum_answer_correct',isCorrect);
                    $toggler.tooltip('dispose')
                            .attr('data-original-title',newHelper)
                            .tooltip({delay:0});
                });
            }
        });
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onFavoriteQuestionClick:function(ev){
        ev.preventDefault();
        var$link=$(ev.currentTarget);
        this._rpc({
            route:$link.data('href'),
        }).then(function(data){
            $link.toggleClass('o_wforum_goldfa-star',data)
                 .toggleClass('fa-star-otext-muted',!data);
        });
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onDeleteCommentClick:function(ev){
        ev.preventDefault();
        var$link=$(ev.currentTarget);
        var$container=$link.closest('.o_wforum_post_comments_container');

        this._rpc({
            route:$link.closest('form').attr('action'),
        }).then(function(){
            $link.closest('.o_wforum_post_comment').remove();

            varcount=$container.find('.o_wforum_post_comment').length;
            if(count){
                $container.find('.o_wforum_comments_count').text(count);
            }else{
                $container.find('.o_wforum_comments_count_header').remove();
            }
        });
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onCloseIntroClick:function(ev){
        ev.preventDefault();
        document.cookie='forum_welcome_message=false';
        $('.forum_intro').slideUp();
        returntrue;
    },
});

publicWidget.registry.websiteForumSpam=publicWidget.Widget.extend({
    selector:'.o_wforum_moderation_queue',
    xmlDependencies:['/website_forum/static/src/xml/website_forum_share_templates.xml'],
    events:{
        'click.o_wforum_select_all_spam':'_onSelectallSpamClick',
        'click.o_wforum_mark_spam':'async_onMarkSpamClick',
        'input#spamSearch':'_onSpamSearchInput',
    },

    /**
     *@override
     */
    start:function(){
        this.spamIDs=this.$('.modal').data('spam-ids');
        returnthis._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Event}ev
     */
    _onSelectallSpamClick:function(ev){
        var$spamInput=this.$('.modal.tab-pane.activeinput');
        $spamInput.prop('checked',true);
    },

    /**
     *@private
     *@param{Event}ev
     */
    _onSpamSearchInput:function(ev){
        varself=this;
        vartoSearch=$(ev.currentTarget).val();
        returnthis._rpc({
            model:'forum.post',
            method:'search_read',
            args:[
                [['id','in',self.spamIDs],
                    '|',
                    ['name','ilike',toSearch],
                    ['content','ilike',toSearch]],
                ['name','content']
            ],
            kwargs:{}
        }).then(function(o){
            _.each(o,function(r){
                r.content=$('<p>'+$(r.content).html()+'</p>').text().substring(0,250);
            });
            self.$('div.post_spam').html(qweb.render('website_forum.spam_search_name',{
                posts:o,
            }));
        });
    },

    /**
     *@private
     *@param{Event}ev
     */
    _onMarkSpamClick:function(ev){
        varkey=this.$('.modal.tab-pane.active').data('key');
        var$inputs=this.$('.modal.tab-pane.activeinput.custom-control-input:checked');
        varvalues=_.map($inputs,function(o){
            returnparseInt(o.value);
        });
        returnthis._rpc({model:'forum.post',
            method:'mark_as_offensive_batch',
            args:[this.spamIDs,key,values],
        }).then(function(){
            window.location.reload();
        });
    },
});

publicWidget.registry.WebsiteForumBackButton=publicWidget.Widget.extend({
    selector:'.o_back_button',
    events:{
        'click':'_onBackButtonClick',
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onBackButtonClick(){
        window.history.back();
    },
});

});
