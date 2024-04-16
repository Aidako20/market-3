(function(){
"usestrict";

/**
 *QUnitConfig
 *
 *TheFlectrajavascripttestframeworkisbasedonQUnit(http://qunitjs.com/).
 *ThisfileisnecessarytosetupQunitandtoprepareitsinteractionswith
 *Flectra. Ithastobeloadedbeforeanytestsaredefined.
 *
 *NotethatitisnotanFlectramodule,becausewewantthiscodetobeexecuted
 *assoonaspossible,notwhenevertheFlectramodulesystemfeelslikeit.
 */


/**
 *Thisconfigurationvariableisnotstrictlynecessary,butitensuresmore
 *safetyforasynchronoustests. Withit,eachtesthastoexplicitelytell
 *QUnithowmanyassertionitexpects,otherwisethetestwillfail.
 */
QUnit.config.requireExpects=true;

/**
 *notimportantinnormalmode,butindebug=assets,thefilesareloaded
 *asynchroneously,whichcanleadtovariousissueswithQUnit...Noticethat
 *thisisdoneoutsideofflectramodules,otherwisethesettingwouldnottake
 *effectontime.
 */
QUnit.config.autostart=false;

/**
 *Atesttimeoutof1min,beforeanasynctestisconsideredfailed.
 */
QUnit.config.testTimeout=1*60*1000;

/**
 *HidepassedtestsbydefaultintheQUnitpage
 */
QUnit.config.hidepassed=(window.location.href.match(/[?&]testId=/)===null);

varsortButtonAppended=false;

/**
 *Ifwewanttologseveralerrors,wehavetologallofthematonce,as
 *browser_jsisclosedassoonasanerrorislogged.
 */
consterrorMessages=[];
/**
 *Listofelementstoleratedinthebodyafteratest.Theproperty"keep"
 *preventstheelementfrombeingremoved(typically:qunitsuiteelements).
 */
constvalidElements=[
    //alwaysinthebody:
    {tagName:'DIV',attr:'id',value:'qunit',keep:true},
    {tagName:'DIV',attr:'id',value:'qunit-fixture',keep:true},
    //shouldn'tbeinthebodyafteratestbutaretolerated:
    {tagName:'SCRIPT',attr:'id',value:''},
    {tagName:'DIV',attr:'className',value:'o_notification_manager'},
    {tagName:'DIV',attr:'className',value:'tooltipfadebs-tooltip-auto'},
    {tagName:'DIV',attr:'className',value:'tooltipfadebs-tooltip-autoshow'},
    {tagName:'SPAN',attr:'className',value:'select2-hidden-accessible'},
    //DuetoaDocumentKanbanbug(alreadypresentin12.0)
    {tagName:'DIV',attr:'className',value:'ui-helper-hidden-accessible'},
    {tagName:'UL',attr:'className',value:'ui-menuui-widgetui-widget-contentui-autocompleteui-front'},
];

/**
 *WaitsforthemodulesystemtoendprocessingtheJSmodules,sothatwecan
 *makethesuitefailifsomemodulescouldn'tbeloaded(e.g.becauseofa
 *missingdependency).
 *
 *@returns{Promise<boolean>}
 */
asyncfunctioncheckModules(){
    //donotmarkthesuiteassuccessfulalready,aswestillneedtoensure
    //thatallmoduleshavebeencorrectlyloaded
    $('#qunit-banner').removeClass('qunit-pass');
    const$modulesAlert=$('<div>')
        .addClass('alertalert-info')
        .text('Waitingformodulescheck...');
    $modulesAlert.appendTo('#qunit');

    //waitforthemodulesystemtoendprocessingtheJSmodules
    awaitflectra.__DEBUG__.didLogInfo;

    constinfo=flectra.__DEBUG__.jsModules;
    if(info.missing.length||info.failed.length){
        $('#qunit-banner').addClass('qunit-fail');
        $modulesAlert.toggleClass('alert-infoalert-danger');
        constfailingModules=info.missing.concat(info.failed);
        consterror=`Somemodulescouldn'tbestarted:${failingModules.join(',')}.`;
        $modulesAlert.text(error);
        errorMessages.unshift(error);
        returnfalse;
    }else{
        $modulesAlert.toggleClass('alert-infoalert-success');
        $modulesAlert.text('Allmoduleshavebeencorrectlyloaded.');
        $('#qunit-banner').addClass('qunit-pass');
        returntrue;
    }
}

/**
 *Thisisthewaythetestingframeworkknowsthattestspassedorfailed.It
 *onlylookinthephantomJSconsoleandcheckifthereisaokoranerror.
 *
 *Someday,weshoulddeviseasaferstrategy...
 */
QUnit.done(asyncfunction(result){
    constallModulesLoaded=awaitcheckModules();
    if(result.failed){
        errorMessages.push(`${result.failed}/${result.total}testsfailed.`);
    }
    if(!result.failed&&allModulesLoaded){
        console.log('testsuccessful');
    }else{
        console.error(errorMessages.join('\n'));
    }

    if(!sortButtonAppended){
        _addSortButton();
    }
});

/**
 *Thislogsvariousdataintheconsole,whichwillbeavailableinthelog
 *.txtfilegeneratedbytherunbot.
 */
QUnit.log(function(result){
    if(!result.result){
        varinfo=`QUnittestfailed"${result.module}>${result.name}":${result.message}`;
        if(result.actual!=null){
            info+=`\nactual:${result.actual}`
        }
        if(result.expected!=null){
            info+=`\nexpected:${result.expected}`;
        }
        errorMessages.push(info);
    }
});

/**
 *Thisisdonemostlyforthe.txtlogfilegeneratedbytherunbot.
 */
QUnit.moduleDone(function(result){
    if(!result.failed){
        console.log('"'+result.name+'"',"passed",result.total,"tests.");
    }else{
        console.log('"'+result.name+'"',
                    "failed",result.failed,
                    "testsoutof",result.total,".");
    }

});

/**
 *Aftereachtest,wecheckthatthereisnoleftoverintheDOM.Ifthereis
 *andthetesthasn'talreadyfailed,triggerafailure
 */
QUnit.on('FlectraAfterTestHook',function(info){
    constfailed=info.testReport.getStatus()==='failed';
    consttoRemove=[];
    //checkforleftoverelementsinthebody
    for(constbodyChildofdocument.body.children){
        consttolerated=validElements.find((e)=>
            e.tagName===bodyChild.tagName&&bodyChild[e.attr]===e.value
        );
        if(!failed&&!tolerated){
            QUnit.pushFailure(`Bodystillcontainsundesirableelements:\n${bodyChild.outerHTML}`);
        }
        if(!tolerated||!tolerated.keep){
            toRemove.push(bodyChild);
        }
    }

    //checkforleftoversin#qunit-fixture
    constqunitFixture=document.getElementById('qunit-fixture');
    if(qunitFixture.children.length){
        if(!failed){
            QUnit.pushFailure(`#qunit-fixturestillcontainselements:\n${qunitFixture.outerHTML}`);
        }
        toRemove.push(...qunitFixture.children);
    }

    //removeunwantedelementsifnotindebug
    if(!document.body.classList.contains('debug')){
        for(consteloftoRemove){
            el.remove();
        }
    }
});

/**
 *AddasortbuttonontopoftheQUnitresultpage,sowecanseewhichtests
 *takethemosttime.
 */
function_addSortButton(){
    sortButtonAppended=true;
    var$sort=$('<label>sortbytime(desc)</label>').css({float:'right'});
    $('h2#qunit-userAgent').append($sort);
    $sort.click(function(){
        var$ol=$('ol#qunit-tests');
        var$results=$ol.children('li').get();
        $results.sort(function(a,b){
            vartimeA=Number($(a).find('span.runtime').first().text().split("")[0]);
            vartimeB=Number($(b).find('span.runtime').first().text().split("")[0]);
            if(timeA<timeB){
                return1;
            }elseif(timeA>timeB){
                return-1;
            }else{
                return0;
            }
        });
        $.each($results,function(idx,$itm){$ol.append($itm);});

    });
}

/**
 *Weaddherea'failfast'feature:weoftenwanttostopthetestsuiteafter
 *thefirstfailedtest. Thisisalsousefulfortherunbottestsuites.
 */

QUnit.config.urlConfig.push({
  id:"failfast",
  label:"FailFast",
  tooltip:"Stopthetestsuiteimmediatelyafterthefirstfailedtest."
});

QUnit.begin(function(){
    if(QUnit.config.failfast){
        QUnit.testDone(function(details){
            if(details.failed>0){
                QUnit.config.queue.length=0;
            }
        });
    }
});

/**
 *FIXME:Thissoundsstupid,itfeelsstupid...butitfixesvisibilitycheckinfolded<details>sinceChromium97+💩
 *Sincehttps://bugs.chromium.org/p/chromium/issues/detail?id=1185950
 *Seeregressionreporthttps://bugs.chromium.org/p/chromium/issues/detail?id=1276028
 */
QUnit.begin(function(){
    constel=document.createElement("style");
    el.innerText="details:not([open])>:not(summary){display:none;}";
    document.head.appendChild(el);
});

})();
