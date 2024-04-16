flectra.define('website_sale.s_products_searchbar',function(require){
'usestrict';

constconcurrency=require('web.concurrency');
constpublicWidget=require('web.public.widget');

const{qweb}=require('web.core');

/**
 *@todomaybethecustomautocompletelogiccouldbeextracttobereusable
 */
publicWidget.registry.productsSearchBar=publicWidget.Widget.extend({
    selector:'.o_wsale_products_searchbar_form',
    xmlDependencies:['/website_sale/static/src/xml/website_sale_utils.xml'],
    events:{
        'input.search-query':'_onInput',
        'focusout':'_onFocusOut',
        'keydown.search-query':'_onKeydown',
    },
    autocompleteMinWidth:300,

    /**
     *@constructor
     */
    init:function(){
        this._super.apply(this,arguments);

        this._dp=newconcurrency.DropPrevious();

        this._onInput=_.debounce(this._onInput,400);
        this._onFocusOut=_.debounce(this._onFocusOut,100);
    },
    /**
     *@override
     */
    start:function(){
        this.$input=this.$('.search-query');

        this.order=this.$('.o_wsale_search_order_by').val();
        this.limit=parseInt(this.$input.data('limit'));
        this.displayDescription=!!this.$input.data('displayDescription');
        this.displayPrice=!!this.$input.data('displayPrice');
        this.displayImage=!!this.$input.data('displayImage');

        if(this.limit){
            this.$input.attr('autocomplete','off');
        }

        returnthis._super.apply(this,arguments);
    },
    /**
     *@override
     */
    destroy(){
        this._super(...arguments);
        this._render(null);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _adaptToScrollingParent(){
        constbcr=this.el.getBoundingClientRect();
        this.$menu[0].style.setProperty('position','fixed','important');
        this.$menu[0].style.setProperty('top',`${bcr.bottom}px`,'important');
        this.$menu[0].style.setProperty('left',`${bcr.left}px`,'important');
        this.$menu[0].style.setProperty('max-width',`${bcr.width}px`,'important');
        this.$menu[0].style.setProperty('max-height',`${document.body.clientHeight-bcr.bottom-16}px`,'important');
    },
    /**
     *@private
     */
    _fetch:function(){
        returnthis._rpc({
            route:'/shop/products/autocomplete',
            params:{
                'term':this.$input.val(),
                'options':{
                    'order':this.order,
                    'limit':this.limit,
                    'display_description':this.displayDescription,
                    'display_price':this.displayPrice,
                    'max_nb_chars':Math.round(Math.max(this.autocompleteMinWidth,parseInt(this.$el.width()))*0.22),
                },
            },
        });
    },
    /**
     *@private
     */
    _render:function(res){
        if(this._scrollingParentEl){
            this._scrollingParentEl.removeEventListener('scroll',this._menuScrollAndResizeHandler);
            window.removeEventListener('resize',this._menuScrollAndResizeHandler);
            deletethis._scrollingParentEl;
            deletethis._menuScrollAndResizeHandler;
        }

        var$prevMenu=this.$menu;
        this.$el.toggleClass('dropdownshow',!!res);
        if(res){
            varproducts=res['products'];
            this.$menu=$(qweb.render('website_sale.productsSearchBar.autocomplete',{
                products:products,
                hasMoreProducts:products.length<res['products_count'],
                currency:res['currency'],
                widget:this,
            }));

            //TODOadaptdirectlyinthetemplateinmaster
            constmutedItemTextEl=this.$menu.find('span.dropdown-item-text.text-muted')[0];
            if(mutedItemTextEl){
                constnewItemTextEl=document.createElement('span');
                newItemTextEl.classList.add('dropdown-item-text');
                mutedItemTextEl.after(newItemTextEl);
                mutedItemTextEl.classList.remove('dropdown-item-text');
                newItemTextEl.appendChild(mutedItemTextEl);
            }

            this.$menu.css('min-width',this.autocompleteMinWidth);

            //Handlethecasewherethesearchbarisinamegamenubymaking
            //itposition:fixedandforcingitssize.Note:thiscouldbethe
            //defaultbehaviororatleastneededinmorecasesthanthemega
            //menuonly(allscrollingparents).Butasastablefix,itwas
            //easiertofixthatcaseonlyasafirststep,especiallysince
            //thiscannotgenericallyworkonallscrollingparent.
            constmegaMenuEl=this.el.closest('.o_mega_menu');
            if(megaMenuEl){
                constnavbarEl=this.el.closest('.navbar');
                constnavbarTogglerEl=navbarEl?navbarEl.querySelector('.navbar-toggler'):null;
                if(navbarTogglerEl&&navbarTogglerEl.clientWidth<1){
                    this._scrollingParentEl=megaMenuEl;
                    this._menuScrollAndResizeHandler=()=>this._adaptToScrollingParent();
                    this._scrollingParentEl.addEventListener('scroll',this._menuScrollAndResizeHandler);
                    window.addEventListener('resize',this._menuScrollAndResizeHandler);

                    this._adaptToScrollingParent();
                }
            }

            this.$el.append(this.$menu);
        }

        if($prevMenu){
            $prevMenu.remove();
        }
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onInput:function(){
        if(!this.limit){
            return;
        }
        this._dp.add(this._fetch()).then(this._render.bind(this));
    },
    /**
     *@private
     */
    _onFocusOut:function(){
        if(!this.$el.has(document.activeElement).length){
            this._render();
        }
    },
    /**
     *@private
     */
    _onKeydown:function(ev){
        switch(ev.which){
            case$.ui.keyCode.ESCAPE:
                this._render();
                break;
            case$.ui.keyCode.UP:
            case$.ui.keyCode.DOWN:
                ev.preventDefault();
                if(this.$menu){
                    let$element=ev.which===$.ui.keyCode.UP?this.$menu.children().last():this.$menu.children().first();
                    $element.focus();
                }
                break;
        }
    },
});
});
