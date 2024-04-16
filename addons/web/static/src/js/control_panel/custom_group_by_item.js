flectra.define('web.CustomGroupByItem',function(require){
    "usestrict";

    constDropdownMenuItem=require('web.DropdownMenuItem');
    const{useModel}=require('web/static/src/js/model.js');

    /**
     *Groupbygeneratormenu
     *
     *Componentusedtogeneratenewfiltersoftype'groupBy'.Itiscomposed
     *ofabutton(usedtotoggletherenderingoftherestofthecomponent)and
     *aninput(select)usedtochooseanewfieldnamewhichwillbeusedasa
     *newgroupByvalue.
     *@extendsDropdownMenuItem
     */
    classCustomGroupByItemextendsDropdownMenuItem{
        constructor(){
            super(...arguments);

            this.canBeOpened=true;
            this.state.fieldName=this.props.fields[0].name;

            this.model=useModel('searchModel');
        }

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *@private
         */
        _onApply(){
            constfield=this.props.fields.find(f=>f.name===this.state.fieldName);
            this.model.dispatch('createNewGroupBy',field);
            this.state.open=false;
        }
    }

    CustomGroupByItem.template='web.CustomGroupByItem';
    CustomGroupByItem.props={
        fields:Array,
    };

    returnCustomGroupByItem;
});
