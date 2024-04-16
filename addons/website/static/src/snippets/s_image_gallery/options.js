flectra.define('website.s_image_gallery_options',function(require){
'usestrict';

varcore=require('web.core');
varweWidgets=require('wysiwyg.widgets');
varoptions=require('web_editor.snippets.options');
constwUtils=require("website.utils");

var_t=core._t;
varqweb=core.qweb;

options.registry.gallery=options.Class.extend({
    xmlDependencies:['/website/static/src/snippets/s_image_gallery/000.xml'],

    /**
     *@override
     */
    start:function(){
        varself=this;

        //Makesureimagepreviewsareupdatedifimagesarechanged
        this.$target.on('image_changed.gallery','img',function(ev){
            var$img=$(ev.currentTarget);
            varindex=self.$target.find('.carousel-item.active').index();
            self.$('.carousel:firstli[data-target]:eq('+index+')')
                .css('background-image','url('+$img.attr('src')+')');
        });

        //Whenthesnippetisempty,aneditionbuttonisthedefaultcontent
        //TODOfindanicerwaytodothattohaveeditorstyle
        this.$target.on('click.gallery','.o_add_images',function(e){
            e.stopImmediatePropagation();
            self.addImages(false);
        });

        this.$target.on('dropped.gallery','img',function(ev){
            self.mode(null,self.getMode());
            if(!ev.target.height){
                $(ev.target).one('load',function(){
                    setTimeout(function(){
                        self.trigger_up('cover_update');
                    });
                });
            }
        });

        const$container=this.$('>.container,>.container-fluid,>.o_container_small');
        letlayoutPromise;
        if($container.find('>*:not(div)').length){
            layoutPromise=self._modeWithImageWait(null,self.getMode());
        }else{
            layoutPromise=Promise.resolve();
        }

        returnlayoutPromise.then(this._super.apply(this,arguments));
    },
    /**
     *@override
     */
    onBuilt:function(){
        if(this.$target.find('.o_add_images').length){
            this.addImages(false);
        }
        //TODOshouldconsidertheasyncparts
        this._adaptNavigationIDs();
    },
    /**
     *@override
     */
    onClone:function(){
        this._adaptNavigationIDs();
    },
    /**
     *@override
     */
    cleanForSave:function(){
        if(this.$target.hasClass('slideshow')){
            this.$target.removeAttr('style');
        }
    },
    /**
     *@override
     */
    destroy(){
        this._super(...arguments);
        this.$target.off('.gallery');
    },

    //--------------------------------------------------------------------------
    //Options
    //--------------------------------------------------------------------------

    /**
     *Allowstoselectimagestoaddaspartofthesnippet.
     *
     *@seethis.selectClassforparameters
     */
    addImages:function(previewMode){
        //Preventopeningdialogtwice.
        if(this.__imageDialogOpened){
            returnPromise.resolve();
        }
        this.__imageDialogOpened=true;
        const$images=this.$('img');
        var$container=this.$('>.container,>.container-fluid,>.o_container_small');
        vardialog=newweWidgets.MediaDialog(this,{multiImages:true,onlyImages:true,mediaWidth:1920});
        varlastImage=_.last(this._getImages());
        varindex=lastImage?this._getIndex(lastImage):-1;
        returnnewPromise(resolve=>{
            letsavedPromise=Promise.resolve();
            dialog.on('save',this,function(attachments){
                for(vari=0;i<attachments.length;i++){
                    $('<img/>',{
                        class:$images.length>0?$images[0].className:'imgimg-fluidd-block',
                        src:attachments[i].image_src,
                        'data-index':++index,
                        alt:attachments[i].description||'',
                        'data-name':_t('Image'),
                        style:$images.length>0?$images[0].style.cssText:'',
                    }).appendTo($container);
                }
                if(attachments.length>0){
                    savedPromise=this._modeWithImageWait('reset',this.getMode()).then(()=>{
                        this.trigger_up('cover_update');
                    });
                }
            });
            dialog.on('closed',this,()=>{
                this.__imageDialogOpened=false;
                returnsavedPromise.then(resolve);
            });
            dialog.open();
        });
    },
    /**
     *Allowstochangethenumberofcolumnswhendisplayingimageswitha
     *grid-likelayout.
     *
     *@seethis.selectClassforparameters
     */
    columns:function(previewMode,widgetValue,params){
        constnbColumns=parseInt(widgetValue||'1');
        this.$target.attr('data-columns',nbColumns);

        //TODOInmasterreturnmode'sresult.
        this.mode(previewMode,this.getMode(),{});//TODOimprove
    },
    /**
     *Gettheimagetarget'slayoutmode(slideshow,masonry,gridornomode).
     *
     *@returns{String('slideshow'|'masonry'|'grid'|'nomode')}
     */
    getMode:function(){
        varmode='slideshow';
        if(this.$target.hasClass('o_masonry')){
            mode='masonry';
        }
        if(this.$target.hasClass('o_grid')){
            mode='grid';
        }
        if(this.$target.hasClass('o_nomode')){
            mode='nomode';
        }
        returnmode;
    },
    /**
     *Displaystheimageswiththe"grid"layout.
     */
    grid:function(){
        varimgs=this._getImages();
        var$row=$('<div/>',{class:'rows_nb_column_fixed'});
        varcolumns=this._getColumns();
        varcolClass='col-lg-'+(12/columns);
        var$container=this._replaceContent($row);

        _.each(imgs,function(img,index){
            var$img=$(img);
            var$col=$('<div/>',{class:colClass});
            $col.append($img).appendTo($row);
            if((index+1)%columns===0){
                $row=$('<div/>',{class:'rows_nb_column_fixed'});
                $row.appendTo($container);
            }
        });
        this.$target.css('height','');
    },
    /**
     *Displaystheimageswiththe"masonry"layout.
     */
    masonry:function(){
        varself=this;
        varimgs=this._getImages();
        varcolumns=this._getColumns();
        varcolClass='col-lg-'+(12/columns);
        varcols=[];

        var$row=$('<div/>',{class:'rows_nb_column_fixed'});
        this._replaceContent($row);

        //Createcolumns
        for(varc=0;c<columns;c++){
            var$col=$('<div/>',{class:'o_masonry_colo_snippet_not_selectable'+colClass});
            $row.append($col);
            cols.push($col[0]);
        }

        //Dispatchimagesincolumnsbyalwaysputtingthenextoneinthe
        //smallest-heightcolumn
        if(this._masonryAwaitImages){
            //TODOInmasterreturnpromise.
            this._masonryAwaitImagesPromise=newPromise(asyncresolve=>{
                for(constimgElofimgs){
                    letmin=Infinity;
                    letsmallestColEl;
                    for(constcolElofcols){
                        constimgEls=colEl.querySelectorAll("img");
                        constlastImgRect=imgEls.length&&imgEls[imgEls.length-1].getBoundingClientRect();
                        constheight=lastImgRect?Math.round(lastImgRect.top+lastImgRect.height):0;
                        if(height<min){
                            min=height;
                            smallestColEl=colEl;
                        }
                    }
                    smallestColEl.append(imgEl);
                    awaitwUtils.onceAllImagesLoaded(this.$target);
                }
                resolve();
            });
            return;
        }
        //TODORemoveinmaster.
        //Ordermightbewrongifimageswerenotloadedyet.
        while(imgs.length){
            varmin=Infinity;
            var$lowest;
            _.each(cols,function(col){
                var$col=$(col);
                varheight=$col.is(':empty')?0:$col.find('img').last().offset().top+$col.find('img').last().height()-self.$target.offset().top;
                //Neutralizeinvisiblesub-pixelheightdifferences.
                height=Math.round(height);
                if(height<min){
                    min=height;
                    $lowest=$col;
                }
            });
            $lowest.append(imgs.shift());
        }
    },
    /**
     *Allowstochangetheimageslayout.@seegrid,masonry,nomode,slideshow
     *
     *@seethis.selectClassforparameters
     */
    mode:function(previewMode,widgetValue,params){
        widgetValue=widgetValue||'slideshow';//FIXMEshouldnotbeneeded
        this.$target.css('height','');
        this.$target
            .removeClass('o_nomodeo_masonryo_grido_slideshow')
            .addClass('o_'+widgetValue);
        this[widgetValue]();
        this.trigger_up('cover_update');
        this._refreshPublicWidgets();
    },
    /**
     *Displaystheimageswiththestandardlayout:floatingimages.
     */
    nomode:function(){
        var$row=$('<div/>',{class:'rows_nb_column_fixed'});
        varimgs=this._getImages();

        this._replaceContent($row);

        _.each(imgs,function(img){
            varwrapClass='col-lg-3';
            if(img.width>=img.height*2||img.width>600){
                wrapClass='col-lg-6';
            }
            var$wrap=$('<div/>',{class:wrapClass}).append(img);
            $row.append($wrap);
        });
    },
    /**
     *Allowstoremoveallimages.Restoresthesnippettothewayitwaswhen
     *itwasaddedinthepage.
     *
     *@seethis.selectClassforparameters
     */
    removeAllImages:function(previewMode){
        var$addImg=$('<div>',{
            class:'alertalert-infocss_non_editable_mode_hiddentext-center',
        });
        var$text=$('<span>',{
            class:'o_add_images',
            style:'cursor:pointer;',
            text:_t("AddImages"),
        });
        var$icon=$('<i>',{
            class:'fafa-plus-circle',
        });
        this._replaceContent($addImg.append($icon).append($text));
    },
    /**
     *Displaystheimageswitha"slideshow"layout.
     */
    slideshow:function(){
        constimageEls=this._getImages();
        constimages=_.map(imageEls,img=>({
            //UsegetAttributetogettheattributevalueotherwise.src
            //returnstheabsoluteurl.
            src:img.getAttribute('src'),
            alt:img.getAttribute('alt'),
        }));
        varcurrentInterval=this.$target.find('.carousel:first').attr('data-interval');
        varparams={
            images:images,
            index:0,
            title:"",
            interval:currentInterval||0,
            id:'slideshow_'+newDate().getTime(),
            attrClass:imageEls.length>0?imageEls[0].className:'',
            attrStyle:imageEls.length>0?imageEls[0].style.cssText:'',
        },
        $slideshow=$(qweb.render('website.gallery.slideshow',params));
        this._replaceContent($slideshow);
        _.each(this.$('img'),function(img,index){
            $(img).attr({contenteditable:true,'data-index':index});
        });
        this.$target.css('height',Math.round(window.innerHeight*0.7));

        //Applylayoutanimation
        this.$target.off('slide.bs.carousel').off('slid.bs.carousel');
        this.$('li.fa').off('click');
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Handlesimageremovalsandimageindexupdates.
     *
     *@override
     */
    notify:function(name,data){
        this._super(...arguments);
        //TODOInmaster:nestinasnippet_edition_requesttoawaitmode.
        if(name==='image_removed'){
            data.$image.remove();//Forcetheremovaloftheimagebeforereset
            //TODOIn16.0:use_modeWithImageWait.
            this.mode('reset',this.getMode());
        }elseif(name==='image_index_request'){
            varimgs=this._getImages();
            varposition=_.indexOf(imgs,data.$image[0]);
            if(position===0&&data.position==="prev"){
                data.position="last";
            }elseif(position===imgs.length-1&&data.position==="next"){
                data.position="first";
            }
            imgs.splice(position,1);
            switch(data.position){
                case'first':
                    imgs.unshift(data.$image[0]);
                    break;
                case'prev':
                    imgs.splice(position-1,0,data.$image[0]);
                    break;
                case'next':
                    imgs.splice(position+1,0,data.$image[0]);
                    break;
                case'last':
                    imgs.push(data.$image[0]);
                    break;
            }
            position=imgs.indexOf(data.$image[0]);
            _.each(imgs,function(img,index){
                //Note:theremightbemoreefficientwaystodothatbutitis
                //moresimplethiswayandallowscompatibilitywith10.0where
                //indexeswerenotthesameaspositions.
                $(img).attr('data-index',index);
            });
            constcurrentMode=this.getMode();
            //TODOIn16.0:use_modeWithImageWait.
            this.mode('reset',currentMode);
            if(currentMode==='slideshow'){
                const$carousel=this.$target.find('.carousel');
                $carousel.removeClass('slide');
                $carousel.carousel(position);
                this.$target.find('.carousel-indicatorsli').removeClass('active');
                this.$target.find('.carousel-indicatorsli[data-slide-to="'+position+'"]').addClass('active');
                this.trigger_up('activate_snippet',{
                    $snippet:this.$target.find('.carousel-item.activeimg'),
                    ifInactiveOptions:true,
                });
                $carousel.addClass('slide');
            }else{
                this.trigger_up('activate_snippet',{
                    $snippet:data.$image,
                    ifInactiveOptions:true,
                });
            }
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _adaptNavigationIDs:function(){
        varuuid=newDate().getTime();
        this.$target.find('.carousel').attr('id','slideshow_'+uuid);
        _.each(this.$target.find('[data-slide],[data-slide-to]'),function(el){
            var$el=$(el);
            if($el.attr('data-target')){
                $el.attr('data-target','#slideshow_'+uuid);
            }elseif($el.attr('href')){
                $el.attr('href','#slideshow_'+uuid);
            }
        });
    },
    /**
     *@override
     */
    _computeWidgetState:function(methodName,params){
        switch(methodName){
            case'mode':{
                letactiveModeName='slideshow';
                for(constmodeNameofparams.possibleValues){
                    if(this.$target.hasClass(`o_${modeName}`)){
                        activeModeName=modeName;
                        break;
                    }
                }
                this.activeMode=activeModeName;
                returnactiveModeName;
            }
            case'columns':{
                return`${this._getColumns()}`;
            }
        }
        returnthis._super(...arguments);
    },
    /**
     *@private
     */
    async_computeWidgetVisibility(widgetName,params){
        if(widgetName==='slideshow_mode_opt'){
            returnfalse;
        }
        returnthis._super(...arguments);
    },
    /**
     *Returnstheimages,sortedbyindex.
     *
     *@private
     *@returns{DOMElement[]}
     */
    _getImages:function(){
        varimgs=this.$('img').get();
        varself=this;
        imgs.sort(function(a,b){
            returnself._getIndex(a)-self._getIndex(b);
        });
        returnimgs;
    },
    /**
     *Returnstheindexassociatedtoagivenimage.
     *
     *@private
     *@param{DOMElement}img
     *@returns{integer}
     */
    _getIndex:function(img){
        returnimg.dataset.index||0;
    },
    /**
     *Returnsthecurrentlyselectedcolumnoption.
     *
     *@private
     *@returns{integer}
     */
    _getColumns:function(){
        returnparseInt(this.$target.attr('data-columns'))||3;
    },
    /**
     *Emptiesthecontainer,addsthegivencontentandreturnsthecontainer.
     *
     *@private
     *@param{jQuery}$content
     *@returns{jQuery}themaincontainerofthesnippet
     */
    _replaceContent:function($content){
        var$container=this.$('>.container,>.container-fluid,>.o_container_small');
        $container.empty().append($content);
        return$container;
    },
    /**
     *Callmodewhileensuringthatallimagesareloaded.
     *
     *@seethis.selectClassforparameters
     *@returns{Promise}
     */
    _modeWithImageWait(previewMode,widgetValue,params){
        //TODORemoveinmaster.
        letpromise;
        this._masonryAwaitImages=true;
        try{
            this.mode(previewMode,widgetValue,params);
            promise=this._masonryAwaitImagesPromise;
        }finally{
            this._masonryAwaitImages=false;
            this._masonryAwaitImagesPromise=undefined;
        }
        returnpromise||Promise.resolve();
    },
});

options.registry.gallery_img=options.Class.extend({
    /**
     *Rebuildsthewholegallerywhenoneimageisremoved.
     *
     *@override
     */
    onRemove:function(){
        this.trigger_up('option_update',{
            optionName:'gallery',
            name:'image_removed',
            data:{
                $image:this.$target,
            },
        });
    },

    //--------------------------------------------------------------------------
    //Options
    //--------------------------------------------------------------------------

    /**
     *Allowstochangethepositionofanimage(itsorderintheimageset).
     *
     *@seethis.selectClassforparameters
     */
    position:function(previewMode,widgetValue,params){
        this.trigger_up('option_update',{
            optionName:'gallery',
            name:'image_index_request',
            data:{
                $image:this.$target,
                position:widgetValue,
            },
        });
    },
});
});
