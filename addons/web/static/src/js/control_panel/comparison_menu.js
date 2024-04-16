flectra.define("web.ComparisonMenu",function(require){
    "usestrict";

    constDropdownMenu=require("web.DropdownMenu");
    const{FACET_ICONS}=require("web.searchUtils");
    const{useModel}=require("web/static/src/js/model.js");

    /**
     *"Comparison"menu
     *
     *Displaysasetofcomparisonoptionsrelatedtothecurrentlyselected
     *datefilters.
     *@extendsDropdownMenu
     */
    classComparisonMenuextendsDropdownMenu{
        constructor(){
            super(...arguments);
            this.model=useModel('searchModel');
        }

        //---------------------------------------------------------------------
        //Getters
        //---------------------------------------------------------------------

        /**
         *@override
         */
        geticon(){
            returnFACET_ICONS.comparison;
        }

        /**
         *@override
         */
        getitems(){
            returnthis.model.get('filters',f=>f.type==='comparison');
        }

        /**
         *@override
         */
        gettitle(){
            returnthis.env._t("Comparison");
        }

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *@private
         *@param{OwlEvent}ev
         */
        _onItemSelected(ev){
            ev.stopPropagation();
            const{item}=ev.detail;
            this.model.dispatch("toggleComparison",item.id);
        }

    }

    returnComparisonMenu;
});
