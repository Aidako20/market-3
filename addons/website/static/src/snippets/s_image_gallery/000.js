flectra.define('website.s_image_gallery',function(require){
'usestrict';

varcore=require('web.core');
varpublicWidget=require('web.public.widget');

varqweb=core.qweb;

constGalleryWidget=publicWidget.Widget.extend({

    selector:'.s_image_gallery:not(.o_slideshow)',
    xmlDependencies:['/website/static/src/snippets/s_image_gallery/000.xml'],
    events:{
        'clickimg':'_onClickImg',
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Calledwhenanimageisclicked.Opensadialogtobrowsealltheimages
     *withabiggersize.
     *
     *@private
     *@param{Event}ev
     */
    _onClickImg:function(ev){
        if(this.$modal||ev.currentTarget.matches("a>img")){
            return;
        }
        varself=this;
        var$cur=$(ev.currentTarget);

        var$images=$cur.closest('.s_image_gallery').find('img');
        varsize=0.8;
        vardimensions={
            min_width:Math.round(window.innerWidth*size*0.9),
            min_height:Math.round(window.innerHeight*size),
            max_width:Math.round(window.innerWidth*size*0.9),
            max_height:Math.round(window.innerHeight*size),
            width:Math.round(window.innerWidth*size*0.9),
            height:Math.round(window.innerHeight*size)
        };

        var$img=($cur.is('img')===true)?$cur:$cur.closest('img');

        constmilliseconds=$cur.closest('.s_image_gallery').data('interval')||false;
        this.$modal=$(qweb.render('website.gallery.slideshow.lightbox',{
            images:$images.get(),
            index:$images.index($img),
            dim:dimensions,
            interval:milliseconds||0,
            id:_.uniqueId('slideshow_'),
        }));
        this.$modal.modal({
            keyboard:true,
            backdrop:true,
        });
        this.$modal.on('hidden.bs.modal',function(){
            $(this).hide();
            $(this).siblings().filter('.modal-backdrop').remove();//bootstrapleavesamodal-backdrop
            $(this).remove();
            self.$modal=undefined;
        });
        this.$modal.find('.modal-content,.modal-body.o_slideshow').css('height','100%');
        this.$modal.appendTo(document.body);

        this.$modal.one('shown.bs.modal',function(){
            self.trigger_up('widgets_start_request',{
                editableMode:false,
                $target:self.$modal.find('.modal-body.o_slideshow'),
            });
        });
    },
});

constGallerySliderWidget=publicWidget.Widget.extend({
    selector:'.o_slideshow',
    xmlDependencies:['/website/static/src/snippets/s_image_gallery/000.xml'],
    disabledInEditableMode:false,

    /**
     *@override
     */
    start:function(){
        varself=this;
        this.$carousel=this.$target.is('.carousel')?this.$target:this.$target.find('.carousel');
        this.$indicator=this.$carousel.find('.carousel-indicators');
        this.$prev=this.$indicator.find('li.o_indicators_left').css('visibility','');//forcevisibilityassomedatabaseshaveithidden
        this.$next=this.$indicator.find('li.o_indicators_right').css('visibility','');
        var$lis=this.$indicator.find('li[data-slide-to]');
        letindicatorWidth=this.$indicator.width();
        if(indicatorWidth===0){
            //Anancestormaybehiddensowetrytofinditandmakeit
            //visiblejusttotakethecorrectwidth.
            const$indicatorParent=this.$indicator.parents().not(':visible').last();
            if(!$indicatorParent[0].style.display){
                $indicatorParent[0].style.display='block';
                indicatorWidth=this.$indicator.width();
                $indicatorParent[0].style.display='';
            }
        }
        letnbPerPage=Math.floor(indicatorWidth/$lis.first().outerWidth(true))-3;//-navigator-1toleavesomespace
        varrealNbPerPage=nbPerPage||1;
        varnbPages=Math.ceil($lis.length/realNbPerPage);

        varindex;
        varpage;
        update();

        functionhide(){
            $lis.each(function(i){
                $(this).toggleClass('d-none',i<page*nbPerPage||i>=(page+1)*nbPerPage);
            });
            if(page<=0){
                self.$prev.detach();
            }else{
                self.$prev.removeClass('d-none');
                self.$prev.prependTo(self.$indicator);
            }
            if(page>=nbPages-1){
                self.$next.detach();
            }else{
                self.$next.removeClass('d-none');
                self.$next.appendTo(self.$indicator);
            }
        }

        functionupdate(){
            constactive=$lis.filter('.active');
            index=active.length?$lis.index(active):0;
            page=Math.floor(index/realNbPerPage);
            hide();
        }

        this.$carousel.on('slide.bs.carousel.gallery_slider',function(){
            setTimeout(function(){
                var$item=self.$carousel.find('.carousel-inner.carousel-item-prev,.carousel-inner.carousel-item-next');
                varindex=$item.index();
                $lis.removeClass('active')
                    .filter('[data-slide-to="'+index+'"]')
                    .addClass('active');
            },0);
        });
        this.$indicator.on('click.gallery_slider','>li:not([data-slide-to])',function(){
            page+=($(this).hasClass('o_indicators_left')?-1:1);
            page=Math.max(0,Math.min(nbPages-1,page));//shouldnotbenecessary
            self.$carousel.carousel(page*realNbPerPage);
            //Wedontusehide()beforetheslideanimationintheeditorbecausethereisatraceback
            //TODO:fixthistraceback
            if(!self.editableMode){
                hide();
            }
        });
        this.$carousel.on('slid.bs.carousel.gallery_slider',update);

        returnthis._super.apply(this,arguments);
    },
    /**
     *@override
     */
    destroy:function(){
        this._super.apply(this,arguments);

        if(!this.$indicator){
            return;
        }

        this.$prev.prependTo(this.$indicator);
        this.$next.appendTo(this.$indicator);
        this.$carousel.off('.gallery_slider');
        this.$indicator.off('.gallery_slider');
    },
});

publicWidget.registry.gallery=GalleryWidget;
publicWidget.registry.gallerySlider=GallerySliderWidget;

return{
    GalleryWidget:GalleryWidget,
    GallerySliderWidget:GallerySliderWidget,
};
});
