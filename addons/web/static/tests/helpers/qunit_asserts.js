flectra.define('web.qunit_asserts',function(require){
    "usestrict";

    /**
     *Inthisfile,weextendQUnitbyaddingsomespecializedassertions.Thegoal
     *ofthesenewassertionsistwofold:
     *-easeofuse:theyshouldallowustosimplifysomecommoncomplexassertions
     *-safer:theseassertionswillfailwhensomepreconditionsarenotmet.
     *
     *Forexample,theassert.isVisibleassertionwillalsocheckthatthetarget
     *matchesexactlyoneelement.
     */

    constWidget=require('web.Widget');

    /**@todousetestUtilsDom.getNodetoextracttheelementfromthe'w'argument*/

    //-------------------------------------------------------------------------
    //Privatefunctions
    //-------------------------------------------------------------------------

    /**
     *Helperfunction,tocheckifagivenelement
     *-isunique(ifitisajquerynodeset)
     *-has(orhasnot)acssclass
     *
     *@private
     *@param{Widget|jQuery|HTMLElement|owl.Component}w
     *@param{string}className
     *@param{boolean}shouldHaveClass
     *@param{string}[msg]
     */
    function_checkClass(w,className,shouldHaveClass,msg){
        if(winstanceofjQuery&&w.length!==1){
            constassertion=shouldHaveClass?'hasClass':'doesNotHaveClass';
            QUnit.assert.ok(false,`Assertion'${assertion}${className}'targets${w.length}elementsinsteadof1`);
        }

        constel=winstanceofWidget||winstanceofowl.Component?w.el:
            winstanceofjQuery?w[0]:w;

        msg=msg||`targetshould${shouldHaveClass?'have':'nothave'}class${className}`;
        constisFalse=className.split("").some(cls=>{
            consthasClass=el.classList.contains(cls);
            returnshouldHaveClass?!hasClass:hasClass;
        });
        QUnit.assert.ok(!isFalse,msg);
    }

    /**
     *Helperfunction,tocheckifagivenelement
     *-isunique(ifitisajquerynodeset)
     *-is(ornot)visible
     *
     *@private
     *@param{Widget|jQuery|HTMLElement|owl.Component}w
     *@param{boolean}shouldBeVisible
     *@param{string}[msg]
     */
    function_checkVisible(w,shouldBeVisible,msg){
        if(winstanceofjQuery&&w.length!==1){
            constassertion=shouldBeVisible?'isVisible':'isNotVisible';
            QUnit.assert.ok(false,`Assertion'${assertion}'targets${w.length}elementsinsteadof1`);
        }

        constel=winstanceofWidget||winstanceofowl.Component?w.el:
            winstanceofjQuery?w[0]:w;

        msg=msg||`targetshould${shouldBeVisible?'':'not'}bevisible`;
        letisVisible=el&&
            el.offsetWidth&&
            el.offsetHeight;
        if(isVisible){
            //Thiscomputationisalittlemoreheavyandweonlywanttoperformit
            //iftheaboveassertionhasfailed.
            constrect=el.getBoundingClientRect();
            isVisible=rect.width+rect.height;
        }
        constcondition=shouldBeVisible?isVisible:!isVisible;
        QUnit.assert.ok(condition,msg);
    }

    //-------------------------------------------------------------------------
    //Publicfunctions
    //-------------------------------------------------------------------------

    /**
     *Checksthatthetargetelement(describedbywidget/jqueryorhtmlelement)
     *containsexactlynmatchesfortheselector.
     *
     *Example:assert.containsN(document.body,'.modal',0)
     *
     *@param{Widget|jQuery|HTMLElement|owl.Component}w
     *@param{string}selector
     *@param{number}n
     *@param{string}[msg]
     */
    functioncontainsN(w,selector,n,msg){
        if(typeofn!=='number'){
            thrownewError("containsNassertshouldbecalledwithanumberasthirdargument");
        }
        letmatches=[];
        if(winstanceofowl.Component){
            if(!w.el){
                thrownewError(`containsNassertwithselector'${selector}'calledonanunmountedcomponent`);
            }
            matches=w.el.querySelectorAll(selector);
        }else{
            const$el=winstanceofWidget?w.$el:
                winstanceofHTMLElement?$(w):
                    w; //jqueryelement
            matches=$el.find(selector);
        }
        if(!msg){
            msg=`Selector'${selector}'shouldhaveexactly${n}matches(insidethetarget)`;
        }
        QUnit.assert.strictEqual(matches.length,n,msg);
    }

    /**
     *Checksthatthetargetelement(describedbywidget/jqueryorhtmlelement)
     *containsexactly0matchfortheselector.
     *
     *@param{Widget|jQuery|HTMLElement|owl.Component}w
     *@param{string}selector
     *@param{string}[msg]
     */
    functioncontainsNone(w,selector,msg){
        containsN(w,selector,0,msg);
    }

    /**
     *Checksthatthetargetelement(describedbywidget/jqueryorhtmlelement)
     *containsexactly1matchfortheselector.
     *
     *@param{Widget|jQuery|HTMLElement|owl.Component}w
     *@param{string}selector
     *@param{string}[msg]
     */
    functioncontainsOnce(w,selector,msg){
        containsN(w,selector,1,msg);
    }

    /**
     *Checksthatthetargetelement(describedbywidget/jqueryorhtmlelement)
     *-exists
     *-isunique
     *-hasthegivenclass(specifiedbyclassName)
     *
     *NotethatitusesthehasClassjQuerymethod,soitcanbeusedtocheckthe
     *presenceofmorethanoneclass('some-classother-class'),butitisa
     *littlebrittle,becauseitdependsontheorderoftheseclasses:
     *
     * div.a.b.c:hasclass'abc',butdoesnothaveclass'acb'
     *
     *@param{Widget|jQuery|HTMLElement|owl.Component}w
     *@param{string}className
     *@param{string}[msg]
     */
    functionhasClass(w,className,msg){
        _checkClass(w,className,true,msg);
    }

    /**
     *Checksthatthetargetelement(describedbywidget/jqueryorhtmlelement)
     *-exists
     *-isunique
     *-doesnothavethegivenclass(specifiedbyclassName)
     *
     *@param{Widget|jQuery|HTMLElement|owl.Component}w
     *@param{string}className
     *@param{string}[msg]
     */
    functiondoesNotHaveClass(w,className,msg){
        _checkClass(w,className,false,msg);
    }

    /**
     *Checksthatthetargetelement(describedbywidget/jqueryorhtmlelement)
     *-exists
     *-isunique
     *-hasthegivenattributewiththepropervalue
     *
     *@param{Widget|jQuery|HTMLElement|owl.Component}w
     *@param{string}attr
     *@param{string}value
     *@param{string}[msg]
     */
    functionhasAttrValue(w,attr,value,msg){
        const$el=winstanceofWidget?w.$el:
            winstanceofHTMLElement?$(w):
                w; //jqueryelement

        if($el.length!==1){
            constdescr=`hasAttrValue(${attr}:${value})`;
            QUnit.assert.ok(false,
                `Assertion'${descr}'targets${$el.length}elementsinsteadof1`
            );
        }else{
            msg=msg||`attribute'${attr}'oftargetshouldbe'${value}'`;
            QUnit.assert.strictEqual($el.attr(attr),value,msg);
        }
    }

    /**
     *Checksthatthetargetelement(describedbywidget/jqueryorhtmlelement)
     *-exists
     *-isvisible(asfarasjQuerycantell:notindisplaynone,...)
     *
     *@param{Widget|jQuery|HTMLElement|owl.Component}w
     *@param{string}[msg]
     */
    functionisVisible(w,msg){
        _checkVisible(w,true,msg);
    }

    /**
     *Checksthatthetargetelement(describedbywidget/jqueryorhtmlelement)
     *-exists
     *-isnotvisible(asfarasjQuerycantell:displaynone,...)
     *
     *@param{Widget|jQuery|HTMLElement|owl.Component}w
     *@param{string}[msg]
     */
    functionisNotVisible(w,msg){
        _checkVisible(w,false,msg);
    }

    //-------------------------------------------------------------------------
    //ExposedAPI
    //-------------------------------------------------------------------------

    QUnit.assert.containsN=containsN;
    QUnit.assert.containsNone=containsNone;
    QUnit.assert.containsOnce=containsOnce;

    QUnit.assert.hasClass=hasClass;
    QUnit.assert.doesNotHaveClass=doesNotHaveClass;

    QUnit.assert.hasAttrValue=hasAttrValue;

    QUnit.assert.isVisible=isVisible;
    QUnit.assert.isNotVisible=isNotVisible;
});
