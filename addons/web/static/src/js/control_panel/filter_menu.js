flectra.define('web.FilterMenu',function(require){
    "usestrict";

    constCustomFilterItem=require('web.CustomFilterItem');
    constDropdownMenu=require('web.DropdownMenu');
    const{FACET_ICONS}=require("web.searchUtils");
    const{useModel}=require('web/static/src/js/model.js');

    /**
     *'Filters'menu
     *
     *Simplerenderingofthefiltersoftype`filter`givenbythecontrolpanel
     *model.ItusesmostofthebehavioursimplementedbythedropdownmenuComponent,
     *withtheadditionofafiltergenerator(@seeCustomFilterItem).
     *@seeDropdownMenuforadditionaldetails.
     *@extendsDropdownMenu
     */
    classFilterMenuextendsDropdownMenu{

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
            returnFACET_ICONS.filter;
        }

        /**
         *@override
         */
        getitems(){
            returnthis.model.get('filters',f=>f.type==='filter');
        }

        /**
         *@override
         */
        gettitle(){
            returnthis.env._t("Filters");
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
            const{item,option}=ev.detail;
            if(option){
                this.model.dispatch('toggleFilterWithOptions',item.id,option.id);
            }else{
                this.model.dispatch('toggleFilter',item.id);
            }
        }
    }

    FilterMenu.components=Object.assign({},DropdownMenu.components,{
        CustomFilterItem,
    });
    FilterMenu.props=Object.assign({},DropdownMenu.props,{
        fields:Object,
    });
    FilterMenu.template='web.FilterMenu';

    returnFilterMenu;
});
