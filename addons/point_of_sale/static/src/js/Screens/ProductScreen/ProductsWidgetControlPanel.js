flectra.define('point_of_sale.ProductsWidgetControlPanel',function(require){
    'usestrict';

    const{useRef}=owl.hooks;
    const{debounce}=owl.utils;
    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classProductsWidgetControlPanelextendsPosComponent{
        constructor(){
            super(...arguments);
            this.searchWordInput=useRef('search-word-input');
            this.updateSearch=debounce(this.updateSearch,100);
        }
        clearSearch(){
            this.searchWordInput.el.value='';
            this.trigger('clear-search');
        }
        updateSearch(event){
            this.trigger('update-search',event.target.value);
            if(event.key==='Enter'){
                //WearepassingthesearchWordInputrefsothatwhennecessary,
                //itcanbemodifiedbytheparent.
                this.trigger('try-add-product',{searchWordInput:this.searchWordInput});
            }
        }
    }
    ProductsWidgetControlPanel.template='ProductsWidgetControlPanel';

    Registries.Component.add(ProductsWidgetControlPanel);

    returnProductsWidgetControlPanel;
});
