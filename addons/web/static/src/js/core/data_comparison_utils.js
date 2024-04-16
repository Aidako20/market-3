flectra.define('web.dataComparisonUtils',function(require){
"usestrict";

varfieldUtils=require('web.field_utils');
varClass=require('web.Class');

varDateClasses=Class.extend({
    /**
     *ThissmallclassoffersalightAPItomanageequivalenceclassesof
     *dates.TwodatesindifferentdateSetsaredeclaredequivalentwhen
     *theirindexesareequal.
     *
     *@param {Array[]}dateSets,alistoflistofdates
     */
    init:function(dateSets){
        //AtleastonedateSetmustbenonempty.
        //ThecompletionofthefirstinhabiteddateSetwillserveasareferenceset.
        //Thereferencesetelementswillbethedefaultrepresentativesfortheclasses.
        this.dateSets=dateSets;
        this.referenceIndex=null;
        for(vari=0;i<dateSets.length;i++){
            vardateSet=dateSets[i];
            if(dateSet.length&&this.referenceIndex===null){
                this.referenceIndex=i;
            }
        }
    },

    //----------------------------------------------------------------------
    //Public
    //----------------------------------------------------------------------

    /**
     *ReturnstheindexofadateinagivendatesetIndex.Thiscanbeconsidered
     *asthedateclassitself.
     *
     *@param {number}datesetIndex
     *@param {string}date
     *@return{number}
     */
    dateClass:function(datesetIndex,date){
        returnthis.dateSets[datesetIndex].indexOf(date);
    },
    /**
     *returnsthedatesoccuringinagivenclass
     *
     *@param {number}dateClass
     *@return{string[]}
     */
    dateClassMembers:function(dateClass){
        return_.uniq(_.compact(this.dateSets.map(function(dateSet){
            returndateSet[dateClass];
        })));
    },
    /**
     *returntherepresentativeofadateclassfromadatesetspecifiedbyan
     *index.
     *
     *@param {number}dateClass
     *@param {number}[index]
     *@return{string}
     */
    representative:function(dateClass,index){
        index=index===undefined?this.referenceIndex:index;
        returnthis.dateSets[index][dateClass];
    },
});
/**
 *@param{Number}value
 *@param{Number}comparisonValue
 *@returns{Number}
 */
functioncomputeVariation(value,comparisonValue){
    if(isNaN(value)||isNaN(comparisonValue)){
        returnNaN;
    }
    if(comparisonValue===0){
        if(value===0){
            return0;
        }elseif(value>0){
            return1;
        }else{
            return-1;
        }
    }
    return(value-comparisonValue)/Math.abs(comparisonValue);
}
/**
 *@param{Number}variation
 *@param{Object}field
 *@param{Object}options
 *@returns{Object}
 */
functionrenderVariation(variation,field,options){
    varclassName='o_variation';
    varvalue;
    if(!isNaN(variation)){
        if(variation>0){
            className+='o_positive';
        }elseif(variation<0){
            className+='o_negative';
        }else{
            className+='o_null';
        }
        value=fieldUtils.format.percentage(variation,field,options);
    }else{
        value='-';
    }
    return$('<div>',{class:className,html:value});
}
/**
 *@param{JQuery}$node
 *@param{Number}value
 *@param{Number}comparisonValue
 *@param{Number}variation
 *@param{function}formatter
 *@param{Object}field
 *@param{Object}options
 *@returns{Object}
 */
functionrenderComparison($node,value,comparisonValue,variation,formatter,field,options){
    var$variation=renderVariation(variation,field,options);
    $node.append($variation);
    if(!isNaN(variation)){
        $node.append(
            $('<div>',{class:'o_comparison'})
            .html(formatter(value,field,options)+'<span>vs</span>'+formatter(comparisonValue,field,options))
        );
    }
}

return{
    computeVariation:computeVariation,
    DateClasses:DateClasses,
    renderComparison:renderComparison,
    renderVariation:renderVariation,
};

});
