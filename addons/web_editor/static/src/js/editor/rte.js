flectra.define('web_editor.rte',function(require){
'usestrict';

varfonts=require('wysiwyg.fonts');
varconcurrency=require('web.concurrency');
varcore=require('web.core');
varWidget=require('web.Widget');
varweContext=require('web_editor.context');
varsummernote=require('web_editor.summernote');
varsummernoteCustomColors=require('web_editor.rte.summernote_custom_colors');

var_t=core._t;

const{browser}=owl;

//SummernoteLib(neekchangetomakeaccessible:methodandobject)
vardom=summernote.core.dom;
varrange=summernote.core.range;

//ChangeHistorytohaveaglobalHistoryforallsummernoteinstances
varHistory=functionHistory($editable){
    varaUndo=[];
    varpos=0;
    vartoSnap;

    this.makeSnap=function(event,rng){
        rng=rng||range.create();
        varelEditable=$(rng&&rng.sc).closest('.o_editable')[0];
        if(!elEditable){
            returnfalse;
        }
        return{
            event:event,
            editable:elEditable,
            contents:elEditable.innerHTML,
            bookmark:rng&&rng.bookmark(elEditable),
            scrollTop:$(elEditable).scrollTop()
        };
    };

    this.applySnap=function(oSnap){
        var$editable=$(oSnap.editable);

        if(document.documentMode){
            $editable.removeAttr('contentEditable').removeProp('contentEditable');
        }

        $editable.trigger('content_will_be_destroyed');
        var$tempDiv=$('<div/>',{html:oSnap.contents});
        _.each($tempDiv.find('.o_temp_auto_element'),function(el){
            var$el=$(el);
            varoriginalContent=$el.attr('data-temp-auto-element-original-content');
            if(originalContent){
                $el.after(originalContent);
            }
            $el.remove();
        });
        $editable.html($tempDiv.html()).scrollTop(oSnap.scrollTop);
        $editable.trigger('content_was_recreated');

        $('.oe_overlay').remove();
        $('.note-control-selection').hide();

        $editable.trigger('content_changed');

        try{
            varr=oSnap.editable.innerHTML===''?range.create(oSnap.editable,0):range.createFromBookmark(oSnap.editable,oSnap.bookmark);
            r.select();
        }catch(e){
            console.error(e);
            return;
        }

        $(document).trigger('click');
        $('.o_editable*').filter(function(){
            var$el=$(this);
            if($el.data('snippet-editor')){
                $el.removeData();
            }
        });


        _.defer(function(){
            vartarget=dom.isBR(r.sc)?r.sc.parentNode:dom.node(r.sc);
            if(!target){
                return;
            }

            $editable.trigger('applySnap');

            varevt=document.createEvent('MouseEvents');
            evt.initMouseEvent('click',true,true,window,0,0,0,0,0,false,false,false,false,0,target);
            target.dispatchEvent(evt);

            $editable.trigger('keyup');
        });
    };

    this.undo=function(){
        if(!pos){return;}
        var_toSnap=toSnap;
        if(_toSnap){
            this.saveSnap();
        }
        if(!aUndo[pos]&&(!aUndo[pos]||aUndo[pos].event!=='undo')){
            vartemp=this.makeSnap('undo');
            if(temp&&(!pos||temp.contents!==aUndo[pos-1].contents)){
                aUndo[pos]=temp;
            }else{
               pos--;
            }
        }elseif(_toSnap){
            pos--;
        }
        this.applySnap(aUndo[Math.max(--pos,0)]);
        while(pos&&(aUndo[pos].event==='blur'||(aUndo[pos+1].editable=== aUndo[pos].editable&&aUndo[pos+1].contents=== aUndo[pos].contents))){
            this.applySnap(aUndo[--pos]);
        }
    };

    this.hasUndo=function(){
        return(toSnap&&(toSnap.event!=='blur'&&toSnap.event!=='activate'&&toSnap.event!=='undo'))||
            !!_.find(aUndo.slice(0,pos+1),function(undo){
                returnundo.event!=='blur'&&undo.event!=='activate'&&undo.event!=='undo';
            });
    };

    this.getEditableHasUndo=function(){
        vareditable=[];
        if((toSnap&&(toSnap.event!=='blur'&&toSnap.event!=='activate'&&toSnap.event!=='undo'))){
            editable.push(toSnap.editable);
        }
        _.each(aUndo.slice(0,pos+1),function(undo){
            if(undo.event!=='blur'&&undo.event!=='activate'&&undo.event!=='undo'){
                editable.push(undo.editable);
            }
        });
        return_.uniq(editable);
    };

    this.redo=function(){
        if(!aUndo[pos+1]){return;}
        this.applySnap(aUndo[++pos]);
        while(aUndo[pos+1]&&aUndo[pos].event==='active'){
            this.applySnap(aUndo[pos++]);
        }
    };

    this.hasRedo=function(){
        returnaUndo.length>pos+1;
    };

    this.recordUndo=function($editable,event,internal_history){
        varself=this;
        if(!$editable){
            varrng=range.create();
            if(!rng)return;
            $editable=$(rng.sc).closest('.o_editable');
        }

        if(aUndo[pos]&&(event==='applySnap'||event==='activate')){
            return;
        }

        if(!internal_history){
            if(!event||!toSnap||!aUndo[pos-1]||toSnap.event==='activate'){//don'ttriggerchangeforallkeypress
                setTimeout(function(){
                    $editable.trigger('content_changed');
                },0);
            }
        }

        if(aUndo[pos]){
            pos=Math.min(pos,aUndo.length);
            aUndo.splice(pos,aUndo.length);
        }

        //=>makeasnapwhentheuserchangeeditablezone(because:don'tmakesnapforeachkeydown)
        if(toSnap&&(toSnap.split||!event||toSnap.event!==event||toSnap.editable!==$editable[0])){
            this.saveSnap();
        }

        if(pos&&aUndo[pos-1].editable!==$editable[0]){
            varsnap=this.makeSnap('blur',range.create(aUndo[pos-1].editable,0));
            pos++;
            aUndo.push(snap);
        }

        if(range.create()){
            toSnap=self.makeSnap(event);
        }else{
            toSnap=false;
        }
    };

    this.splitNext=function(){
        if(toSnap){
            toSnap.split=true;
        }
    };

    this.saveSnap=function(){
        if(toSnap){
            if(!aUndo[pos]){
                pos++;
            }
            aUndo.push(toSnap);
            deletetoSnap.split;
            toSnap=null;
        }
    };
};
varhistory=newHistory();

//jQueryextensions
$.extend($.expr[':'],{
    o_editable:function(node,i,m){
        while(node){
            if(node.className&&_.isString(node.className)){
                if(node.className.indexOf('o_not_editable')!==-1){
                    returnfalse;
                }
                if(node.className.indexOf('o_editable')!==-1){
                    returntrue;
                }
            }
            node=node.parentNode;
        }
        returnfalse;
    },
});
$.fn.extend({
    focusIn:function(){
        if(this.length){
            range.create(dom.firstChild(this[0]),0).select();
        }
        returnthis;
    },
    focusInEnd:function(){
        if(this.length){
            varlast=dom.lastChild(this[0]);
            range.create(last,dom.nodeLength(last)).select();
        }
        returnthis;
    },
    selectContent:function(){
        if(this.length){
            varnext=dom.lastChild(this[0]);
            range.create(dom.firstChild(this[0]),0,next,next.textContent.length).select();
        }
        returnthis;
    },
});

//RTE
varRTEWidget=Widget.extend({
    /**
     *@constructor
     */
    init:function(parent,params){
        varself=this;
        this._super.apply(this,arguments);

        this.init_bootstrap_carousel=$.fn.carousel;
        this.edit_bootstrap_carousel=function(){
            varres=self.init_bootstrap_carousel.apply(this,arguments);
            //offbootstrapkeydowneventtoremoveevent.preventDefault()
            //andallowtochangecursorposition
            $(this).off('keydown.bs.carousel');
            returnres;
        };

        this._getConfig=params&&params.getConfig||this._getDefaultConfig;
        this._saveElement=params&&params.saveElement||this._saveElement;

        fonts.computeFonts();
    },
    /**
     *@override
     */
    start:function(){
        varself=this;

        this.saving_mutex=newconcurrency.Mutex();

        $.fn.carousel=this.edit_bootstrap_carousel;

        $(document).on('click.rtekeyup.rte',function(){
            varcurrent_range={};
            try{
                current_range=range.create()||{};
            }catch(e){
                //ifrangeisonRestrictedelementignoreerror
            }
            var$popover=$(current_range.sc).closest('[contenteditable]');
            varpopover_history=($popover.data()||{}).NoteHistory;
            if(!popover_history||popover_history===history)return;
            vareditor=$popover.parent('.note-editor');
            $('button[data-event="undo"]',editor).attr('disabled',!popover_history.hasUndo());
            $('button[data-event="redo"]',editor).attr('disabled',!popover_history.hasRedo());
        });
        $(document).on('mousedown.rteactivate.rte',this,this._onMousedown.bind(this));
        $(document).on('mouseup.rte',this,this._onMouseup.bind(this));

        $('.o_not_editable').attr('contentEditable',false);

        var$editable=this.editable();
        this.__$editable=$editable;

        //Whenaundo/redoisperformed,thewholeDOMischangedsowehave
        //toprepareforit(websitewillrestartanimationsforexample)
        //TODOshouldbebetterhandled
        $editable.on('content_will_be_destroyed',function(ev){
            self.trigger_up('content_will_be_destroyed',{
                $target:$(ev.currentTarget),
            });
        });
        $editable.on('content_was_recreated',function(ev){
            self.trigger_up('content_was_recreated',{
                $target:$(ev.currentTarget),
            });
        });

        $editable.addClass('o_editable')
        .data('rte',this)
        .each(function(){
            var$node=$(this);

            //fallbackforfirefoxiframedisplay:noneseehttps://github.com/flectra/flectra/pull/22610
            varcomputedStyles=window.getComputedStyle(this)||window.parent.getComputedStyle(this);
            //addclasstodisplayinline-blockforemptyt-field
            if(computedStyles.display==='inline'&&$node.data('oe-type')!=='image'){
                $node.addClass('o_is_inline_editable');
            }
        });

        //startelementobservation
        letpastingData=false;
        $(document).on('paste',function(ev){
            pastingData=[...self.editable()];
            browser.setTimeout(function(){pastingData=false;},0);
        });
        $(document).on('content_changed',function(ev){
            self.trigger_up('rte_change',{target:ev.target});

            if(pastingData){
                constpastedDirtyEls=ev.target.querySelectorAll('[data-oe-id]');
                _.difference([...pastedDirtyEls],pastingData).forEach(el=>{
                    constdirtyAttributes=el.getAttributeNames().filter(name=>!name.indexOf("data-oe-"));
                    dirtyAttributes.forEach(name=>el.removeAttribute(name));
                })
                pastingData=false;
            }

            //Addthedirtyflagtotheelementthatchangedbyeitheradding
            //itonthehighesteditableancestoror,ifthereisnoeditable
            //ancestor,ontheelementitself(thatelementmaynotbeeditable
            //butifitreceivedacontent_changedevent,itshouldbemarked
            //asdirtytoallowforcustomsavings).
            if(!ev.__isDirtyHandled){
                ev.__isDirtyHandled=true;

                varel=ev.target;
                vardirty=el.closest('.o_editable')||el;
                dirty.classList.add('o_dirty');
            }
        });

        $('#wrapwrap,.o_editable').on('click.rte','*',this,this._onClick.bind(this));

        $('body').addClass('editor_enable');

        $(document.body)
            .tooltip({
                selector:'[data-oe-readonly]',
                container:'body',
                trigger:'hover',
                delay:{'show':1000,'hide':100},
                placement:'bottom',
                title:_t("Readonlyfield")
            })
            .on('click',function(){
                $(this).tooltip('hide');
            });

        $(document).trigger('mousedown');
        this.trigger('rte:start');

        returnthis._super.apply(this,arguments);
    },
    /**
     *@override
     */
    destroy:function(){
        this.cancel();
        this._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *StopstheRTE.
     */
    cancel:function(){
        if(this.$last){
            this.$last.destroy();
            this.$last=null;
        }

        $.fn.carousel=this.init_bootstrap_carousel;

        $(document).off('.rte');
        $('#wrapwrap,.o_editable').off('.rte');

        $('.o_not_editable').removeAttr('contentEditable');

        $(document).off('click.rtekeyup.rtemousedown.rteactivate.rtemouseup.rte');
        $(document).off('content_changed').removeClass('o_is_inline_editable').removeData('rte');
        $(document).tooltip('dispose');
        $('body').removeClass('editor_enable');
        this.trigger('rte:stop');
    },
    /**
     *Returnstheeditableareasonthepage.
     *
     *@returns{jQuery}
     */
    editable:function(){
        return$('#wrapwrap[data-oe-model]')
            .not('.o_not_editable')
            .filter(function(){
                return!$(this).closest('.o_not_editable').length;
            })
            .not('link,script')
            .not('[data-oe-readonly]')
            .not('img[data-oe-field="arch"],br[data-oe-field="arch"],input[data-oe-field="arch"]')
            .not('.oe_snippet_editor')
            .add('.o_editable');
    },
    /**
     *Recordsthecurrentstateofthegiven$targettobeabletoundofuture
     *changes.
     *
     *@seeHistory.recordUndo
     *@param{jQuery}$target
     *@param{string}event
     *@param{boolean}internal_history
     */
    historyRecordUndo:function($target,event,internal_history){
        constinitialActiveElement=document.activeElement;
        constinitialSelectionStart=initialActiveElement&&initialActiveElement.selectionStart;
        constinitialSelectionEnd=initialActiveElement&&initialActiveElement.selectionEnd;

        $target=$($target);
        varrng=range.create();
        var$editable=$(rng&&rng.sc).closest('.o_editable');
        if(!rng||!$editable.length){
            $editable=$target.closest('.o_editable');
            rng=range.create($target.closest('*')[0],0);
        }else{
            rng=$editable.data('range')||rng;
        }
        try{
            //TODOthislinemightbreakforunknownreasons.Isupposethat
            //thecreatedrangeisaninvalidone.Asitmightbetrickyto
            //adaptthatlineandthatitisnotacriticalone,temporaryfix
            //istoignoretheerrorsthatthisgenerates.
            rng.select();
        }catch(e){
            console.log('error',e);
        }
        history.recordUndo($editable,event,internal_history);

        if(initialActiveElement&&initialActiveElement!==document.activeElement){
            initialActiveElement.focus();
            //Rangeinputsdon'tsupportselection
            if(initialActiveElement.matches('input[type=range]')){
                return;
            }
            try{
                initialActiveElement.selectionStart=initialSelectionStart;
                initialActiveElement.selectionEnd=initialSelectionEnd;
            }catch(e){
                //Theactiveelementmightbeofatypethat
                //doesnotsupportselection.
                console.log('error',e);
            }
        }
    },
    /**
     *Searchesallthedirtyelementonthepageandsavesthemonebyone.If
     *onecannotbesaved,thisnotifiesittotheuserandrestartsrte
     *edition.
     *
     *@param{Object}[context]-thecontexttouseforsavingrpc,defaultto
     *                          theeditorcontextfoundonthepage
     *@return{Promise}rejectedifthesavecannotbedone
     */
    save:function(context){
        varself=this;

        $('.o_editable')
            .destroy()
            .removeClass('o_editableo_is_inline_editableo_editable_date_field_linkedo_editable_date_field_format_changed');

        var$dirty=$('.o_dirty');
        $dirty
            .removeAttr('contentEditable')
            .removeClass('o_dirtyoe_carlos_dangero_is_inline_editable');
        vardefs=_.map($dirty,function(el){
            var$el=$(el);

            $el.find('[class]').filter(function(){
                if(!this.getAttribute('class').match(/\S/)){
                    this.removeAttribute('class');
                }
            });

            //TODO:Addaqueuewithconcurrencylimitinwebclient
            //https://github.com/medikoo/deferred/blob/master/lib/ext/function/gate.js
            returnself.saving_mutex.exec(function(){
                returnself._saveElement($el,context||weContext.get())
                .then(function(){
                    $el.removeClass('o_dirty');
                }).guardedCatch(function(response){
                    //becauseckeditorregeneratesallthedom,wecan'tjust
                    //setupthepopoverhereaseverythingwillbedestroyedby
                    //theDOMregeneration.Addmarkingsinstead,andreturnsa
                    //newrejectionwithallrelevantinfo
                    varid=_.uniqueId('carlos_danger_');
                    $el.addClass('o_dirtyoe_carlos_danger'+id);
                    $('.o_editable.'+id)
                        .removeClass(id)
                        .popover({
                            trigger:'hover',
                            content:response.message.data.message||'',
                            placement:'autotop',
                        })
                        .popover('show');
                });
            });
        });

        returnPromise.all(defs).then(function(){
            window.onbeforeunload=null;
        }).guardedCatch(function(failed){
            //Iftherewereerrors,re-enableedition
            self.cancel();
            self.start();
        });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Whentheusersclicksonaneditableelement,thisfunctionallowstoadd
     *externalbehaviors.
     *
     *@private
     *@param{jQuery}$editable
     */
    _enableEditableArea:function($editable){
        if($editable.data('oe-type')==="datetime"||$editable.data('oe-type')==="date"){
            varselector='[data-oe-id="'+$editable.data('oe-id')+'"]';
            selector+='[data-oe-field="'+$editable.data('oe-field')+'"]';
            selector+='[data-oe-model="'+$editable.data('oe-model')+'"]';
            var$linkedFieldNodes=this.editable().find(selector).addBack(selector);
            $linkedFieldNodes.not($editable).addClass('o_editable_date_field_linked');
            if(!$editable.hasClass('o_editable_date_field_format_changed')){
                $linkedFieldNodes.html($editable.data('oe-original-with-format'));
                $linkedFieldNodes.addClass('o_editable_date_field_format_changed');
            }
        }
        if($editable.data('oe-type')==="monetary"){
            $editable.attr('contenteditable',false);
            $editable.find('.oe_currency_value').attr('contenteditable',true);
        }
        if($editable.is('[data-oe-model]')&&!$editable.is('[data-oe-model="ir.ui.view"]')&&!$editable.is('[data-oe-type="html"]')){
            $editable.data('layoutInfo').popover().find('.btn-group:not(.note-history)').remove();
        }
        if($editable.data('oe-type')==="image"){
            $editable.attr('contenteditable',false);
            $editable.find('img').attr('contenteditable',true);
        }
    },
    /**
     *Whenanelemententersedition,summernoteisinitializedonit.This
     *functionreturnsthedefaultconfigurationforthesummernoteinstance.
     *
     *@see_getConfig
     *@private
     *@param{jQuery}$editable
     *@returns{Object}
     */
    _getDefaultConfig:function($editable){
        return{
            'airMode':true,
            'focus':false,
            'airPopover':[
                ['style',['style']],
                ['font',['bold','italic','underline','clear']],
                ['fontsize',['fontsize']],
                ['color',['color']],
                ['para',['ul','ol','paragraph']],
                ['table',['table']],
                ['insert',['link','picture']],
                ['history',['undo','redo']],
            ],
            'styleWithSpan':false,
            'inlinemedia':['p'],
            'lang':'flectra',
            'onChange':function(html,$editable){
                $editable.trigger('content_changed');
            },
            'colors':summernoteCustomColors,
        };
    },
    /**
     *GetsjQueryclonedelementwithinternaltextnodesescapedforXML
     *storage.
     *
     *@private
     *@param{jQuery}$el
     *@return{jQuery}
     */
    _getEscapedElement:function($el){
        varescaped_el=$el.clone();
        varto_escape=escaped_el.find('*').addBack();
        to_escape=to_escape.not(to_escape.filter('object,iframe,script,style,[data-oe-model][data-oe-model!="ir.ui.view"]').find('*').addBack());
        to_escape.contents().each(function(){
            if(this.nodeType===3){
                this.nodeValue=$('<div/>').text(this.nodeValue).html();
            }
        });
        returnescaped_el;
    },
    /**
     *Savesone(dirty)elementofthepage.
     *
     *@private
     *@param{jQuery}$el-theelementtosave
     *@param{Object}context-thecontexttouseforthesavingrpc
     *@param{boolean}[withLang=false]
     *       falseifthelangmustbeomittedinthecontext(saving"master"
     *       pageelement)
     */
    _saveElement:function($el,context,withLang){
        varviewID=$el.data('oe-id');
        if(!viewID){
            returnPromise.resolve();
        }

        returnthis._rpc({
            model:'ir.ui.view',
            method:'save',
            args:[
                viewID,
                this._getEscapedElement($el).prop('outerHTML'),
                $el.data('oe-xpath')||null,
            ],
            context:context,
        },withLang?undefined:{
            noContextKeys:'lang',
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Calledwhenanyeditableelementisclicked->Preventsdefaultbrowser
     *actionfortheelement.
     *
     *@private
     *@param{Event}e
     */
    _onClick:function(e){
        e.preventDefault();
    },
    /**
     *Calledwhenthemouseispressedonthedocument->activateelement
     *edition.
     *
     *@private
     *@param{Event}ev
     */
    _onMousedown:function(ev){
        var$target=$(ev.target);
        var$editable=$target.closest('.o_editable');
        varisLink=$target.is('a');

        if(this&&this.$last&&this.$last.length&&this.$last[0]!==$target[0]){
            $('.o_editable_date_field_linked').removeClass('o_editable_date_field_linked');
        }
        if(!$editable.length||(!isLink&&$.summernote.core.dom.isContentEditableFalse($target))){
            return;
        }

        //Removesstrange_moz_absposattributewhenitappears.Cannot
        //findanothersolutionwhichworksinallcases.Agrabberstill
        //appearsatthesametimewhichIdidnotmanagetoremove.
        //TODOfindacompleteandbettersolution
        _.defer(function(){
            $editable.find('[_moz_abspos]').removeAttr('_moz_abspos');
        });

        if(isLink&&!$target.closest('.o_not_editable').length){
            /**
             *Removecontenteditableeverywhereandadditonthelinkonlysothatcharacterscanbeadded
             *andremovedatthestartandattheendofit.
             */
            lethasContentEditable=$target.attr('contenteditable');
            $target.attr('contenteditable',true);
            _.defer(function(){
                $editable.not($target).attr('contenteditable',false);
                $target.focus();
            });

            //Onceclickedoutside,removecontenteditableonlinkandreactiveall
            $(document).on('mousedown.reactivate_contenteditable',function(e){
                if($target.is(e.target))return;
                if(!hasContentEditable){
                    $target.removeAttr('contenteditable');
                }
                $editable.attr('contenteditable',true);
                $(document).off('mousedown.reactivate_contenteditable');
            });
        }

        if(this&&this.$last&&(!$editable.length||this.$last[0]!==$editable[0])){
            var$destroy=this.$last;
            history.splitNext();
            //Insomespecialcases,weneedtoclearthetimeout.
            varlastTimerId=_.delay(function(){
                varid=$destroy.data('note-id');
                $destroy.destroy().removeData('note-id').removeAttr('data-note-id');
                $('#note-popover-'+id+',#note-handle-'+id+',#note-dialog-'+id+'').remove();
            },150);//setTimeouttoremoveflickeringwhenchangetoeditablezone(re-createaneditor)
            this.$last=null;
            //formodaldialogs(egnewsletterpopup),whenweclosethedialog,themodalis
            //destroyedimmediatelyandsoafterthedelayedexecutionduetotimeout,dialogwill
            //notbeavailable,leadingtotrace-back,soweneedtoclearTimeoutforthedialogs.
            if($destroy.hasClass('modal-body')){
                clearTimeout(lastTimerId);
            }
        }

        if($editable.length&&(!this.$last||this.$last[0]!==$editable[0])){
            $editable.summernote(this._getConfig($editable));

            $editable.data('NoteHistory',history);
            this.$last=$editable;

            //firefox&IEfix
            try{
                document.execCommand('enableObjectResizing',false,false);
                document.execCommand('enableInlineTableEditing',false,false);
                document.execCommand('2D-position',false,false);
            }catch(e){/**/}
            document.body.addEventListener('resizestart',function(evt){evt.preventDefault();returnfalse;});
            document.body.addEventListener('movestart',function(evt){evt.preventDefault();returnfalse;});
            document.body.addEventListener('dragstart',function(evt){evt.preventDefault();returnfalse;});

            if(!range.create()){
                $editable.focusIn();
            }

            if(dom.isImg($target[0])){
                $target.trigger('mousedown');//foractivateselectiononpicture
            }

            this._enableEditableArea($editable);
        }
    },
    /**
     *Calledwhenthemouseisunpressedonthedocument.
     *
     *@private
     *@param{Event}ev
     */
    _onMouseup:function(ev){
        var$target=$(ev.target);
        var$editable=$target.closest('.o_editable');

        if(!$editable.length){
            return;
        }

        varself=this;
        _.defer(function(){
            self.historyRecordUndo($target,'activate', true);
        });

        //Browsersselectdifferentcontentfromonetoanotheraftera
        //tripleclick(especially:iftriple-clickingonaparagraphon
        //Chrome,blankcharactersoftheelementfollowingtheparagraphare
        //selectedtoo)
        //
        //Thetripleclickbehaviorisreimplementedforallbrowsershere
        if(ev.originalEvent&&ev.originalEvent.detail===3){
            //SelectthewholecontentinsidethedeepestDOMelementthatwas
            //triple-clicked
            range.create(ev.target,0,ev.target,ev.target.childNodes.length).select();
        }
    },
});

return{
    Class:RTEWidget,
    history:history,
};
});

flectra.define('web_editor.rte.summernote_custom_colors',function(require){
'usestrict';

//ThesecolorsarealreadynormalizedaspernormalizeCSSColorinweb.Colorpicker
return[
    ['#000000','#424242','#636363','#9C9C94','#CEC6CE','#EFEFEF','#F7F7F7','#FFFFFF'],
    ['#FF0000','#FF9C00','#FFFF00','#00FF00','#00FFFF','#0000FF','#9C00FF','#FF00FF'],
    ['#F7C6CE','#FFE7CE','#FFEFC6','#D6EFD6','#CEDEE7','#CEE7F7','#D6D6E7','#E7D6DE'],
    ['#E79C9C','#FFC69C','#FFE79C','#B5D6A5','#A5C6CE','#9CC6EF','#B5A5D6','#D6A5BD'],
    ['#E76363','#F7AD6B','#FFD663','#94BD7B','#73A5AD','#6BADDE','#8C7BC6','#C67BA5'],
    ['#CE0000','#E79439','#EFC631','#6BA54A','#4A7B8C','#3984C6','#634AA5','#A54A7B'],
    ['#9C0000','#B56308','#BD9400','#397B21','#104A5A','#085294','#311873','#731842'],
    ['#630000','#7B3900','#846300','#295218','#083139','#003163','#21104A','#4A1031']
];
});
