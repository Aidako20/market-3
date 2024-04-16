flectra.define('web.GroupByMenu',function(require){
    "usestrict";

    constCustomGroupByItem=require('web.CustomGroupByItem');
    constDropdownMenu=require('web.DropdownMenu');
    const{FACET_ICONS,GROUPABLE_TYPES}=require('web.searchUtils');
    const{useModel}=require('web/static/src/js/model.js');

    /**
     *'Groupby'menu
     *
     *Simplerenderingofthefiltersoftype`groupBy`givenbythecontrolpanel
     *model.ItusesmostofthebehavioursimplementedbythedropdownmenuComponent,
     *withtheadditionofagroupByfiltergenerator(@seeCustomGroupByItem).
     *@seeDropdownMenuforadditionaldetails.
     *@extendsDropdownMenu
     */
    classGroupByMenuextendsDropdownMenu{

        constructor(){
            super(...arguments);

            this.fields=Object.values(this.props.fields)
                .filter(field=>this._validateField(field))
                .sort(({string:a},{string:b})=>a>b?1:a<b?-1:0);

            this.model=useModel('searchModel');
        }

        //---------------------------------------------------------------------
        //Getters
        //---------------------------------------------------------------------

        /**
         *@override
         */
        geticon(){
            returnFACET_ICONS.groupBy;
        }

        /**
         *@override
         */
        getitems(){
            returnthis.model.get('filters',f=>f.type==='groupBy');
        }

        /**
         *@override
         */
        gettitle(){
            returnthis.env._t("GroupBy");
        }

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *@private
         *@param{Object}field
         *@returns{boolean}
         */
        _validateField(field){
            returnfield.sortable&&
                field.name!=="id"&&
                GROUPABLE_TYPES.includes(field.type);
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

    GroupByMenu.components=Object.assign({},DropdownMenu.components,{
        CustomGroupByItem,
    });
    GroupByMenu.props=Object.assign({},DropdownMenu.props,{
        fields:Object,
    });
    GroupByMenu.template='web.GroupByMenu';

    returnGroupByMenu;
});
