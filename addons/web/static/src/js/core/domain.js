flectra.define("web.Domain",function(require){
"usestrict";

varcollections=require("web.collections");
varpyUtils=require("web.py_utils");
varpy=window.py;//lookpy.js

constTRUE_LEAF=[1,'=',1];
constFALSE_LEAF=[0,'=',1];
constTRUE_DOMAIN=[TRUE_LEAF];
constFALSE_DOMAIN=[FALSE_LEAF];

functioncompare(a,b){
    returnJSON.stringify(a)===JSON.stringify(b);
}

/**
 *TheDomainClassallowstoworkwithadomainasatreeandprovidestools
 *tomanipulatearrayandstringrepresentationsofdomains.
 */
varDomain=collections.Tree.extend({
    /**
     *@constructor
     *@param{string|Array|boolean|undefined}domain
     *       Thegivendomaincanbe:
     *           *astringrepresentationofthePythonprefix-array
     *             representationofthedomain.
     *           *aJSprefix-arrayrepresentationofthedomain.
     *           *abooleanwherethe"true"domainmatchallrecordsandthe
     *             "false"domaindoesnotmatchanyrecords.
     *           *undefined,consideredasthefalseboolean.
     *           *anumber,consideredastrueexcept0consideredasfalse.
     *@param{Object}[evalContext]-incasethegivendomainisastring,an
     *                              evaluationcontextmightbeneeded
     */
    init:function(domain,evalContext){
        this._super.apply(this,arguments);
        if(_.isArray(domain)||_.isString(domain)){
            this._parse(this.normalizeArray(_.clone(this.stringToArray(domain,evalContext))));
        }else{
            this._data=!!domain;
        }
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Evaluatesthedomainwithasetofvalues.
     *
     *@param{Object}values-amapping{fieldName->fieldValue}(note:all
     *                       thefieldsusedinthedomainshouldbegivena
     *                       valueotherwisethecomputationwillbreak)
     *@returns{boolean}
     */
    compute:function(values){
        if(this._data===true||this._data===false){
            //Thedomainisaalways-trueoraalways-falsedomain
            returnthis._data;
        }elseif(_.isArray(this._data)){
            //Thedomainisa[name,operator,value]entity
            //Firstcheckifwehavethefieldvalueinthefieldvaluesset
            //andifthefirstpartofthedomaincontains'parent.field'
            //getthevaluefromtheparentrecord.
            varisParentField=false;
            varfieldName=this._data[0];
            //Wesplitthedomainfirstpartandcheckifit'samatch
            //forthesyntax'parent.field'.

            letfieldValue;
            if(compare(this._data,FALSE_LEAF)||compare(this._data,TRUE_LEAF)){
                fieldValue=this._data[0];
            }else{
                varparentField=this._data[0].split('.');
                if('parent'invalues&&parentField.length===2){
                    fieldName=parentField[1];
                    isParentField=parentField[0]==='parent'&&
                        fieldNameinvalues.parent;
                }
                if(!(this._data[0]invalues)&&!(isParentField)){
                    thrownewError(_.str.sprintf(
                        "Unknownfield%sindomain",
                        this._data[0]
                    ));
                }
                fieldValue=isParentField?values.parent[fieldName]:values[fieldName];
            }

            switch(this._data[1]){
                case"=":
                case"==":
                    return_.isEqual(fieldValue,this._data[2]);
                case"!=":
                case"<>":
                    return!_.isEqual(fieldValue,this._data[2]);
                case"<":
                    return(fieldValue<this._data[2]);
                case">":
                    return(fieldValue>this._data[2]);
                case"<=":
                    return(fieldValue<=this._data[2]);
                case">=":
                    return(fieldValue>=this._data[2]);
                case"in":
                    return_.intersection(
                        _.isArray(this._data[2])?this._data[2]:[this._data[2]],
                        _.isArray(fieldValue)?fieldValue:[fieldValue],
                    ).length!==0;
                case"notin":
                    return_.intersection(
                        _.isArray(this._data[2])?this._data[2]:[this._data[2]],
                        _.isArray(fieldValue)?fieldValue:[fieldValue],
                    ).length===0;
                case"like":
                    if(fieldValue===false){
                        returnfalse;
                    }
                    return(fieldValue.indexOf(this._data[2])>=0);
                case"=like":
                    if(fieldValue===false){
                        returnfalse;
                    }
                    returnnewRegExp(this._data[2].replace(/%/g,'.*')).test(fieldValue);
                case"ilike":
                    if(fieldValue===false){
                        returnfalse;
                    }
                    return(fieldValue.toLowerCase().indexOf(this._data[2].toLowerCase())>=0);
                case"=ilike":
                    if(fieldValue===false){
                        returnfalse;
                    }
                    returnnewRegExp(this._data[2].replace(/%/g,'.*'),'i').test(fieldValue);
                default:
                    thrownewError(_.str.sprintf(
                        "Domain%susesanunsupportedoperator",
                        this._data
                    ));
            }
        }else{//Thedomainisasetof[name,operator,value]entitie(s)
            switch(this._data){
                case"&":
                    return_.every(this._children,function(child){
                        returnchild.compute(values);
                    });
                case"|":
                    return_.some(this._children,function(child){
                        returnchild.compute(values);
                    });
                case"!":
                    return!this._children[0].compute(values);
            }
        }
    },
    /**
     *ReturntheJSprefix-arrayrepresentationofthisdomain.Notethatall
     *domainsthatusethe"false"domaincannotberepresentedassuch.
     *
     *@returns{Array}JSprefix-arrayrepresentationofthisdomain
     */
    toArray:function(){
        if(this._data===false){
            thrownewError("'false'domaincannotbeconvertedtoarray");
        }elseif(this._data===true){
            return[];
        }else{
            vararr=[this._data];
            returnarr.concat.apply(arr,_.map(this._children,function(child){
                returnchild.toArray();
            }));
        }
    },
    /**
     *@returns{string}representationofthePythonprefix-array
     *                  representationofthedomain
     */
    toString:function(){
        returnDomain.prototype.arrayToString(this.toArray());
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Initializesthetreerepresentationofthedomainaccordingtoitsgiven
     *JSprefix-arrayrepresentation.Note:thegivenarrayisconsidered
     *alreadynormalized.
     *
     *@private
     *@param{Array}domain-normalizedJSprefix-arrayrepresentationof
     *                      thedomain
     */
    _parse:function(domain){
        this._data=(domain.length===0?true:domain[0]);
        if(domain.length<=1)return;

        varexpected=1;
        for(vari=1;i<domain.length;i++){
            if(domain[i]==="&"||domain[i]==="|"){
                expected++;
            }elseif(domain[i]!=="!"){
                expected--;
            }

            if(!expected){
                i++;
                this._addSubdomain(domain.slice(1,i));
                this._addSubdomain(domain.slice(i));
                break;
            }
        }
    },

    /**
     *Addsadomainasachild(e.g.ifthecurrentdomainis["|",A,B],
     *usingthismethodwitha["&",C,D]domainwillresultina
     *["|","|",A,B,"&",C,D]).
     *Note:theinternaltreerepresentationisautomaticallysimplified.
     *
     *@param{Array}domain-normalizedJSprefix-arrayrepresentationofa
     *                      domaintoadd
     */
    _addSubdomain:function(domain){
        if(!domain.length)return;
        varsubdomain=newDomain(domain);

        if(!subdomain._children.length||subdomain._data!==this._data){
            this._children.push(subdomain);
        }else{
            varself=this;
            _.each(subdomain._children,function(childDomain){
                self._children.push(childDomain);
            });
        }
    },

    //--------------------------------------------------------------------------
    //Static
    //--------------------------------------------------------------------------

    /**
     *ConvertsJSprefix-arrayrepresentationofadomaintoastring
     *representationofthePythonprefix-arrayrepresentationofthisdomain.
     *
     *@static
     *@param{Array|string|undefined}domain
     *@returns{string}
     */
    arrayToString:function(domain){
        if(_.isString(domain))returndomain;

        functionjsToPy(p){
            switch(p){
                casenull:return"None";
                casetrue:return"True";
                casefalse:return"False";
                default:
                    if(Array.isArray(p)){
                        return`[${p.map(jsToPy)}]`;
                    }
                    returnJSON.stringify(p);
            }
        }

        return`[${(domain||[]).map(jsToPy)}]`;
    },
    /**
     *ConvertsastringrepresentationofthePythonprefix-array
     *representationofadomaintoaJSprefix-arrayrepresentationofthis
     *domain.
     *
     *@static
     *@param{string|Array}domain
     *@param{Object}[evalContext]
     *@returns{Array}
     */
    stringToArray:function(domain,evalContext){
        if(!_.isString(domain))return_.clone(domain);
        returnpyUtils.eval("domain",domain?domain.replace(/%%/g,'%'):"[]",evalContext);
    },
    /**
     *Makesimplicit"&"operatorsexplicitinthegivenJSprefix-array
     *representationofdomain(e.g[A,B]->["&",A,B])
     *
     *@static
     *@param{Array}domain-theJSprefix-arrayrepresentationofthedomain
     *                      tonormalize(!willbenormalizedin-place)
     *@returns{Array}thenormalizedJSprefix-arrayrepresentationofthe
     *                 givendomain
     *@throws{Error}ifthedomainisinvalidandcan'tbenormalised
     */
    normalizeArray:function(domain){
        if(domain.length===0){returndomain;}
        varexpected=1;
        _.each(domain,function(item){
            if(item==="&"||item==="|"){
                expected++;
            }elseif(item!=="!"){
                expected--;
            }
        });
        if(expected<0){
            domain.unshift.apply(domain,_.times(Math.abs(expected),_.constant("&")));
        }elseif(expected>0){
            thrownewError(_.str.sprintf(
                "invaliddomain%s(missing%dsegment(s))",
                JSON.stringify(domain),expected
            ));
        }
        returndomain;
    },
    /**
     *ConvertsJSprefix-arrayrepresentationofadomaintoapythoncondition
     *
     *@static
     *@param{Array}domain
     *@returns{string}
     */
    domainToCondition:function(domain){
        if(!domain.length){
            return'True';
        }
        varself=this;
        functionconsume(stack){
            varlen=stack.length;
            if(len<=1){
                returnstack;
            }elseif(stack[len-1]==='|'||stack[len-1]==='&'||stack[len-2]==='|'||stack[len-2]==='&'){
                returnstack;
            }elseif(len==2){
                stack.splice(-2,2,stack[len-2]+'and'+stack[len-1]);
            }elseif(stack[len-3]=='|'){
                if(len===3){
                    stack.splice(-3,3,stack[len-2]+'or'+stack[len-1]);
                }else{
                    stack.splice(-3,3,'('+stack[len-2]+'or'+stack[len-1]+')');
                }
            }else{
                stack.splice(-3,3,stack[len-2]+'and'+stack[len-1]);
            }
            consume(stack);
        }

        varstack=[];
        _.each(domain,function(dom){
            if(dom==='|'||dom==='&'){
                stack.push(dom);
            }else{
                varoperator=dom[1]==='='?'==':dom[1];
                if(!operator){
                    thrownewError('Wrongoperatorforthisdomain');
                }
                if(operator==='!='&&dom[2]===false){//thefieldisset
                    stack.push(dom[0]);
                }elseif(dom[2]===null||dom[2]===true||dom[2]===false){
                    stack.push(dom[0]+''+(operator==='!='?'isnot':'is')+(dom[2]===null?'None':(dom[2]?'True':'False')));
                }else{
                    stack.push(dom[0]+''+operator+''+JSON.stringify(dom[2]));
                }
                consume(stack);
            }
        });

        if(stack.length!==1){
            thrownewError('Wrongdomain');
        }

        returnstack[0];
    },
    /**
     *ConvertspythonconditiontoaJSprefix-arrayrepresentationofadomain
     *
     *@static
     *@param{string}condition
     *@returns{Array}
     */
    conditionToDomain:function(condition){
        if(!condition||condition.match(/^\s*(True)?\s*$/)){
            return[];
        }

        varast=py.parse(py.tokenize(condition));


        functionastToStackValue(node){
            switch(node.id){
                case'(name)':returnnode.value;
                case'.':returnastToStackValue(node.first)+'.'+astToStackValue(node.second);
                case'(string)':returnnode.value;
                case'(number)':returnnode.value;
                case'(constant)':returnnode.value==='None'?null:node.value==='True'?true:false;
                case'[':return_.map(node.first,function(node){returnastToStackValue(node);});
            }
        }
        functionastToStack(node){
            switch(node.id){
                case'(name)':return[[astToStackValue(node),'!=',false]];
                case'.':return[[astToStackValue(node.first)+'.'+astToStackValue(node.second),'!=',false]];
                case'not':return[[astToStackValue(node.first),'=',false]];

                case'or':return['|'].concat(astToStack(node.first)).concat(astToStack(node.second));
                case'and':return['&'].concat(astToStack(node.first)).concat(astToStack(node.second));
                case'(comparator)':
                    if(node.operators.length!==1){
                        thrownewError('Wrongconditiontoconvertindomain');
                    }
                    varright=astToStackValue(node.expressions[0]);
                    varleft=astToStackValue(node.expressions[1]);
                    varoperator=node.operators[0];
                    switch(operator){
                        case'is':operator='=';break;
                        case'isnot':operator='!=';break;
                        case'==':operator='=';break;
                    }
                    return[[right,operator,left]];
                default:
                    throw"Conditioncannotbetransformedintodomain";
            }
        }

        returnastToStack(ast);
    },
});

Domain.TRUE_LEAF=TRUE_LEAF;
Domain.FALSE_LEAF=FALSE_LEAF;
Domain.TRUE_DOMAIN=TRUE_DOMAIN;
Domain.FALSE_DOMAIN=FALSE_DOMAIN;

returnDomain;
});
