flectra.define('web_editor.wysiwyg.multizone',function(require){
'usestrict';

varWysiwyg=require('web_editor.wysiwyg');
varsnippetsEditor=require('web_editor.snippet.editor');

/**
 *Show/hidethedropdownsassociatedtothegiventogglesandallowstowait
 *forwhenitisfullyshown/hidden.
 *
 *Note:thisalsotakescareofthefactthe'toggle'methodofbootstrapdoes
 *notproperlyworkinallcases.
 *
 *@param{jQuery}$toggles
 *@param{boolean}[show]
 *@returns{Promise<jQuery>}
 */
functiontoggleDropdown($toggles,show){
    returnPromise.all(_.map($toggles,toggle=>{
        var$toggle=$(toggle);
        var$dropdown=$toggle.parent();
        varshown=$dropdown.hasClass('show');
        if(shown===show){
            return;
        }
        vartoShow=!shown;
        returnnewPromise(resolve=>{
            $dropdown.one(
                toShow?'shown.bs.dropdown':'hidden.bs.dropdown',
                ()=>resolve()
            );
            $toggle.dropdown(toShow?'show':'hide');
        });
    })).then(()=>$toggles);
}

/**
 *HtmlEditor
 *IntendedtoeditHTMLcontent.ThiswidgetusestheWysiwygeditor
 *improvedbyflectra.
 *
 *classeditable:o_editable
 *classnoneditable:o_not_editable
 *
 */
varWysiwygMultizone=Wysiwyg.extend({
    /**
     *@override
     */
    start:function(){
        varself=this;
        this.options.toolbarHandler=$('#web_editor-top-edit');
        this.options.saveElement=function($el,context,withLang){
            varouterHTML=this._getEscapedElement($el).prop('outerHTML');
            returnself._saveElement(outerHTML,self.options.recordInfo,$el[0]);
        };

        //Megamenuinitialization:handledropdownopeningsbyhand
        var$megaMenuToggles=this.$('.o_mega_menu_toggle');
        $megaMenuToggles.removeAttr('data-toggle').dropdown('dispose');
        $megaMenuToggles.on('click.wysiwyg_multizone',ev=>{
            var$toggle=$(ev.currentTarget);

            //Eachtimewetoggleadropdown,wewilldestroythedropdown
            //behaviorafterwardstokeepmanualcontrolofit
            vardispose=($els=>$els.dropdown('dispose'));

            //Firsthideallothermegamenus
            toggleDropdown($megaMenuToggles.not($toggle),false).then(dispose);

            //Thentoggletheclickedone
            toggleDropdown($toggle)
                .then(dispose)
                .then($el=>{
                    varisShown=$el.parent().hasClass('show');
                    this.editor.snippetsMenu.toggleMegaMenuSnippets(isShown);
                });
        });

        //Ensure:blankoe_structureelementsareinfactemptyas':blank'
        //doesnotreallyworkwithallbrowsers.
        for(constelofthis.$('.oe_structure')){
            if(!el.innerHTML.trim()){
                el.innerHTML='';
            }
        }

        //TODOremovethiscodeinmasterbymigratinguserswhodidnot
        //receivetheXMLchangeaboutthe'oe_structure_solo'class(the
        //headeroriginalXMLisnowcorrectbutwechangedspecsafter
        //releasetonotallowmultisnippetsdropzonesintheheader).
        const$headerZones=this._getEditableArea().filter((i,el)=>el.closest('header#top')!==null);
        //oe_structure_multitoeasecustoinstable
        constselector='.oe_structure[id*="oe_structure"]:not(.oe_structure_multi)';
        $headerZones.find(selector).addBack(selector).addClass('oe_structure_solo');

        returnthis._super.apply(this,arguments).then(()=>{
            //ShowingMegaMenusnippetsifonedropdownisalreadyopened
            if(this.$('.o_mega_menu').hasClass('show')){
                this.editor.snippetsMenu.toggleMegaMenuSnippets(true);
            }
        });
    },
    /**
     *@override
     *@returns{Promise}
     */
    save:function(){
        if(this.isDirty()){
            returnthis._restoreMegaMenus()
                .then(()=>this.editor.save(false))
                .then(()=>({isDirty:true}));
        }else{
            returnPromise.resolve({isDirty:false});
        }
    },
    /**
     *@override
     */
    destroy:function(){
        this._restoreMegaMenus();
        this._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    _getEditableArea:function(){
        return$(':o_editable');
    },
    /**
     *@private
     *@param{HTMLElement}editable
     */
    _saveCoverProperties:function(editable){
        varel=editable.closest('.o_record_cover_container');
        if(!el){
            return;
        }

        varresModel=el.dataset.resModel;
        varresID=parseInt(el.dataset.resId);
        if(!resModel||!resID){
            thrownewError('Thereshouldbeamodelandidassociatedtothecover');
        }

        this.__savedCovers=this.__savedCovers||{};
        this.__savedCovers[resModel]=this.__savedCovers[resModel]||[];

        if(this.__savedCovers[resModel].includes(resID)){
            return;
        }
        this.__savedCovers[resModel].push(resID);

        varcssBgImage=$(el.querySelector('.o_record_cover_image')).css('background-image');
        varcoverProps={
            'background-image':cssBgImage.replace(/"/g,'').replace(window.location.protocol+"//"+window.location.host,''),
            'background_color_class':el.dataset.bgColorClass,
            'background_color_style':el.dataset.bgColorStyle,
            'opacity':el.dataset.filterValue,
            'resize_class':el.dataset.coverClass,
            'text_align_class':el.dataset.textAlignClass,
        };

        returnthis._rpc({
            model:resModel,
            method:'write',
            args:[
                resID,
                {'cover_properties':JSON.stringify(coverProps)}
            ],
        });
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
    _saveElement:function(outerHTML,recordInfo,editable){
        varpromises=[];

        var$el=$(editable);

        //Savingaviewcontent
        varviewID=$el.data('oe-id');
        if(viewID){
            promises.push(this._rpc({
                model:'ir.ui.view',
                method:'save',
                args:[
                    viewID,
                    outerHTML,
                    $el.data('oe-xpath')||null,
                ],
                context:recordInfo.context,
            }));
        }

        //Savingmegamenuoptions
        if($el.data('oe-field')==='mega_menu_content'){
            //Ontopofsavingthemegamenucontentlikeanyotherfield
            //content,wemustsavethecustomclassesthatweresetonthe
            //menuitself.
            //FIXMEnormallyremovingthe'show'classshouldnotbenecessaryhere
            //TODOcheckthateditorclassesareremovedhereaswell
            varclasses=_.without($el.attr('class').split(''),'dropdown-menu','o_mega_menu','show');
            promises.push(this._rpc({
                model:'website.menu',
                method:'write',
                args:[
                    [parseInt($el.data('oe-id'))],
                    {
                        'mega_menu_classes':classes.join(''),
                    },
                ],
            }));
        }

        //Savingcoverpropertiesonrelatedmodelifany
        varprom=this._saveCoverProperties(editable);
        if(prom){
            promises.push(prom);
        }

        returnPromise.all(promises);
    },
    /**
     *Restoresmegamenubehaviorsandclosesthem(importanttodobefore
     *savingotherwisetheywouldbesavedopened).
     *
     *@private
     *@returns{Promise}
     */
    _restoreMegaMenus:function(){
        var$megaMenuToggles=this.$('.o_mega_menu_toggle');
        $megaMenuToggles.off('.wysiwyg_multizone')
            .attr('data-toggle','dropdown')
            .dropdown({});
        returntoggleDropdown($megaMenuToggles,false);
    },
});

snippetsEditor.Class.include({
    /**
     *@private
     *@param{boolean}show
     */
    toggleMegaMenuSnippets:function(show){
        setTimeout(()=>this._activateSnippet(false));
        this._showMegaMenuSnippets=show;
        this._filterSnippets();
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _filterSnippets(search){
        this._super(...arguments);
        if(!this._showMegaMenuSnippets){
            this.el.querySelector('#snippet_mega_menu').classList.add('d-none');
        }
    },
    /**
     *@override
     */
    _insertDropzone:function($hook){
        var$hookParent=$hook.parent();
        var$dropzone=this._super(...arguments);
        $dropzone.attr('data-editor-message',$hookParent.attr('data-editor-message'));
        $dropzone.attr('data-editor-sub-message',$hookParent.attr('data-editor-sub-message'));
        return$dropzone;
    },
});

returnWysiwygMultizone;
});
