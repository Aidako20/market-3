flectra.define('web.CustomFilterItem',function(require){
    "usestrict";

    const{DatePicker,DateTimePicker}=require('web.DatePickerOwl');
    constDomain=require('web.Domain');
    constDropdownMenuItem=require('web.DropdownMenuItem');
    const{FIELD_OPERATORS,FIELD_TYPES}=require('web.searchUtils');
    constfield_utils=require('web.field_utils');
    constpatchMixin=require('web.patchMixin');
    const{useModel}=require('web/static/src/js/model.js');

    /**
     *Filtergeneratormenu
     *
     *Componentwhichpurposeistogeneratenewfiltersfromasetofinputs.
     *Itismadeofoneorseveral`condition`objectsthatwillbeusedtogenerate
     *filterswhichwillbeaddedinthefiltermenu.Eachconditioniscomposed
     *of2,3or4inputs:
     *
     *1.FIELD(select):thefieldusedtoformthebaseofthedomaincondition;
     *
     *2.OPERATOR(select):thesymboldeterminingtheoperator(s)ofthedomain
     *                      condition,linkingthefieldtooneorseveralvalue(s).
     *                      Someoperatorscanhavepre-definedvaluesthatwillreplaceuserinputs.
     *                      @seesearchUtilsforthelistofoperators.
     *
     *3.[VALUE](input|select):thevalueofthedomaincondition.itwillbeparsed
     *                           accordingtotheselectedfield'stype.Notethat
     *                           itisoptionalassomeoperatorshavedefinedvalues.
     *                           Thegeneratedconditiondomainwillbeasfollowing:
     *                           [
     *                               [field,operator,(operator_value|input_value)]
     *                           ]
     *
     *4.[VALUE](input):fornow,onlydate-typedfieldswiththe'between'operator
     *                    allowforasecondvalue.Thegiveninputvalueswillthen
     *                    betakenasthebordersofthedaterange(betweenxandy)
     *                    andwillbetranslatedasthefollowingdomainform:
     *                    [
     *                        [date_field,'>=',x],
     *                        [date_field,'<=',y],
     *                    ]
     *@extendsDropdownMenuItem
     */
    classCustomFilterItemextendsDropdownMenuItem{
        constructor(){
            super(...arguments);

            this.model=useModel('searchModel');

            this.canBeOpened=true;
            this.state.conditions=[];
            //Format,filterandsortthefieldsprops
            this.fields=Object.values(this.props.fields)
                .filter(field=>this._validateField(field))
                .concat({string:'ID',type:'id',name:'id'})
                .sort(({string:a},{string:b})=>a>b?1:a<b?-1:0);

            //Giveaccesstoconstantsvariablestothetemplate.
            this.DECIMAL_POINT=this.env._t.database.parameters.decimal_point;
            this.OPERATORS=FIELD_OPERATORS;
            this.FIELD_TYPES=FIELD_TYPES;

            //Adddefaultemptycondition
            this._addDefaultCondition();
        }

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *Populatetheconditionslistwithadefaultconditionhavingasproperties:
         *-thefirstavailablefield
         *-thefirstavailableoperator
         *-anulloremptyarrayvalue
         *@private
         */
        _addDefaultCondition(){
            constcondition={
                field:0,
                operator:0,
            };
            this._setDefaultValue(condition);
            this.state.conditions.push(condition);
        }

        /**
         *@private
         *@param{Object}field
         *@returns{boolean}
         */
        _validateField(field){
            return!field.deprecated&&
                field.searchable&&
                FIELD_TYPES[field.type]&&
                field.name!=='id';
        }

        /**
         *@private
         *@param{Object}condition
         */
        _setDefaultValue(condition){
            constfieldType=this.fields[condition.field].type;
            constgenericType=FIELD_TYPES[fieldType];
            constoperator=FIELD_OPERATORS[genericType][condition.operator];
            //Logicalvalue
            switch(genericType){
                case'id':
                case'number':
                    condition.value=0;
                    break;
                case'date':
                    condition.value=[moment()];
                    if(operator.symbol==='between'){
                        condition.value.push(moment());
                    }
                    break;
                case'datetime':
                    condition.value=[moment('00:00:00','hh:mm:ss').utcOffset(0,true)];
                    if(operator.symbol==='between'){
                        condition.value.push(moment('23:59:59','hh:mm:ss').utcOffset(0,true));
                    }
                    break;
                case'selection':
                    if(this.fields[condition.field].selection.length){
                        const[firstValue]=this.fields[condition.field].selection[0];
                        condition.value=firstValue;
                    }
                    else{
                        condition.value="";
                    }
                    break;
                default:
                    condition.value="";
            }
            //Displayedvalue
            if(["float","monetary"].includes(fieldType)){
                condition.displayedValue=`0${this.DECIMAL_POINT}0`;
            }else{
                condition.displayedValue=String(condition.value);
            }
        }

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *Convertallconditionstoprefilters.
         *@private
         */
        _onApply(){
            constpreFilters=this.state.conditions.map(condition=>{
                constfield=this.fields[condition.field];
                consttype=this.FIELD_TYPES[field.type];
                constoperator=this.OPERATORS[type][condition.operator];
                constdescriptionArray=[field.string,operator.description];
                constdomainArray=[];
                letdomainValue;
                //Fieldtypespecifics
                if('value'inoperator){
                    domainValue=[operator.value];
                    //Nodescriptiontopushhere
                }elseif(['date','datetime'].includes(type)){
                    domainValue=condition.value.map(
                        val=>field_utils.parse[type](val,{type},{timezone:true})
                    );
                    constdateValue=condition.value.map(
                        val=>field_utils.format[type](val,{type},{timezone:false})
                    );
                    descriptionArray.push(`"${dateValue.join(""+this.env._t("and")+"")}"`);
                }elseif(type==="selection"){
                    domainValue=[condition.value];
                    constformattedValue=field_utils.format[type](condition.value,field);
                    descriptionArray.push(`"${formattedValue}"`);
                }else{
                    domainValue=[condition.value];
                    descriptionArray.push(`"${condition.value}"`);
                }
                //Operatorspecifics
                if(operator.symbol==='between'){
                    domainArray.push(
                        [field.name,'>=',domainValue[0]],
                        [field.name,'<=',domainValue[1]]
                    );
                }else{
                    domainArray.push([field.name,operator.symbol,domainValue[0]]);
                }
                constpreFilter={
                    description:descriptionArray.join(""),
                    domain:Domain.prototype.arrayToString(domainArray),
                    type:'filter',
                };
                returnpreFilter;
            });

            this.model.dispatch('createNewFilters',preFilters);

            //Resetstate
            this.state.open=false;
            this.state.conditions=[];
            this._addDefaultCondition();
        }

        /**
         *@private
         *@param{Object}condition
         *@param{number}valueIndex
         *@param{OwlEvent}ev
         */
        _onDateChanged(condition,valueIndex,ev){
            condition.value[valueIndex]=ev.detail.date;
        }

        /**
         *@private
         *@param{Object}condition
         *@param{Event}ev
         */
        _onFieldSelect(condition,ev){
            Object.assign(condition,{
                field:ev.target.selectedIndex,
                operator:0,
            });
            this._setDefaultValue(condition);
        }

        /**
         *@private
         *@param{Object}condition
         *@param{Event}ev
         */
        _onOperatorSelect(condition,ev){
            condition.operator=ev.target.selectedIndex;
            this._setDefaultValue(condition);
        }

        /**
         *@private
         *@param{Object}condition
         */
        _onRemoveCondition(conditionIndex){
            this.state.conditions.splice(conditionIndex,1);
        }

        /**
         *@private
         *@param{Object}condition
         *@param{Event}ev
         */
        _onValueInput(condition,ev){
            if(!ev.target.value){
                returnthis._setDefaultValue(condition);
            }
            let{type}=this.fields[condition.field];
            if(type==="id"){
                type="integer";
            }
            if(FIELD_TYPES[type]==="number"){
                try{
                    //Writelogicalvalueintothe'value'property
                    condition.value=field_utils.parse[type](ev.target.value);
                    //Writedisplayedvalueintheinputand'displayedValue'property
                    condition.displayedValue=ev.target.value;
                }catch(err){
                    //Parsingerror:revertstopreviousvalue
                    ev.target.value=condition.displayedValue;
                }
            }else{
                condition.value=condition.displayedValue=ev.target.value;
            }
        }
    }

    CustomFilterItem.components={DatePicker,DateTimePicker};
    CustomFilterItem.props={
        fields:Object,
    };
    CustomFilterItem.template='web.CustomFilterItem';

    returnpatchMixin(CustomFilterItem);
});
