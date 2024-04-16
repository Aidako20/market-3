flectra.define('web_editor.field.html',function(require){
'usestrict';

varajax=require('web.ajax');
varbasic_fields=require('web.basic_fields');
varconfig=require('web.config');
varcore=require('web.core');
varWysiwyg=require('web_editor.wysiwyg.root');
varfield_registry=require('web.field_registry');
//mustwaitforweb/toaddthedefaulthtmlwidget,otherwiseitwouldoverridetheweb_editorone
require('web._field_registry');

var_lt=core._lt;
varTranslatableFieldMixin=basic_fields.TranslatableFieldMixin;
varQWeb=core.qweb;
varassetsLoaded;

varjinjaRegex=/(^|\n)\s*%\s(end|set\s)/;

/**
 *FieldHtmlWidget
 *IntendedtodisplayHTMLcontent.Thiswidgetusesthewysiwygeditor
 *improvedbyflectra.
 *
 *nodeOptions:
 * -style-inline=>convertclasstoinlinestyle(nore-edition)=>forsendingbyemail
 * -no-attachment
 * -cssEdit
 * -cssReadonly
 * -snippets
 * -wrapper
 */
varFieldHtml=basic_fields.DebouncedField.extend(TranslatableFieldMixin,{
    description:_lt("Html"),
    className:'oe_form_fieldoe_form_field_html',
    supportedFieldTypes:['html'],

    custom_events:{
        wysiwyg_focus:'_onWysiwygFocus',
        wysiwyg_blur:'_onWysiwygBlur',
        wysiwyg_change:'_onChange',
        wysiwyg_attachment:'_onAttachmentChange',
    },

    /**
     *@override
     */
    willStart:function(){
        varself=this;
        this.isRendered=false;
        this._onUpdateIframeId='onLoad_'+_.uniqueId('FieldHtml');
        vardefAsset;
        if(this.nodeOptions.cssReadonly){
            defAsset=ajax.loadAsset(this.nodeOptions.cssReadonly);
        }

        if(!assetsLoaded){//avoidflickeringwhenbegintoedit
            assetsLoaded=newPromise(function(resolve){
                varwysiwyg=newWysiwyg(self,{});
                wysiwyg.attachTo($('<textarea>')).then(function(){
                    wysiwyg.destroy();
                    resolve();
                });
            });
        }

        returnPromise.all([this._super(),assetsLoaded,defAsset]);
    },
    /**
     *@override
     */
    destroy:function(){
        deletewindow.top[this._onUpdateIframeId];
        if(this.$iframe){
            this.$iframe.remove();
        }
        this._super();
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    activate:function(options){
        if(this.wysiwyg){
            this.wysiwyg.focus();
            returntrue;
        }
    },
    /**
     *Wysiwygdoesn'tnotifyforchangesdoneincodemode.Weoverride
     *commitChangestomanuallyswitchbacktonormalmodebeforecommitting
     *changes,sothatthewidgetisawareofthechangesdoneincodemode.
     *
     *@override
     */
    commitChanges:function(){
        varself=this;
        if(config.isDebug()&&this.mode==='edit'){
            varlayoutInfo=$.summernote.core.dom.makeLayoutInfo(this.wysiwyg.$editor);
            $.summernote.pluginEvents.codeview(undefined,undefined,layoutInfo,false);
        }
        if(this.mode=="readonly"||!this.isRendered){
            returnthis._super();
        }
        var_super=this._super.bind(this);
        returnthis.wysiwyg.saveModifiedImages(this.$content).then(function(){
            returnself.wysiwyg.save(self.nodeOptions).then(function(result){
                self._isDirty=result.isDirty;
                _super();
            });
        });
    },
    /**
     *@override
     */
    isSet:function(){
        varvalue=this.value&&this.value.split('&nbsp;').join('').replace(/\s/g,'');//Removingspaces&htmlspaces
        returnvalue&&value!=="<p></p>"&&value!=="<p><br></p>"&&value.match(/\S/);
    },
    /**
     *@override
     */
    getFocusableElement:function(){
        returnthis.$target||$();
    },
    /**
     *Donotre-renderthisfieldifitwastheoriginoftheonchangecall.
     *
     *@override
     */
    reset:function(record,event){
        this._reset(record,event);
        varvalue=this.value;
        if(this.nodeOptions.wrapper){
            value=this._wrap(value);
        }
        value=this._textToHtml(value);
        if(!event||event.target!==this){
            if(this.mode==='edit'){
                this.wysiwyg.setValue(value);
            }else{
                this.$content.html(value);
            }
        }
        returnPromise.resolve();
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _getValue:function(){
        varvalue=this.$target.val();
        if(this.nodeOptions.wrapper){
            returnthis._unWrap(value);
        }
        returnvalue;
    },
    /**
     *Createthewysiwyginstancewiththetarget(this.$target)
     *thenaddtheeditablecontent(this.$content).
     *
     *@private
     *@returns{$.Promise}
     */
    _createWysiwygIntance:function(){
        varself=this;
        this.wysiwyg=newWysiwyg(this,this._getWysiwygOptions());
        this.wysiwyg.__extraAssetsForIframe=this.__extraAssetsForIframe||[];

        //bydefaultthisissynchronousbecausetheassetsarealreadyloadedinwillStart
        //butitcanbeasyncinthecaseofoptionssuchasiframe,snippets...
        returnthis.wysiwyg.attachTo(this.$target).then(function(){
            self.$content=self.wysiwyg.$editor.closest('body,flectra-wysiwyg-container');
            self._onLoadWysiwyg();
            self.isRendered=true;
        });
    },
    /**
     *Getwysiwygoptionstocreatewysiwyginstance.
     *
     *@private
     *@returns{Object}
     */
    _getWysiwygOptions:function(){
        varself=this;
        returnObject.assign({},this.nodeOptions,{
            recordInfo:{
                context:this.record.getContext(this.recordParams),
                res_model:this.model,
                res_id:this.res_id,
            },
            noAttachment:this.nodeOptions['no-attachment'],
            inIframe:!!this.nodeOptions.cssEdit,
            iframeCssAssets:this.nodeOptions.cssEdit,
            snippets:this.nodeOptions.snippets,

            tabsize:0,
            height:180,
            generateOptions:function(options){
                vartoolbar=options.toolbar||options.airPopover||{};
                varpara=_.find(toolbar,function(item){
                    returnitem[0]==='para';
                });
                if(para&&para[1]&&para[1].indexOf('checklist')===-1){
                    para[1].splice(2,0,'checklist');
                }
                if(config.isDebug()){
                    options.codeview=true;
                    varview=_.find(toolbar,function(item){
                        returnitem[0]==='view';
                    });
                    if(view){
                        if(!view[1].includes('codeview')){
                            view[1].splice(-1,0,'codeview');
                        }
                    }else{
                        toolbar.splice(-1,0,['view',['codeview']]);
                    }
                }
                if(self.model==="mail.compose.message"||self.model==="mailing.mailing"){
                    options.noVideos=true;
                }
                options.prettifyHtml=false;
                returnoptions;
            },
        });
    },
    /**
     *trigger_up'field_changed'addrecordintothe"ir.attachment"fieldfoundintheview.
     *Thismethodiscalledwhenanimageisuploadedviathemediadialog.
     *
     *Fore.g.whensendingemail,thisallowspeopletoaddattachmentswiththecontent
     *editorinterfaceandthattheyappearintheattachmentlist.
     *Thenewdocumentsbeingattachedtotheemail,theywillnotbeerasedbytheCRON
     *whenclosingthewizard.
     *
     *@private
     *@param{Object}eventtheeventcontainingattachmentdata
     */
    _onAttachmentChange:function(event){
        //Thisonlyneedstohappenforthecomposerfornow
        if(!this.fieldNameAttachment||this.model!=='mail.compose.message'){
            return;
        }
        this.trigger_up('field_changed',{
            dataPointID:this.dataPointID,
            changes:_.object([this.fieldNameAttachment],[{
                operation:'ADD_M2M',
                ids:event.data
            }])
        });
    },
    /**
     *@override
     */
    _renderEdit:function(){
        varvalue=this._textToHtml(this.value);
        if(this.nodeOptions.wrapper){
            value=this._wrap(value);
        }
        this.$target=$('<textarea>').val(value).hide();
        this.$target.appendTo(this.$el);

        varfieldNameAttachment=_.chain(this.recordData)
            .pairs()
            .find(function(value){
                return_.isObject(value[1])&&value[1].model==="ir.attachment";
            })
            .first()
            .value();
        if(fieldNameAttachment){
            this.fieldNameAttachment=fieldNameAttachment;
        }

        if(this.nodeOptions.cssEdit){
            //mustbeasyncbecausethetargetmustbeappendintheDOM
            this._createWysiwygIntance();
        }else{
            returnthis._createWysiwygIntance();
        }
    },
    /**
     *@override
     */
    _renderReadonly:function(){
        varself=this;
        varvalue=this._textToHtml(this.value);
        if(this.nodeOptions.wrapper){
            value=this._wrap(value);
        }

        this.$el.empty();
        varresolver;
        vardef=newPromise(function(resolve){
            resolver=resolve;
        });
        if(this.nodeOptions.cssReadonly){
            this.$iframe=$('<iframeclass="o_readonly"/>');
            this.$iframe.appendTo(this.$el);

            varavoidDoubleLoad=0;//thisbugonlyappearsonsomecomputerswithsomechromeversion.

            //injectcontentiniframe

            this.$iframe.data('loadDef',def);//forunittest
            window.top[this._onUpdateIframeId]=function(_avoidDoubleLoad){
                if(_avoidDoubleLoad!==avoidDoubleLoad){
                    console.warn('Wysiwygiframedoubleloaddetected');
                    return;
                }
                self.$content=$('#iframe_target',self.$iframe[0].contentWindow.document.body);
                resolver();
            };

            this.$iframe.on('load',functiononLoad(){
                var_avoidDoubleLoad=++avoidDoubleLoad;
                ajax.loadAsset(self.nodeOptions.cssReadonly).then(function(asset){
                    if(_avoidDoubleLoad!==avoidDoubleLoad){
                        console.warn('Wysiwygimmediateiframedoubleloaddetected');
                        return;
                    }
                    varcwindow=self.$iframe[0].contentWindow;
                    try{
                        cwindow.document;
                    }catch(e){
                        return;
                    }
                    cwindow.document
                        .open("text/html","replace")
                        .write(
                            '<head>'+
                                '<metacharset="utf-8"/>'+
                                '<metahttp-equiv="X-UA-Compatible"content="IE=edge,chrome=1"/>\n'+
                                '<metaname="viewport"content="width=device-width,initial-scale=1,user-scalable=no"/>\n'+
                                _.map(asset.cssLibs,function(cssLib){
                                    return'<linktype="text/css"rel="stylesheet"href="'+cssLib+'"/>';
                                }).join('\n')+'\n'+
                                _.map(asset.cssContents,function(cssContent){
                                    return'<styletype="text/css">'+cssContent+'</style>';
                                }).join('\n')+'\n'+
                            '</head>\n'+
                            '<bodyclass="o_in_iframeo_readonly">\n'+
                                '<divid="iframe_target">'+value+'</div>\n'+
                                '<scripttype="text/javascript">'+
                                    'if(window.top.'+self._onUpdateIframeId+'){'+
                                        'window.top.'+self._onUpdateIframeId+'('+_avoidDoubleLoad+')'+
                                    '}'+
                                '</script>\n'+
                            '</body>');

                    varheight=cwindow.document.body.scrollHeight;
                    self.$iframe.css('height',Math.max(30,Math.min(height,500))+'px');
                });
            });
        }else{
            this.$content=$('<divclass="o_readonly"/>').html(value);
            this.$content.appendTo(this.$el);
            resolver();
        }

        def.then(function(){
            self.$content.on('click','ul.o_checklist>li',self._onReadonlyClickChecklist.bind(self));
        });
    },
    /**
     *@private
     *@param{string}text
     *@returns{string}thetextconvertedtohtml
     */
    _textToHtml:function(text){
        varvalue=text||"";
        if(jinjaRegex.test(value)){//isjinja
            returnvalue;
        }
        try{
            $(text)[0].innerHTML;//crashesiftextisn'thtml
        }catch(e){
            if(value.match(/^\s*$/)){
                value='<p><br/></p>';
            }else{
                value="<p>"+value.split(/<br\/?>/).join("<br/></p><p>")+"</p>";
                value=value
                            .replace(/<p><\/p>/g,'')
                            .replace('<p><p>','<p>')
                            .replace('<p><p','<p')
                            .replace('</p></p>','</p>');
            }
        }
        returnvalue;
    },
    /**
     *MoveHTMLcontentsoutoftheirwrapper.
     *
     *@private
     *@param{string}htmlcontent
     *@returns{string}htmlcontent
     */
    _unWrap:function(html){
        var$wrapper=$(html).find('#wrapper');
        return$wrapper.length?$wrapper.html():html;
    },
    /**
     *WrapHTMLinordertocreateacustomdisplay.
     *
     *Thewrapper(this.nodeOptions.wrapper)mustbeastatic
     *XMLtemplatewithcontentid="wrapper".
     *
     *@private
     *@param{string}htmlcontent
     *@returns{string}htmlcontent
     */
    _wrap:function(html){
        return$(QWeb.render(this.nodeOptions.wrapper))
            .find('#wrapper').html(html)
            .end().prop('outerHTML');
    },

    //--------------------------------------------------------------------------
    //Handler
    //--------------------------------------------------------------------------

    /**
     *Methodcalledwhenwysiwygtriggersachange.
     *
     *@private
     *@param{FlectraEvent}ev
     */
    _onChange:function(ev){
        this._doDebouncedAction.apply(this,arguments);

        var$lis=this.$content.find('.note-editableul.o_checklist>li:not(:has(>ul.o_checklist))');
        if(!$lis.length){
            return;
        }
        varmax=0;
        varids=[];
        $lis.map(function(){
            varchecklistId=parseInt(($(this).attr('id')||'0').replace(/^checklist-id-/,''));
            if(ids.indexOf(checklistId)===-1){
                if(checklistId>max){
                    max=checklistId;
                }
                ids.push(checklistId);
            }else{
                $(this).removeAttr('id');
            }
        });
        $lis.not('[id]').each(function(){
            $(this).attr('id','checklist-id-'+(++max));
        });
    },
    /**
     *AllowsEnterkeypressinatextarea(sourcemode)
     *
     *@private
     *@param{FlectraEvent}ev
     */
    _onKeydown:function(ev){
        if(ev.which===$.ui.keyCode.ENTER){
            ev.stopPropagation();
            return;
        }
        this._super.apply(this,arguments);
    },
    /**
     *Methodcalledwhenwysiwygtriggersachange.
     *
     *@private
     *@param{FlectraEvent}ev
     */
    _onReadonlyClickChecklist:function(ev){
        varself=this;
        if(ev.offsetX>0){
            return;
        }
        ev.stopPropagation();
        ev.preventDefault();
        varchecked=$(ev.target).hasClass('o_checked');
        varchecklistId=parseInt(($(ev.target).attr('id')||'0').replace(/^checklist-id-/,''));

        this._rpc({
            route:'/web_editor/checklist',
            params:{
                res_model:this.model,
                res_id:this.res_id,
                filename:this.name,
                checklistId:checklistId,
                checked:!checked,
            },
        }).then(function(value){
            self._setValue(value);
        });
    },
    /**
     *Methodcalledwhenthewysiwyginstanceisloaded.
     *
     *@private
     */
    _onLoadWysiwyg:function(){
        var$button=this._renderTranslateButton();
        $button.css({
            'font-size':'15px',
            position:'absolute',
            right:'+5px',
            top:'+5px',
        });
        this.$el.append($button);
    },
    /**
     *@private
     *@param{FlectraEvent}ev
     */
    _onWysiwygBlur:function(ev){
        ev.stopPropagation();
        this._doAction();
        if(ev.data.key==='TAB'){
            this.trigger_up('navigation_move',{
                direction:ev.data.shiftKey?'left':'right',
            });
        }
    },
    /**
     *@private
     *@param{FlectraEvent}ev
     */
    _onWysiwygFocus:function(ev){},
});


field_registry.add('html',FieldHtml);


returnFieldHtml;
});
