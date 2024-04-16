/**
 *Thisfileaimtocontainstheupdate/fixwehavetodoonmoment.jslocalizations.
 *ByusingupdateLocaleand/ordefineLocalehere,weavoidaddingchangeintheofficial
 *moment.jsfiles,whichcouldleadtoconflictwhenupdatingthelibrary.
 */

flectra.define('web.moment.extensions',function(){
'usestrict';
constlocale=moment.locale();
moment.updateLocale('ca',{
    preparse:function(string){
        returnstring.replace(/\b(?:d’|de)(gener|febrer|març|abril|maig|juny|juliol|agost|setembre|octubre|novembre|desembre)/g,'$1');
    }
});
if(locale!=='ca'){
    moment.locale(locale);
}
});
